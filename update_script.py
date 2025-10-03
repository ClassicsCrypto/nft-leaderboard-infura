import os
import requests
import json
from datetime import datetime, timezone

# --- CONFIGURATION ---
API_KEY = os.environ.get('ALCHEMY_API_KEY')
CONTRACT_ADDRESS = '0xc1374b803DFb1A9c87eaB9e76929222DBa3a8C39'
TOKEN_ID = '233135866589270025735431199023256918527023659760796851524427037696933759150'
# -------------------

def fetch_leaderboard():
    """Fetches all token holders using the Alchemy NFT API and handles pagination."""
    if not API_KEY:
        raise ValueError("ALCHEMY_API_KEY is not set in GitHub secrets.")

    all_owners = []
    page_key = None
    
    print("Starting to fetch data from Alchemy...")
    while True:
        # Alchemy's endpoint for getting owners for a specific ERC-1155 token ID
        url = f"https://base-mainnet.g.alchemy.com/nft/v3/{API_KEY}/getOwnersForToken"
        
        params = {
            'contractAddress': CONTRACT_ADDRESS,
            'tokenId': TOKEN_ID,
        }
        if page_key:
            params['pageKey'] = page_key
        
        headers = {"accept": "application/json"}
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status() # Raise an error for bad responses
        
        data = response.json()
        
        # Add the owners from the current page to our list
        owners_on_page = data.get('owners', [])
        all_owners.extend(owners_on_page)
        print(f"Fetched {len(owners_on_page)} owners. Total so far: {len(all_owners)}.")
        
        # Check for the next page using 'pageKey'
        page_key = data.get('pageKey')
        if not page_key:
            print("No more pages to fetch. All data retrieved.")
            break # Exit the loop if there's no more pageKey

    # Process the raw data into the desired leaderboard format.
    # Alchemy provides balances directly, so we don't need to calculate them.
    leaderboard = [{'address': owner['ownerAddress'], 'count': owner['tokenBalances'][0]['balance']} for owner in all_owners]
    
    # Sort by count in descending order
    leaderboard.sort(key=lambda x: x['count'], reverse=True)
    return leaderboard

def main():
    """Main function to run the script."""
    print("Updating NFT leaderboard using Alchemy...")
    leaderboard_data = fetch_leaderboard()
    
    output = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'leaderboard': leaderboard_data
    }
    
    with open('leaderboard.json', 'w') as f:
        json.dump(output, f, indent=2)
        
    print(f"Successfully wrote {len(leaderboard_data)} entries to leaderboard.json.")

if __name__ == '__main__':
    main()
