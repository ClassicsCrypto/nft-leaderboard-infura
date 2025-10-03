import os
import requests
import json
from datetime import datetime, timezone
import time

# --- CONFIGURATION ---
API_KEY = os.environ.get('OPENSEA_API_KEY')
CONTRACT_ADDRESS = '0xc1374b803dfb1a9c87eaB9e76929222DBa3a8C39'
# OpenSea uses the decimal string for the identifier
TARGET_TOKEN_ID = '233135866589270025735431199023256918527023659760796851524427037696933759150'
# -------------------

def fetch_and_calculate_balances():
    if not API_KEY:
        raise ValueError("OPENSEA_API_KEY is not set in GitHub secrets.")

    balances = {}
    next_cursor = None
    
    # Use OpenSea's events endpoint
    base_url = f"https://api.opensea.io/api/v2/events/chain/base/contract/{CONTRACT_ADDRESS}"
    
    print("Starting to fetch all transfer events from OpenSea's API...")
    while True:
        params = {
            'event_type': 'item_transferred',
            'limit': 100 # Max limit is 100
        }
        if next_cursor:
            params['next'] = next_cursor

        headers = {
            "accept": "application/json",
            "X-API-KEY": API_KEY
        }

        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        events = data.get('asset_events', [])
        
        print(f"Processing {len(events)} transfer events...")
        for event in events:
            # Check if the event is for our specific token ID
            if event.get('nft', {}).get('identifier') == TARGET_TOKEN_ID:
                from_address = event.get('from_account', {}).get('address', '').lower()
                to_address = event.get('to_account', {}).get('address', '').lower()
                amount = int(event.get('quantity', 0))

                if from_address and to_address != '0x0000000000000000000000000000000000000000':
                    balances[from_address] = balances.get(from_address, 0) - amount
                
                if to_address:
                    balances[to_address] = balances.get(to_address, 0) + amount
        
        # Check for the next page
        next_cursor = data.get('next')
        if not next_cursor:
            print("No more pages. All events processed.")
            break
        else:
            print(f"Fetching next page with cursor: {next_cursor[:10]}...")
            time.sleep(0.3) # Be polite to the API and avoid rate limits

    leaderboard = [{'address': addr, 'count': count} for addr, count in balances.items() if count > 0]
    leaderboard.sort(key=lambda x: x['count'], reverse=True)
    return leaderboard

def main():
    """Main function to run the script."""
    print("Updating NFT leaderboard by processing all transaction events from OpenSea...")
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
