import re
import asyncio
from typing import Dict, Any

from app.services.dns_checker import get_mx_records
from app.services.smtp_checker import check_smtp
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)

# Lists can be loaded from DB/Redis or files in a real app
ROLE_BASED_PREFIXES = {"admin", "support", "info", "sales", "contact", "billing", "hello", "webmaster", "marketing", "dev", "hr"}
DISPOSABLE_DOMAINS = {"mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com", "yopmail.com", "maildrop.cc"}
FREE_EMAIL_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com", "live.com", "msn.com"}

async def verify_email(email: str, check_smtp_enabled: bool = True) -> Dict[str, Any]:
    logger.info(f"Starting verification for: {email}")
    email = email.lower().strip()
    
    result = {
        "email": email,
        "status": "invalid",
        "reason": "Unknown",
        "smtp_code": 0,
        "smtp_message": "",
        "risk": "high",
        "action": "Remove",
        "retry": False,
        "is_disposable": False,
        "is_catch_all": False,
        "is_role_based": False,
        "is_free_email": False,
        "smtp_check": False,
        "mx_found": False,
        "score": 0
    }
    
    # 1. Format Check
    if not EMAIL_REGEX.match(email):
        result["reason"] = "Invalid Format"
        return result
    
    local_part, domain = email.split('@')
    
    # 2. Role-based Check
    if local_part in ROLE_BASED_PREFIXES:
        result["is_role_based"] = True
        
    # 3. Disposable Domain Check
    if domain in DISPOSABLE_DOMAINS:
        result["is_disposable"] = True
        
    # 4. Free Email Check
    if domain in FREE_EMAIL_DOMAINS:
        result["is_free_email"] = True
        
    # 5. MX Records Check
    mx_records = await get_mx_records(domain)
    if mx_records:
        result["mx_found"] = True
    else:
        result["reason"] = "No MX Records"
        result["risk"] = "high"
        return result
        
    # 6. SMTP & Catch-All Check
    if check_smtp_enabled:
        # Add random delay to prevent blocking
        await asyncio.sleep(0.5) 
        
        smtp_data = await check_smtp(email, mx_records, proxy_url=settings.SMTP_PROXY_URL)
        result["smtp_check"] = smtp_data.get("is_deliverable", False)
        result["is_catch_all"] = smtp_data.get("is_catch_all", False)
        result["smtp_code"] = smtp_data.get("smtp_code", 0)
        result["smtp_message"] = smtp_data.get("smtp_message", "")
    else:
        # If SMTP check is disabled, we set these cautiously
        result["smtp_check"] = False
        result["is_catch_all"] = False
        result["reason"] = "SMTP Check Disabled"

    # 7. Scoring system (Additive)
    score = 0
    breakdown = []
    
    if result["smtp_check"]:
        score += 40
        breakdown.append({"label": "SMTP Success", "points": "+40"})
    else:
        breakdown.append({"label": "SMTP Success", "points": "+0"})

    if result["mx_found"]:
        score += 20
        breakdown.append({"label": "Valid MX", "points": "+20"})

    if not result["is_disposable"]:
        score += 10
        breakdown.append({"label": "Not Disposable", "points": "+10"})

    if not result["is_catch_all"]:
        score += 15
        breakdown.append({"label": "Not Catch-all", "points": "+15"})

    if not result["is_role_based"]:
        score += 5
        breakdown.append({"label": "Not Role-based", "points": "+5"})

    if not result["is_free_email"]:
        score += 10
        breakdown.append({"label": "Business Email", "points": "+10"})
    else:
        breakdown.append({"label": "Free Email", "points": "+0"})
        
    result["score"] = min(100, max(0, score))
    result["breakdown"] = breakdown
    
    # 8. SaaS Status Classification
    code = result["smtp_code"]
    msg = result["smtp_message"].lower()
    
    if result["smtp_check"]:
        result["status"] = "valid"
        result["reason"] = "Delivered successfully"
        result["risk"] = "low"
        result["action"] = "Send"
        
        if result["is_catch_all"]:
            result["status"] = "catch_all"
            result["reason"] = "Catch-all enabled"
            result["risk"] = "medium"
            result["action"] = "Risky"
        elif result["is_disposable"]:
            result["status"] = "disposable"
            result["reason"] = "Disposable provider"
            result["risk"] = "high"
            result["action"] = "Remove"
        elif result["is_role_based"]:
            result["status"] = "role_based"
            result["reason"] = "Role-based account"
            result["risk"] = "medium"
            result["action"] = "Avoid"
    else:
        # Map failures
        if code == 552 or "storage" in msg or "full" in msg:
            result["status"] = "inbox_full"
            result["reason"] = "Mailbox full"
            result["risk"] = "medium"
            result["action"] = "Retry later"
            result["retry"] = True
        elif code == 550 and ("disabled" in msg or "suspended" in msg or "unavailable" in msg):
            result["status"] = "disabled"
            result["reason"] = "Account disabled"
            result["risk"] = "high"
            result["action"] = "Remove"
        elif code in [421, 450, 451]:
            result["status"] = "temporary_failure"
            if "Timeout" in result["smtp_message"] or "Check Port 25" in result["smtp_message"]:
                result["reason"] = "SMTP Connection Timeout (Port 25 Blocked)"
                result["action"] = "Run on VPS with Port 25 open"
            else:
                result["reason"] = "Temporary failure (Greylisted)"
                result["action"] = "Retry"
            result["risk"] = "medium"
            result["retry"] = True
        elif code == 554 or "spam" in msg or "blocked" in msg:
            result["status"] = "blocked"
            result["reason"] = "Anti-spam protection"
            result["risk"] = "high"
            result["action"] = "Retry different IP"
            result["retry"] = True
        elif code == 550:
            result["status"] = "invalid"
            result["reason"] = "Mailbox not found"
            result["risk"] = "high"
            result["action"] = "Remove"
        else:
            result["status"] = "unknown"
            result["reason"] = "No clear SMTP signal"
            result["risk"] = "medium"
            result["action"] = "Unknown"

    logger.info(f"Finished verification for: {email} - Status: {result['status']}")
    return result
