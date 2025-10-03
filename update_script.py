import os
import requests
import json
from datetime import datetime, timezone

# --- CONFIGURATION ---
API_KEY = os.environ.get('ALCHEMY_API_KEY')
CONTRACT_ADDRESS = '0xc1374b803DFb1A9c87eaB9e76929222DBa3a8C39'
TOKEN_ID = '233135866589270025735431199023256918527023659760796851524427037696933759150'
# -------------------

def fetch_top_holders():
    """Fetches the top holders of a token using the Alchemy NFT API."""
    if not API_KEY:
        raise ValueError("ALCHEMY_API_KEY is not set in GitHub secrets.")

    print("Starting to fetch data for top holders from Alchemy...")
    
    # Alchemy's endpoint for getting owners for a specific ERC-1155 token ID
    url = f"https://base-mainnet.g.alchemy.com/nft/v3/{API_KEY}/getOwnersForToken"
    
    # We will make only ONE request for the first page, which gives us the top holders.
    # We also add a pageSize parameter to control how many results we get.
    params = {
        'contractAddress': CONTRACT_ADDRESS,
        'tokenId': TOKEN_ID,
        'pageSize': 50 # Let's ask for the Top 50 holders
    }
    
    headers = {"accept": "application/json"}
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status() # Raise an error for bad responses
    
    data = response.json()
    
    owners = data.get('owners', [])
    print(f"Successfully fetched {len(owners)} owners.")
    
    # Process the raw data into the desired leaderboard format.
    leaderboard = [{'address': owner['ownerAddress'], 'count': owner['tokenBalances'][0]['balance']} for owner in owners]
    
    # The API doesn't guarantee the order, so we still sort by count
    leaderboard.sort(key=lambda x: x['count'], reverse=True)
    return leaderboard

def main():
    """Main function to run the script."""
    print("Updating NFT leaderboard using Alchemy...")
    leaderboard_data = fetch_top_holders()
    
    output = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'leaderboard': leaderboard_data
    }
    
    with open('leaderboard.json', 'w') as f:
        json.dump(output, f, indent=2)
        
    print(f"Successfully wrote {len(leaderboard_data)} entries to leaderboard.json.")

if __name__ == '__main__':
    main()
