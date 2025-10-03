import os
import requests
import json
from datetime import datetime, timezone

# --- CONFIGURATION ---
API_KEY = os.environ.get('ALCHEMY_API_KEY')
CONTRACT_ADDRESS = '0xc1374b803DFb1A9c87eaB9e76929222DBa3a8C39'
# The token ID we are interested in, now as an integer for robust comparison
TARGET_TOKEN_ID = 233135866589270025735431199023256918527023659760796851524427037696933759150
# -------------------

def fetch_and_calculate_balances():
    """Fetches all ERC-1155 transfers for a contract and calculates final balances."""
    if not API_KEY:
        raise ValueError("ALCHEMY_API_KEY is not set in GitHub secrets.")

    balances = {}
    page_key = None
    
    url = f"https://base-mainnet.g.alchemy.com/v2/{API_KEY}"
    
    print("Starting to fetch all transfer events using alchemy_getAssetTransfers...")
    while True:
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getAssetTransfers",
            "params": [
                {
                    "fromBlock": "0x0",
                    "toBlock": "latest",
                    "contractAddresses": [CONTRACT_ADDRESS],
                    # Broaden the search category to be safe
                    "category": ["erc1155", "internal", "external"],
                    "withMetadata": False,
                    "excludeZeroValue": True,
                    "pageKey": page_key
                }
            ]
        }
        
        headers = {"accept": "application/json", "content-type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        result = data.get('result', {})
        transfers = result.get('transfers', [])
        
        print(f"Processing {len(transfers)} transfer events...")
        for transfer in transfers:
            # Check if the transfer has the required ERC-1155 metadata
            if transfer.get('erc1155Metadata'):
                # Convert the token ID from the API (which is a hex string) to an integer for a reliable comparison
                received_token_id = int(transfer['erc1155Metadata'][0]['tokenId'], 16)

                if received_token_id == TARGET_TOKEN_ID:
                    from_address = transfer.get('from', '').lower()
                    to_address = transfer.get('to', '').lower()
                    amount = int(transfer['erc1155Metadata'][0]['value'], 16)

                    if from_address != '0x0000000000000000000000000000000000000000':
                        balances[from_address] = balances.get(from_address, 0) - amount
                    
                    balances[to_address] = balances.get(to_address, 0) + amount

        page_key = result.get('pageKey')
        if not page_key:
            print("No more pages. All events processed.")
            break
        else:
            print("Fetching next page...")

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
