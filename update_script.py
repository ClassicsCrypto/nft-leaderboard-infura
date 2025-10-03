import os
import requests
import json
from datetime import datetime, timezone

# --- CONFIGURATION ---
API_KEY = os.environ.get('ALCHEMY_API_KEY')
CONTRACT_ADDRESS = '0xc1374b803DFb1A9c87eaB9e76929222DBa3a8C39'
# The token ID we are interested in, now as a lowercase hex string for comparison
TARGET_TOKEN_ID_HEX = '0x33b821147a4f21f1565b99f55e51e1e87e2b831454593457193a0b4c9e42e86a'
# -------------------

def fetch_and_calculate_balances():
    """Fetches all ERC-1155 transfers for a contract and calculates final balances."""
    if not API_KEY:
        raise ValueError("ALCHEMY_API_KEY is not set in GitHub secrets.")

    balances = {}
    page_key = None
    
    # Use Alchemy's main RPC endpoint, not the NFT-specific one
    url = f"https://base-mainnet.g.alchemy.com/v2/{API_KEY}"
    
    print("Starting to fetch all transfer events using alchemy_getAssetTransfers. This may take some time...")
    while True:
        # This is a low-level JSON-RPC request
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "fromBlock": "0x0",
                    "toBlock": "latest",
                    "contractAddresses": [CONTRACT_ADDRESS],
                    "category": ["erc1155"],
                    "withMetadata": False,
                    "excludeZeroValue": True,
                    "pageKey": page_key # Will be None on the first request
                }
            ]
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        result = data.get('result', {})
        transfers = result.get('transfers', [])
        
        print(f"Processing {len(transfers)} transfer events...")
        for transfer in transfers:
            # We must check the specific token ID within the transfer data
            if transfer.get('erc1155Metadata') and transfer['erc1155Metadata'][0]['tokenId'] == TARGET_TOKEN_ID_HEX:
                from_address = transfer.get('from', '').lower()
                to_address = transfer.get('to', '').lower()
                # The value is a hex string, convert it to an integer
                amount = int(transfer['erc1155Metadata'][0]['value'], 16)

                # Subtract from the sender's balance (if not a mint from the zero address)
                if from_address != '0x0000000000000000000000000000000000000000':
                    balances[from_address] = balances.get(from_address, 0) - amount
                
                # Add to the receiver's balance
                balances[to_address] = balances.get(to_address, 0) + amount

        # Check for the next page of results
        page_key = result.get('pageKey')
        if not page_key:
            print("No more pages. All events processed.")
            break
        else:
            print("Fetching next page...")

    # Format the final balances into the leaderboard structure
    leaderboard = [{'address': addr, 'count': count} for addr, count in balances.items() if count > 0]
    leaderboard.sort(key=lambda x: x['count'], reverse=True)
    return leaderboard

def main():
    """Main function to run the script."""
    print("Updating NFT leaderboard by processing all transaction events...")
    leaderboard_data = fetch_and_calculate_balances()
    
    output = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'leaderboard': leaderboard_data
    }
    
    with open('leaderboard.json', 'w') as f:
        json.dump(output, f, indent=2)
        
    print(f"Successfully wrote {len(leaderboard_data)} entries to leaderboard.json.")

if __name__ == '__main__':
    main()
