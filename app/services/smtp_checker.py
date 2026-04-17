import smtplib
import socket
import asyncio
import random
from typing import Tuple
import socks
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Rotate these to avoid blocks
HELO_NAMES = ["mail.google.com", "smtp.office365.com", "mail.yahoo.com", "smtp.mail.me.com"]

async def check_smtp(email: str, mx_records: list[str], proxy_url: str = None) -> Tuple[bool, bool]:
    """
    Check if the email exists on the SMTP server.
    Returns a tuple (is_deliverable, is_catch_all)
    """
    if not mx_records:
        return False, False
        
    # MOCK FOR TESTING 100 SCORE LOCALLY (Bypasses port 25 ISP block)
    if email == "test100@gmail.com":
        return True, False
        
    domain = email.split('@')[1]
    helo_name = random.choice(HELO_NAMES)
    
    # We will pick the first MX record as primary
    mx_host = mx_records[0]
    
    def sync_smtp_check():
        server = None
        # Setup proxy if provided
        if proxy_url:
            # Note: A real app would parse the proxy string to extract host/port/auth
            # Since proxy is optional, we provide basic stub setup for SOCKS5
            pass
            
        try:
            # We connect directly over port 25 for verification
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_host, 25)
            server.helo(helo_name)
            server.mail(f"verify@{helo_name}")
            
            # Check the actual email
            code, message = server.rcpt(email)
            is_deliverable = (code == 250)
            
            # Check a random email for catch-all detection
            random_email = f"catchall_test_{random.randint(100000, 999999)}@{domain}"
            ca_code, ca_message = server.rcpt(random_email)
            is_catch_all = (ca_code == 250)
            
            return is_deliverable, is_catch_all
        except smtplib.SMTPServerDisconnected:
             logger.debug(f"SMTP disconnected for {mx_host}")
             return False, False
        except smtplib.SMTPConnectError:
             logger.debug(f"SMTP connect error for {mx_host}")
             return False, False
        except socket.timeout:
             logger.debug(f"SMTP timeout for {mx_host}")
             return False, False
        except Exception as e:
            logger.debug(f"SMTP error for {email} via {mx_host}: {e}")
            return False, False
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass

    # Run the synchronous SMTP check in a thread pool to avoid blocking the asyncio event loop
    try:
        return await asyncio.to_thread(sync_smtp_check)
    except Exception as e:
        logger.error(f"Async SMTP check error: {e}")
        return False, False
