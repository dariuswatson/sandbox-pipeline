import requests
from requests.auth import HTTPBasicAuth

import config


def get_activities(access_token, organization_id, start_time, stop_time, project_id=None, page_limit=100, page_start_id=None):
    """
    Fetches activity records for a given Hubstaff organization.
    See https://developer.hubstaff.com/docs/hubstaff_v2#!/activities/getV2OrganizationsOrganizationIdActivities
    """
    url = f'{config.BASE_URL}/organizations/{organization_id}/activities'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    params = {
        'page_limit': page_limit
    }

    if page_start_id:
        params['page_start_id'] = page_start_id
    if start_time:
        params['time_slot[start]'] = start_time
    if stop_time:
        params['time_slot[stop]'] = stop_time
    if project_id:
        params['filters[project_id][]'] = project_id

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Activities Error {response.status_code}: {response.text}")
        raise Exception("Failed to retrieve activities.")


def get_all_activities_for_date(access_token, organization_id, start_time, stop_time, project_id=None, page_limit=100):
    """
    Fetches all activities for the given organization and date range, paging through results.
    """
    all_activities = []
    page_start_id = None

    while True:
        response = get_activities(access_token, organization_id, start_time, stop_time, project_id, page_limit, page_start_id)

        activities = response.get('activities', [])
        if not activities:
            break

        all_activities.extend(activities)

        # Get the next page_start_id
        page_start_id = response.get("pagination", {}).get("next_page_start_id")

        # If fewer than the page_limit were returned, we're done
        if len(activities) < page_limit:
            break

    return {'activities': all_activities}