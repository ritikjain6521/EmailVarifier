import dns.asyncresolver
import dns.resolver
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def get_mx_records(domain: str) -> list[str]:
    """Retrieve MX records for a given domain asynchronously."""
    try:
        resolver = dns.asyncresolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        answers = await resolver.resolve(domain, 'MX')
        # Sort by preference (priority)
        records = sorted(answers, key=lambda r: r.preference)
        return [str(record.exchange).rstrip('.') for record in records]
    except dns.resolver.NoAnswer:
        logger.debug(f"No MX records found for {domain}")
        return []
    except dns.resolver.NXDOMAIN:
        logger.debug(f"Domain does not exist: {domain}")
        return []
    except Exception as e:
        logger.error(f"DNS lookup error for {domain}: {e}")
        return []
