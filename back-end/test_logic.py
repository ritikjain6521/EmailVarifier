import asyncio
import json
from app.services.email_validator import verify_email

async def test():
    emails = [
        "test100@gmail.com",
        "full@gmail.com",
        "disabled@gmail.com",
        "retry@gmail.com",
        "spam@gmail.com",
        "admin@gmail.com",
        "temp@mailinator.com"
    ]
    
    print(f"{'Email':<25} | {'Status':<15} | {'Reason':<25} | {'Risk':<10}")
    print("-" * 80)
    
    for email in emails:
        result = await verify_email(email)
        print(f"{result['email']:<25} | {result['status']:<15} | {result.get('reason', 'N/A'):<25} | {result.get('risk', 'N/A'):<10}")

if __name__ == "__main__":
    asyncio.run(test())
