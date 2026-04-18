import argparse
import asyncio
import os
import json
from app.services.email_validator import verify_email
from app.utils.helpers import export_to_csv

async def process_file(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return
        
    with open(input_file, 'r') as f:
        emails = [line.strip() for line in f if line.strip()]
        
    print(f"Found {len(emails)} emails. Starting verification...")
    
    # Process with bounded concurrency
    semaphore = asyncio.Semaphore(10) # 10 concurrent requests max
    
    async def verify_with_semaphore(email):
        async with semaphore:
            return await verify_email(email)
            
    tasks = [verify_with_semaphore(email) for email in emails]
    results = await asyncio.gather(*tasks)
    
    # Output to CSV or JSON depending on the extension
    if output_file.endswith('.csv'):
        export_to_csv(results, output_file)
    else:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
            
    print(f"Verification complete. Results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email Verifier CLI")
    parser.add_argument("input_file", help="Input file containing emails (one per line)")
    parser.add_argument("--output", "-o", default="results.csv", help="Output file location (use .csv or .json extension)")
    
    args = parser.parse_args()
    asyncio.run(process_file(args.input_file, args.output))
