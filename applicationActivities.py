

import requests

import config

def get_app_activities(access_token, organization_id, start_time, stop_time, project_id, page_limit=100, page_start_id=None):
    """
    Fetches URL activity data from Hubstaff.

    """
    url = f"{config.BASE_URL}/projects/{project_id}/application_activities"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    params = {
        'time_slot[start]': start_time,
        'time_slot[stop]': stop_time,
        'page_limit': page_limit
    }

    if page_start_id:
        params['page_start_id'] = page_start_id
    if start_time:
        params['time_slot[start]'] = start_time
    if stop_time:
        params['time_slot[stop]'] = stop_time


    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"App Activities Error {response.status_code}: {response.text}")


def get_all_apps_for_date(access_token, organization_id, start_time, stop_time, project_id=None, page_limit=100):
    """
    Fetches all URL Activities for the given organization and date range, paging through results.
    """
    all_apps = []
    page_start_id = None

    while True:
        response = get_app_activities(access_token, organization_id, start_time, stop_time, project_id, page_limit, page_start_id)

        apps = response.get('applications', [])
        if not apps:
            break

        all_apps.extend(apps)

        # Get the next page_start_id
        page_start_id = response.get("pagination", {}).get("next_page_start_id")

        # If fewer than the page_limit were returned, we're done
        if len(apps) < page_limit:
            break

    return all_apps