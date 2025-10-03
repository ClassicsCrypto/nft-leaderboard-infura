import os
import requests
import json
from datetime import datetime, timezone

# --- CONFIGURATION ---
# Fetch credentials from GitHub Actions secrets
PROJECT_ID = os.environ.get('f279733f4b9a426f83d988d0664ae96c')
PROJECT_SECRET = os.environ.get('NtRlsAy1I29K1RQvOBwAQzjQGBHVTJxbgHtN3TUsLpXcX2j7bQE9lg')

# NFT Details
CONTRACT_ADDRESS = '0xc1374b803DFb1A9c87eaB9e76929222DBa3a8C39'
TOKEN_ID = '233135866589270025735431199023256918527023659760796851524427037696933759150'
CHAIN_ID = '8453' # Base Mainnet
# -------------------

def fetch_leaderboard():
    """Fetches all token holders using the Infura NFT API and handles pagination."""
    
    if not PROJECT_ID or not PROJECT_SECRET:
        raise ValueError("Infura credentials (INFURA_PROJECT_ID, INFURA_PROJECT_SECRET) are not set.")

    all_owners = []
    cursor = None
    
    print("Starting to fetch data from Infura...")
    while True:
        # Construct the URL, adding the cursor if it exists
        url = f"https://nft-api.infura.io/networks/{CHAIN_ID}/nfts/{CONTRACT_ADDRESS}/tokens/{TOKEN_ID}/owners"
        params = {'cursor': cursor} if cursor else {}
        
        # Make the request with Basic Authentication
        response = requests.get(
            url,
            params=params,
            auth=(PROJECT_ID, PROJECT_SECRET)
        )
        
        # Raise an error for bad responses (4xx or 5xx)
        response.raise_for_status()
        
        data = response.json()
        
        # Add the owners from the current page to our list
        owners_on_page = data.get('owners', [])
        all_owners.extend(owners_on_page)
        print(f"Fetched {len(owners_on_page)} owners. Total so far: {len(all_owners)}.")
        
        # Check for the next page
        cursor = data.get('cursor')
        if not cursor:
            print("No more pages to fetch. All data retrieved.")
            break # Exit the loop if there's no more cursor

    # Process the raw data into the desired leaderboard format
    leaderboard = []
    for owner_data in all_owners:
        leaderboard.append({
            'address': owner_data['ownerOf'],
            'count': int(owner_data['amount'])
        })
        
    # Sort by count in descending order
    leaderboard.sort(key=lambda x: x['count'], reverse=True)
    return leaderboard

def main():
    """Main function to run the script."""
    print("Updating NFT leaderboard...")
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
