import os
import json
import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

import config

TOKEN_FILE = 'token.json'

def create_initial_token():
    """Create initial token using refresh token from config"""
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': config.REFRESH_TOKEN
    }
    auth = HTTPBasicAuth(config.CLIENT_ID, config.CLIENT_SECRET)
    response = requests.post(config.TOKEN_URL, data=data, headers=headers, auth=auth)

    if response.status_code == 200:
        resp_data = response.json()
        access_token = resp_data['access_token']
        refresh_token = resp_data.get('refresh_token', config.REFRESH_TOKEN)
        expires_in = int(resp_data.get('expires_in', 3600))  # seconds
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

        token_data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
        
        save_tokens(token_data)
        print("✅ Initial token created successfully.")
        return token_data
    else:
        print(f"Debug - Response: {response.status_code} {response.text}")
        raise Exception(f"❌ Failed to create initial token: {response.status_code} {response.text}")

def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        print("🔄 Token file does not exist. Creating initial token...")
        return create_initial_token()
    
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)

def save_tokens(token_data):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)

def is_token_expired(token_data):
    if 'expires_at' not in token_data:
        return True
    return datetime.utcnow() >= datetime.fromisoformat(token_data['expires_at'])

def refresh_access_token(refresh_token):
    headers = {
        'Accept': 'application/json'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    auth = HTTPBasicAuth(config.CLIENT_ID, config.CLIENT_SECRET)
    response = requests.post(config.TOKEN_URL, data=data, headers=headers, auth=auth)

    if response.status_code == 200:
        resp_data = response.json()
        access_token = resp_data['access_token']
        expires_in = int(resp_data.get('expires_in', 3600))  # seconds
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()

        print("✅ Access token refreshed.")
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
    else:
        raise Exception(f"❌ Failed to refresh access token: {response.status_code} {response.text}")

def get_access_token():
    token_data = load_tokens()

    if is_token_expired(token_data):
        print("🔄 Access token expired or missing. Refreshing...")
        token_data = refresh_access_token(token_data['refresh_token'])
        save_tokens(token_data)

    return token_data['access_token']
