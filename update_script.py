import os
import requests
import json
from datetime import datetime, timezone

# --- CONFIGURATION ---
API_KEY = os.environ.get('COVALENT_API_KEY')
CONTRACT_ADDRESS = '0xc1374b803DFb1A9c87eaB9e76929222DBa3a8C39'
TOKEN_ID = '233135866589270025735431199023256918527023659760796851524427037696933759150'
CHAIN_NAME = 'base-mainnet'
# -------------------

def fetch_leaderboard():
    if not API_KEY:
        raise ValueError("COVALENT_API_KEY is not set in GitHub secrets.")

    url = f"https://api.covalenthq.com/v1/{CHAIN_NAME}/tokens/{CONTRACT_ADDRESS}/token_holders/?quote-currency=USD&format=JSON&token-id={TOKEN_ID}&page-size=100000&key={API_KEY}"
    
    print("Fetching data from Covalent...")
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()['data']['items']

    leaderboard = []
    for item in data:
        quantity = int(item['balance']) / (10**int(item['contract_decimals']))
        if quantity > 0:
            leaderboard.append({'address': item['address'], 'count': int(quantity)})
    
    leaderboard.sort(key=lambda x: x['count'], reverse=True)
    return leaderboard

def main():
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
