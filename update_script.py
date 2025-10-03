import os
import requests
import json
from datetime import datetime, timezone

# --- CONFIGURATION ---
API_KEY = os.environ.get('COVALENT_API_KEY')
CONTRACT_ADDRESS = '0xc1374b803DFb1A9c87eaB9e76929222DBa3a8C39'
# The token ID we are interested in, as an integer for easy comparison
TARGET_TOKEN_ID = 233135866589270025735431199023256918527023659760796851524427037696933759150
CHAIN_NAME = 'base-mainnet'
# The event signature for an ERC-1155 Transfer
TRANSFER_SINGLE_TOPIC = '0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62'
# -------------------

def fetch_and_calculate_balances():
    if not API_KEY:
        raise ValueError("COVALENT_API_KEY is not set in GitHub secrets.")

    balances = {}
    url = f"https://api.covalenthq.com/v1/{CHAIN_NAME}/events/address/{CONTRACT_ADDRESS}/?starting-block=1&ending-block=latest&page-size=1000&key={API_KEY}"

    print("Starting to fetch all transaction events. This may take a moment...")
    while url:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['data']
        items = data.get('items', [])
        
        print(f"Processing {len(items)} events...")

        for item in items:
            # We only care about 'TransferSingle' events
            if item.get('raw_log_topics', []) and item['raw_log_topics'][0] == TRANSFER_SINGLE_TOPIC:
                # Decode the event parameters
                params = {p['name']: p['value'] for p in item.get('decoded', {}).get('params', [])}
                
                # Check if the event is for our specific token ID
                event_token_id = int(params.get('id', -1))
                if event_token_id == TARGET_TOKEN_ID:
                    from_address = params.get('from', '').lower()
                    to_address = params.get('to', '').lower()
                    amount = int(params.get('value', 0))

                    # Subtract from the sender's balance (if not a mint)
                    if from_address != '0x0000000000000000000000000000000000000000':
                        balances[from_address] = balances.get(from_address, 0) - amount
                    
                    # Add to the receiver's balance
                    balances[to_address] = balances.get(to_address, 0) + amount
        
        # Check for the next page of results
        url = data['links'].get('next')
        if url:
            url += f"&key={API_KEY}" # Covalent's next link doesn't include the key
            print("Fetching next page...")

    print("All events processed. Finalizing leaderboard.")
    # Format the balances into the leaderboard structure
    leaderboard = [{'address': addr, 'count': count} for addr, count in balances.items() if count > 0]
    leaderboard.sort(key=lambda x: x['count'], reverse=True)
    return leaderboard

def main():
    print("Updating NFT leaderboard by processing transaction events...")
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
