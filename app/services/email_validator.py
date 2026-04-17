import re
import asyncio
from typing import Dict, Any

from app.services.dns_checker import get_mx_records
from app.services.smtp_checker import check_smtp
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
        return result
        
    # 6. SMTP & Catch-All Check
    if check_smtp_enabled:
        # Add random delay to prevent blocking
        await asyncio.sleep(0.5) 
        
        is_deliverable, is_catch_all = await check_smtp(email, mx_records)
        result["smtp_check"] = is_deliverable
        result["is_catch_all"] = is_catch_all
    else:
        # If SMTP check is disabled, we set these cautiously
        result["smtp_check"] = False
        result["is_catch_all"] = False

    # 7. Scoring system (Additive)
    # SMTP success +40
    # Valid MX +20
    # Not disposable +10
    # Not catch-all +15
    # Not role-based +5
    # Not free email +10
    
    score = 0
    if result["smtp_check"]:
        score += 40
    if result["mx_found"]:
        score += 20
    if not result["is_disposable"]:
        score += 10
    if not result["is_catch_all"]:
        score += 15
    if not result["is_role_based"]:
        score += 5
    if not result["is_free_email"]:
        score += 10
        
    result["score"] = min(100, max(0, score))
    
    # Status determination based on required categories
    if not EMAIL_REGEX.match(email) or not result["mx_found"]:
        result["status"] = "invalid"
    elif result["is_disposable"]:
        result["status"] = "disposable"
    elif not result["smtp_check"] and check_smtp_enabled:
        result["status"] = "unknown" # Could be greylisted/unknown or invalid if it bounced
    elif result["is_catch_all"]:
        result["status"] = "catch_all"
    elif result["is_role_based"]:
        result["status"] = "role_based"
    elif result["is_free_email"]:
        result["status"] = "free_email"
    elif result["score"] >= 80:
        result["status"] = "valid"
    else:
        result["status"] = "risky"

    logger.info(f"Finished verification for: {email} - Status: {result['status']}")
    return result
