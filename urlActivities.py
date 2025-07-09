

import requests

import config

def get_url_activities(access_token, organization_id, start_time, stop_time, project_id, page_limit=100, page_start_id=None):
    """
    Fetches URL activity data from Hubstaff.

    """
    url = f"{config.BASE_URL}/projects/{project_id}/url_activities"

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
        raise Exception(f"URL Activities Error {response.status_code}: {response.text}")

def flatten_url_activities(url_activities):
    activities = []
    details = []

    for activity in url_activities:
        activity_id = activity.get('id')

        # Add the flattened activity record
        activities.append({
            'id': activity_id,
            'site': activity.get('site'),
            'date': activity.get('date'),
            'created_at': activity.get('created_at'),
            'updated_at': activity.get('updated_at'),
            'time_slot': activity.get('time_slot'),
            'user_id': activity.get('user_id'),
            'project_id': activity.get('project_id'),
            'tracked': activity.get('tracked')
        })

        # Flatten each detail with a sequence number
        for index, detail in enumerate(activity.get('details', []), start=1):
            details.append({
                'activity_id': activity_id,
                'sequence': index,
                'title': detail.get('title'),
                'url': detail.get('url'),
                'tracked': detail.get('tracked')
            })

    return activities, details


def get_all_urls_for_date(access_token, organization_id, start_time, stop_time, project_id=None, page_limit=100):
    """
    Fetches all URL Activities for the given organization and date range, paging through results.
    """
    all_urls = []
    all_details = []
    page_start_id = None

    while True:
        response = get_url_activities(access_token, organization_id, start_time, stop_time, project_id, page_limit, page_start_id)

        urls, details = flatten_url_activities(response.get('urls', []))
        if not urls:
            break

        all_urls.extend(urls)
        all_details.extend(details)

        # Get the next page_start_id
        page_start_id = response.get("pagination", {}).get("next_page_start_id")

        # If fewer than the page_limit were returned, we're done
        if len(urls) < page_limit:
            break

    return all_urls, all_details