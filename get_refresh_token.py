import requests
import json
import config
from requests.auth import HTTPBasicAuth

# === Load from config (which loads from environment variables) ===
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
REDIRECT_URI = config.REDIRECT_URI
SCOPE = config.SCOPE
TOKEN_URL = config.TOKEN_URL

# 1. Print the authorization URL
params = {
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URI,
    'response_type': 'code',
    'scope': SCOPE
}
auth_url = f"https://account.hubstaff.com/authorize?" + '&'.join([f"{k}={v}" for k, v in params.items()])
print("\nGo to this URL in your browser and log in:")
print(auth_url)

# 2. Prompt for the code
code = input("\nPaste the authorization code from the redirect URL here: ").strip()

# 3. Exchange code for tokens
post_data = {
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI
}
auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
response = requests.post(TOKEN_URL, data=post_data, auth=auth)

if response.status_code == 200:
    resp_data = response.json()
    access_token = resp_data['access_token']
    refresh_token = resp_data['refresh_token']
    expires_in = int(resp_data.get('expires_in', 3600))
    from datetime import datetime, timedelta
    expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

    token_data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at
    }
    with open('token.json', 'w') as f:
        json.dump(token_data, f, indent=2)
    print("\n✅ token.json created! You can now run your main script.")
else:
    print(f"\n❌ Error: {response.status_code} {response.text}") 