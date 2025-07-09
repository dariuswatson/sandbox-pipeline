import requests
from requests.auth import HTTPBasicAuth
import argparse
from datetime import datetime, timedelta

import config
import users
import urlActivities
import fileManager
import activitiesManager
import applicationActivities
import tokenManager


def get_organizations(access_token):
    org_url = f'{config.BASE_URL}/organizations'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    params = {
        'page_start_id': 1,
        'page_limit': 100
    }

    response = requests.get(org_url, headers=headers, params=params)

    if response.status_code == 200:
        print("Organizations data retrieved.")
        orgs = response.json()
        return next((org['id'] for org in orgs['organizations'] if org['name'] == config.ORG_NAME), None)
    elif response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            print(f"Rate limit hit. Retry after {retry_after} seconds.")
        else:
            print("Rate limit hit. No Retry-After header provided.")
        raise Exception("Failed to retrieve Organizations due to rate limiting.")
    else:
        print(f"Organizations Error {response.status_code}: {response.text}")
        raise Exception("Failed to retrieve organizations.")


def get_projects(access_token, organization_id, page_limit=100, page_start_id=None):
    """
    Fetches project records for a given Hubstaff organization.
    See https://developer.hubstaff.com/docs/hubstaff_v2#!/projects/getV2OrganizationsOrganizationIdProjects
    """
    url = f'{config.BASE_URL}/organizations/{organization_id}/projects'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    params = {
        'page_limit': page_limit
    }

    if page_start_id:
        params['page_start_id'] = page_start_id

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        projects = response.json()
        return next((project['id'] for project in projects['projects'] if project['name'] == config.PROJECT_NAME), None)
    elif response.status_code == 429:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            print(f"Rate limit hit. Retry after {retry_after} seconds.")
        else:
            print("Rate limit hit. No Retry-After header provided.")
        raise Exception("Failed to retrieve Projects due to rate limiting.")
    else:
        print(f"Projects Error {response.status_code}: {response.text}")
        raise Exception("Failed to retrieve projects.")


# ------------------------ MAIN ------------------------
# -- python main.py start_date

if __name__ == '__main__':
    try:
        # Parse CLI arguments
        parser = argparse.ArgumentParser(description="Process Hubstaff data from start date through yesterday.")
        parser.add_argument("start_date", help="Start date in YYYY-MM-DD format")
        args = parser.parse_args()

        token = tokenManager.get_access_token()
        org_id = get_organizations(token)
        print(f"Org Id: {org_id}")

        project_id = get_projects(token, org_id)
        print(f"Project Id: {project_id}")

        # load all my known users, and we'll add to this list/file as we pull in activities
        known_users = users.load_known_users(f'{config.DATA_FOLDER}{config.USERS_FILE}')
        print(f'# of Known Users:{len(known_users)}')

        # All activities are logged to a project
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.today() - timedelta(days=1)
        end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # loop through all the dates in a range
        current_date = start_date


        while current_date <= end_date:
            print(f'Loading Date: {current_date}')
            day_str = current_date.strftime('%Y-%m-%d')
            day_start = current_date.strftime("%Y-%m-%dT00:00:00Z")
            day_end = current_date.strftime("%Y-%m-%dT23:59:59Z")

            # GET Activities
            activities = activitiesManager.get_all_activities_for_date(token, org_id, day_start, day_end, project_id)
            fileManager.write_dicts_to_csv(activities.get('activities', []), f'{config.DATA_FOLDER}activities_{day_str}.csv')
            print(f"\tNew Activities count: {len(activities.get('activities', []))}")

            # GET Url Activities
            urls, details = urlActivities.get_all_urls_for_date(token, org_id, day_start, day_end, project_id)
            fileManager.write_dicts_to_csv(urls, f'{config.DATA_FOLDER}url_activities_{day_str}.csv')
            print(f"\tNew URLs count: {len(urls)}")
            fileManager.write_dicts_to_csv(details, f'{config.DATA_FOLDER}url_details_{day_str}.csv')
            print(f"\tNew URL Details count: {len(details)}")

            # GET Application Activities
            apps = applicationActivities.get_all_apps_for_date(token, org_id, day_start, day_end, project_id)
            fileManager.write_dicts_to_csv(apps, f'{config.DATA_FOLDER}app_activities_{day_str}.csv')
            print(f"\tNew Application Activity count: {len(apps)}")

            ## Save the New User Data
            users.update_users_from_activities(token, known_users, activities.get('activities', []), f'{config.DATA_FOLDER}new_users_{day_str}.csv')
            users.update_users_from_urls(token, known_users, urls, f'{config.DATA_FOLDER}new_users_{day_str}.csv')

            # Process the data as needed
            current_date += timedelta(days=1)

    except Exception as e:
        print("Overall Error:", e)
