import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Configuration ===
# Load from environment variables with fallbacks to GH secrets
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
PAT = os.getenv('PAT')
USERNAME = os.getenv('USERNAME')
TOKEN_URL = os.getenv('TOKEN_URL')
BASE_URL = os.getenv('BASE_URL')
ORG_NAME = os.getenv('ORG_NAME')
PROJECT_NAME = os.getenv('PROJECT_NAME')
USERS_FILE = os.getenv('USERS_FILE')
DATA_FOLDER = os.getenv('DATA_FOLDER')

# these values could change or are dynamically determined
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
ORG_ID = 'ORG_ID'

# OAuth Configuration
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = os.getenv('SCOPE', 'openid hubstaff:read')
