import os
import requests

# === CONFIGURATION ===
API_TOKEN = os.getenv('API_TOKEN')  # Read API token from environment variable
BASE_URL = os.getenv('BASE_URL', 'https://poc.polaris.blackduck.com/api')  # Default value if not set
APPLICATION_NAME = os.getenv('APPLICATION_NAME', 'Default-App-Name')  # Default value if not set
PROJECT_NAME = os.getenv('PROJECT_NAME', 'Default-Project-Name')  # Default value if not set
NOTES = os.getenv('NOTES', 'Default Notes')  # Default value if not set

# === HEADERS ===
headers = {
    'Api-token': API_TOKEN,
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/json'
}

# === STEP 1: Get Portfolio ID ===
def get_portfolio_id():
    url = f'{BASE_URL}/portfolios'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    portfolios = response.json().get('_items', [])
    if portfolios:
        return portfolios[0]['id']  # Use the first portfolio found
    return None

# === STEP 2: Get Application ID ===
def get_application_id(portfolio_id):
    offset = 0
    limit = 100
    while True:
        url = f'{BASE_URL}/portfolios/{portfolio_id}/applications?_offset={offset}&_limit={limit}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        applications = response.json().get('_items', [])
        for app in applications:
            if app['name'] == APPLICATION_NAME:
                return app['id']
        if len(applications) < limit:
            break  # No more pages
        offset += limit
    return None

# === STEP 3: Get Project ID ===
def get_project_id(portfolio_id, application_id):
    url = f'{BASE_URL}/portfolios/{portfolio_id}/applications/{application_id}/projects'
    params = {
        '_includeLabelIds': 'true'
    }
    headers.update({'accept': 'application/vnd.polaris.portfolios.projects-1+json'})  # Update headers
    response = requests.get(url, headers=headers, params=params)  # Add query parameters
    response.raise_for_status()
    projects = response.json().get('_items', [])
    for project in projects:
        if project['name'] == PROJECT_NAME:
            return project['id']
    print(f'No project found with name: {PROJECT_NAME}')
    return None

# === STEP 4: Get Profile ID ===
def get_profile_id(portfolio_id, application_id, project_id):
    url = f'{BASE_URL}/portfolios/{portfolio_id}/applications/{application_id}/projects/{project_id}'
    headers.update({'accept': 'application/vnd.polaris.portfolios.projects-1+json'})  # Update headers
    response = requests.get(url, headers=headers)
    
    # Handle non-200 responses
    if response.status_code != 200:
        print("Error: Received non-200 response.")
        return None

    # Extract profile ID from the response
    try:
        project_data = response.json()
        profile = project_data.get('profile', {})
        profile_id = profile.get('id')
        if profile_id:
            return profile_id
        else:
            print("No profile found in the project.")
            return None
    except requests.exceptions.JSONDecodeError:
        return None
    return None

# === STEP 5: Kick off Fast Web App Test ===
def kick_off_fast_web_app_test(portfolio_id, application_id, project_id, profile_id):
    url = f'{BASE_URL}/tests'
    payload = {
        "applicationId": application_id,
        "projectId": project_id,
        "notes": NOTES,
        "assessmentTypes": ["DAST"],
        "testMode": "DAST_WEBAPP",
        "scanMode": "DYNAMIC_TEST",
        "profileDetails": {
            "id": profile_id
        }
    }
    headers = {
        'Api-Token': API_TOKEN,  # Correct header key
        'Accept': 'application/vnd.polaris.tests.tests-bulk-1+json',  # Correct Accept header
        'Content-Type': 'application/vnd.polaris.tests.tests-bulk-create-1+json'  # Correct Content-Type header
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# === MAIN EXECUTION ===
if __name__ == '__main__':
    portfolio_id = get_portfolio_id()
    if portfolio_id:
        print(f'Portfolio ID: {portfolio_id}')
        app_id = get_application_id(portfolio_id)
        if app_id:
            print(f'Application ID: {app_id}')
            proj_id = get_project_id(portfolio_id, app_id)  # Pass both arguments
            if proj_id:
                print(f'Project ID: {proj_id}')
                profile_id = get_profile_id(portfolio_id, app_id, proj_id)  # Pass all three arguments
                if profile_id:
                    print(f'Profile ID: {profile_id}')
                    test_response = kick_off_fast_web_app_test(portfolio_id, app_id, proj_id, profile_id)
                    # Extract the test URL from the response
                    test_url = test_response['responses'][0]['body']['_links'][0]['href']
                    print(f'Test successfully kicked off, URL: {test_url}')
                else:
                    print('No profile associated with the project.')
            else:
                print('Project not found.')
        else:
            print('Application not found.')
    else:
        print('Portfolio not found.')
