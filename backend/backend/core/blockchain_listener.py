import os
import django
import asyncio
import json
from pathlib import Path
from web3 import Web3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

# -------------------- SETUP DJANGO ENVIRONMENT --------------------
BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from core.models import PhishingReport, ReputationToken  # Django models

# -------------------- LOAD ENV VARIABLES --------------------
load_dotenv(BASE_DIR / ".env")

contract_address = os.getenv("PHISHING_CONTRACT_ADDRESS")
rpc_url = os.getenv("ETH_SEPOLIA_RPC_URL")

if not contract_address or not rpc_url:
    raise ValueError("❌ Missing environment variables: PHISHING_CONTRACT_ADDRESS or ETH_SEPOLIA_RPC_URL")

# Ensure contract address format
if not contract_address.startswith("0x"):
    contract_address = f"0x{contract_address}"

# -------------------- CONNECT TO BLOCKCHAIN --------------------
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Add middleware for Sepolia or other PoA testnets
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if not w3.is_connected():
    raise ConnectionError("❌ Failed to connect to Ethereum node. Check RPC URL.")

# -------------------- LOAD CONTRACT ABI --------------------
with open(BASE_DIR / "backend" / "contracts" / "PhishingReputation.json") as f:
    artifact = json.load(f)
abi = artifact.get("abi")

if not abi:
    raise ValueError("❌ ABI not found in PhishingReputation.json")

contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=abi)

# -------------------- EVENT HANDLERS --------------------
def handle_report_submitted(event):
    args = event["args"]
    report_hash = args["reportHash"].hex()
    domain_hash = args["domainHash"].hex()
    reporter_address = args["reporter"]

    print(f"✅ New Report Submitted:\n  • Report: {report_hash}\n  • Domain: {domain_hash}\n  • Reporter: {reporter_address}")

    report, created = PhishingReport.objects.get_or_create(
        incident_hash=report_hash,
        defaults={
            "domain": domain_hash,
            "reporter_address": reporter_address,
            "verified": False,
        },
    )
    if not created:
        print("ℹ️ Report already exists in DB.")


def handle_tokens_awarded(event):
    args = event["args"]
    user_address = args["user"]
    amount = args["amount"]

    print(f"🏅 Tokens Awarded:\n  • User: {user_address}\n  • Amount: {amount}")

    token_record, _ = ReputationToken.objects.get_or_create(user_address=user_address)
    token_record.tokens = amount
    token_record.save()

# -------------------- EVENT LOOP --------------------
async def log_loop(event_filter, poll_interval):
    while True:
        try:
            for event in event_filter.get_new_entries():
                event_name = event.event
                if event_name == "ReportSubmitted":
                    handle_report_submitted(event)
                elif event_name == "TokensAwarded":
                    handle_tokens_awarded(event)
        except Exception as e:
            print(f"⚠️ Error processing event: {str(e)}")
        await asyncio.sleep(poll_interval)

# -------------------- MAIN FUNCTION --------------------
def main():
    print("🚀 Listening for blockchain events...")

    try:
        report_filter = contract.events.ReportSubmitted.create_filter(fromBlock="latest")
        tokens_filter = contract.events.TokensAwarded.create_filter(fromBlock="latest")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to create event filters: {str(e)}")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(report_filter, 2),
                log_loop(tokens_filter, 2),
            )
        )
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
    finally:
        loop.close()

# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    main()
