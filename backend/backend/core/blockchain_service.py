import os
import json
from pathlib import Path
from web3 import Web3

# Load environment variables
contract_address = os.getenv("PHISHING_CONTRACT_ADDRESS")
rpc_url = os.getenv("ETH_SEPOLIA_RPC_URL")
private_key = os.getenv("BLOCKCHAIN_PRIVATE_KEY")

# Load contract ABI from file
BASE_DIR = Path(__file__).resolve().parent.parent
abi_path = BASE_DIR / 'backend' / 'contracts' / 'PhishingReputation.json'
with open(abi_path) as f:
    artifact = json.load(f)
abi = artifact["abi"]

# Connect to Sepolia network
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Create contract instance
contract = w3.eth.contract(address=w3.to_checksum_address(contract_address), abi=abi)

def submit_phishing_report(report_hash: bytes, domain_hash: bytes, sender_address: str):
    try:
        nonce = w3.eth.getTransactionCount(sender_address)
        txn = contract.functions.submitReport(report_hash, domain_hash).buildTransaction({
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': w3.toWei('10', 'gwei')
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return w3.toHex(tx_hash)
    except Exception as e:
        # Optionally log error here
        raise RuntimeError(f"Blockchain transaction failed: {str(e)}")

def get_domain_reputation(domain_hash: bytes):
    try:
        return contract.functions.getDomainReputation(domain_hash).call()
    except Exception as e:
        # Optionally log error here
        raise RuntimeError(f"Could not fetch domain reputation: {str(e)}")
