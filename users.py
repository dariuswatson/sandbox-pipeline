import csv
import os
import requests

import config
import fileManager

# this should be replaced with a call to only insert a user if they don't already exist
def load_known_users(filename):
    """Loads existing user records into a dict keyed by user_id."""
    users = {}

    # doesn't exist create it
    if not os.path.exists(filename):
        print(f'Load Users file does not exist: {filename}')
        return users

    # opens exist file and loads the users
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            users[int(row['id'])] = row
    return users

def get_user(access_token, user_id):
    """Calls Hubstaff API to fetch user info by ID."""
    url = f"{config.BASE_URL}/users/{user_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('user')
    else:
        print(f"Failed to fetch user {user_id}: {response.status_code}")
        return None

def update_users_from_activities(access_token, known_users, activities, filename):
    """Ensures all users from activity data are known and added if missing."""
    activity_user_ids = {a['user_id'] for a in activities}
    missing_user_ids = activity_user_ids - set(known_users.keys())


    new_users = []
    for user_id in missing_user_ids:
        user_data = get_user(access_token, user_id)
        if user_data:
            new_users.append(user_data)
            known_users[user_data['id']] = user_data

    if new_users:
        fileManager.write_dicts_to_csv(new_users, f'{config.DATA_FOLDER}{config.USERS_FILE}') # add to the known users files
        fileManager.write_dicts_to_csv(new_users, filename) # indicate who is new today
        print(f"\tNew User count: {len(new_users)}")


def update_users_from_urls(access_token, known_users, urls, filename):
    """Ensures all users from url data are known and added if missing."""
    url_user_ids = {a['user_id'] for a in urls}
    missing_user_ids = url_user_ids - set(known_users.keys())

    new_users = []
    for user_id in missing_user_ids:
        user_data = get_user(access_token, user_id)
        if user_data:
            new_users.append(user_data)
            known_users[user_data['id']] = user_data

    if new_users:
        fileManager.write_dicts_to_csv(new_users, f'{config.DATA_FOLDER}{config.USERS_FILE}') # add to the known users files
        fileManager.write_dicts_to_csv(new_users, filename) # indicate who is new today
        print(f"\tNew User count: {len(new_users)}")