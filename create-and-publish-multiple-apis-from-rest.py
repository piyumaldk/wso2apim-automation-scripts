import requests
import json
import urllib3
from time import sleep
import base64

# ==================== Configuration Variables ====================
NAME_PREFIX = 'pro'
START_NUMBER = 2
COUNT = 45
USERNAME = 'admin'
PASSWORD = 'admin'
BASE_URL = 'https://localhost:9443/api/am/publisher/v4'
# ================================================================

# Disable SSL warnings for localhost (remove in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_basic_auth_header(username, password):
    """
    Generate Basic Authentication header value
    
    Args:
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        str: Base64 encoded credentials in Basic Auth format
    """
    credentials = f'{username}:{password}'
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
    return f'Basic {encoded_credentials}'

def create_api(api_name, auth_header):
    """
    Step 1: Create API
    
    Args:
        api_name: Name of the API to create
        auth_header: Basic authentication header value
        
    Returns:
        tuple: (success: bool, api_id: str or None, error: str or None)
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    payload = {
        "name": api_name,
        "version": "1",
        "context": api_name,
        "policies": ["Unlimited"],
        "endpointConfig": {
            "endpoint_type": "http",
            "sandbox_endpoints": {
                "url": "http://localhost:3000"
            },
            "production_endpoints": {
                "url": "http://localhost:3000"
            }
        }
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/apis?openAPIVersion=v3',
            headers=headers,
            json=payload,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            api_id = response.json().get('id')
            return True, api_id, None
        else:
            return False, None, f"Status {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, None, str(e)

def create_revision(api_id, auth_header):
    """
    Step 2: Create API Revision
    
    Args:
        api_id: ID of the created API
        auth_header: Basic authentication header value
        
    Returns:
        tuple: (success: bool, revision_id: str or None, error: str or None)
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    payload = {
        "description": "Initial Revision"
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/apis/{api_id}/revisions',
            headers=headers,
            json=payload,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            revision_id = response.json().get('id')
            return True, revision_id, None
        else:
            return False, None, f"Status {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, None, str(e)

def deploy_revision(api_id, revision_id, auth_header):
    """
    Step 3: Deploy API Revision
    
    Args:
        api_id: ID of the API
        revision_id: ID of the revision
        auth_header: Basic authentication header value
        
    Returns:
        tuple: (success: bool, error: str or None)
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    payload = [
        {
            "name": "Default",
            "displayOnDevportal": True,
            "vhost": "localhost"
        }
    ]
    
    try:
        response = requests.post(
            f'{BASE_URL}/apis/{api_id}/deploy-revision?revisionId={revision_id}',
            headers=headers,
            json=payload,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            return True, None
        else:
            return False, f"Status {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, str(e)

def publish_api(api_id, auth_header):
    """
    Step 4: Publish API (Change lifecycle to Publish)
    
    Args:
        api_id: ID of the API
        auth_header: Basic authentication header value
        
    Returns:
        tuple: (success: bool, error: str or None)
    """
    
    headers = {
        'Authorization': auth_header,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/apis/change-lifecycle?action=Publish&apiId={api_id}',
            headers=headers,
            verify=False
        )
        
        if response.status_code in [200, 201]:
            return True, None
        else:
            return False, f"Status {response.status_code}: {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, str(e)

def create_and_publish_api(api_name, auth_header):
    """
    Complete workflow: Create, Revise, Deploy, and Publish API
    
    Args:
        api_name: Name of the API to create
        auth_header: Basic authentication header value
        
    Returns:
        tuple: (success: bool, details: dict)
    """
    
    # Step 1: Create API
    success, api_id, error = create_api(api_name, auth_header)
    if not success:
        return False, {'step': 'create', 'error': error}
    
    # Step 2: Create Revision
    success, revision_id, error = create_revision(api_id, auth_header)
    if not success:
        return False, {'step': 'revision', 'error': error, 'api_id': api_id}
    
    # Step 3: Deploy Revision
    success, error = deploy_revision(api_id, revision_id, auth_header)
    if not success:
        return False, {'step': 'deploy', 'error': error, 'api_id': api_id}
    
    # Step 4: Publish API
    success, error = publish_api(api_id, auth_header)
    if not success:
        return False, {'step': 'publish', 'error': error, 'api_id': api_id}
    
    return True, {'api_id': api_id, 'revision_id': revision_id}

def main():
    """Main execution function"""
    
    print('=' * 60)
    print('API Creation and Publishing Script Started')
    print(f'Name Prefix: {NAME_PREFIX}')
    print(f'Start Number: {START_NUMBER}')
    print(f'Total Count: {COUNT}')
    print(f'Authentication: Basic Auth ({USERNAME})')
    print('=' * 60)
    
    # Generate Basic Auth header
    auth_header = get_basic_auth_header(USERNAME, PASSWORD)
    print(f'Auth Header: {auth_header}')
    print('=' * 60)
    
    success_count = 0
    fail_count = 0
    failed_apis = []
    
    for i in range(COUNT):
        current_number = START_NUMBER + i
        api_name = f'{NAME_PREFIX}{current_number}'
        
        print(f'{i + 1}/{COUNT}', end=' - ', flush=True)
        
        success, details = create_and_publish_api(api_name, auth_header)
        
        if success:
            success_count += 1
            api_id = details.get('api_id', 'N/A')
            print(f'✅ Published: {api_name} (ID: {api_id})')
        else:
            fail_count += 1
            failed_apis.append({
                'name': api_name,
                'step': details.get('step', 'unknown'),
                'error': details.get('error', 'Unknown error')
            })
            step = details.get('step', 'unknown')
            print(f'❌ Failed: {api_name} (Step: {step})')
            print(f'   Error: {details.get("error", "Unknown")}')
        
        # Small delay to avoid overwhelming the server
        if i < COUNT - 1:
            sleep(0.5)
    
    print('=' * 60)
    print('✅ Script Completed!')
    print(f'Total APIs: {COUNT}')
    print(f'Successfully Published: {success_count}')
    print(f'Failed: {fail_count}')
    
    if failed_apis:
        print('\nFailed APIs Details:')
        for api in failed_apis:
            print(f'  - {api["name"]} (Failed at: {api["step"]})')
            print(f'    Error: {api["error"][:100]}...' if len(api["error"]) > 100 else f'    Error: {api["error"]}')
    
    print('=' * 60)

if __name__ == '__main__':
    main()