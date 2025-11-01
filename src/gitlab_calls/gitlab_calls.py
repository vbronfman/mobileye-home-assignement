"""
Functions to call GitLab API :
  - set user permissions
  - querying issues/merge requests
"""

import requests
import os
from datetime import datetime
#from typing import List, Dict, Literal

# GitLab Configuration
GITLAB_URL = os.getenv('GITLAB_URL', 'http://localhost:8080')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', '')

# Headers for API requests
HEADERS = {
    'PRIVATE-TOKEN': GITLAB_TOKEN,
    'Content-Type': 'application/json'
}


def grant_user_role(username: str, repo_or_group: str, role: str) -> map:
    """
    Grant or change role permissions for a user on a repository or group.
    
    Args:
        username: GitLab username
        repo_or_group: Repository path (e.g., 'group/repo') or group name
        role: Access level - one of: guest, reporter, developer, maintainer, owner
    
    Returns:
        Dictionary with API response
        
    Raises:
        Exception: If API request fails
    """
    # Map role names to GitLab access levels
    role_mapping = {
        'guest': 10,
        'reporter': 20,
        'developer': 30,
        'maintainer': 40,
        'owner': 50
    }
    
    if role.lower() not in role_mapping:
        raise ValueError(f"Invalid role. Must be one of: {', '.join(role_mapping.keys())}")
    
    access_level = role_mapping[role.lower()]
    
    # Get user ID by username
    user_url = f"{GITLAB_URL}/api/v4/users?username={username}"
    user_response = requests.get(user_url, headers=HEADERS)
    user_response.raise_for_status()
    
    users = user_response.json()
    if not users:
        raise Exception(f"User '{username}' not found")
    
    user_id = users[0]['id']
    
    # Determine if it's a project or group by checking if path contains '/'
    if '/' in repo_or_group:
        # It's a project (repository)
        project_url = f"{GITLAB_URL}/api/v4/projects/{requests.utils.quote(repo_or_group, safe='')}"
        project_response = requests.get(project_url, headers=HEADERS)
        project_response.raise_for_status()
        project_id = project_response.json()['id']
        
        # Try to update existing member first
        member_url = f"{GITLAB_URL}/api/v4/projects/{project_id}/members/{user_id}"
        update_response = requests.put(
            member_url,
            headers=HEADERS,
            json={'access_level': access_level}
        )
        
        # If member doesn't exist (404), add them
        if update_response.status_code == 404:
            add_url = f"{GITLAB_URL}/api/v4/projects/{project_id}/members"
            response = requests.post(
                add_url,
                headers=HEADERS,
                json={'user_id': user_id, 'access_level': access_level}
            )
            response.raise_for_status()
            return response.json()
        else:
            update_response.raise_for_status()
            return update_response.json()
    else:
        # It's a group
        group_url = f"{GITLAB_URL}/api/v4/groups/{requests.utils.quote(repo_or_group, safe='')}"
        group_response = requests.get(group_url, headers=HEADERS)
        group_response.raise_for_status()
        group_id = group_response.json()['id']
        
        # Try to update existing member first
        member_url = f"{GITLAB_URL}/api/v4/groups/{group_id}/members/{user_id}"
        update_response = requests.put(
            member_url,
            headers=HEADERS,
            json={'access_level': access_level}
        )
        
        # If member doesn't exist (404), add them
        if update_response.status_code == 404:
            add_url = f"{GITLAB_URL}/api/v4/groups/{group_id}/members"
            response = requests.post(
                add_url,
                headers=HEADERS,
                json={'user_id': user_id, 'access_level': access_level}
            )
            response.raise_for_status()
            return response.json()
        else:
            update_response.raise_for_status()
            return update_response.json()


def get_items_by_year(item_type: str, year: int) -> list[map] | None:
    """
    Retrieve all merge requests or issues created in a given year.
    
    Args:
        item_type: Type of items to retrieve - 'mr' for merge requests or 'issues'
        year: 4-digit year (e.g., 2023)
    
    Returns:
        List of dictionaries containing items data
        
    Raises:
        Exception: If API request 
    """        
    
    if not ( 2001 <= year <=  datetime.now().year ): # TODO: add proper min year
        raise ValueError("Value of 'year' argument is Not valid")
    
    # Define date range for the year
    start_date = f"{year}-01-01T00:00:00Z"
    end_date = f"{year}-12-31T23:59:59Z"
    
    # Determine endpoint based on item type
    match item_type:
        case 'mr':
          endpoint = 'merge_requests'
        case 'issues':
          endpoint = 'issues'
        case _:
           raise ValueError("item_type must be either 'mr' or 'issues'")
            
    
    all_items = []
    page = 1
    per_page = 100  # Max items per page
    
    while True:
        # API endpoint for all merge requests/issues
        url = f"{GITLAB_URL}/api/v4/{endpoint}"
        
        params = {
            'created_after': start_date,
            'created_before': end_date,
            'scope': 'all',
            'per_page': per_page,
            'page': page
        }
        
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        
        items = response.json()
        
        if not items:
            break
        
        all_items.extend(items)
        
        # Check if there are more pages
        if 'x-next-page' not in response.headers or not response.headers['x-next-page']:
            break
        
        page += 1
    
    return all_items


# FOR DEBUG
if __name__ == '__main__':
    print (f"call {get_items_by_year('mr', 2018)=}")