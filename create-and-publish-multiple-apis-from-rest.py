import requests
import json
import urllib3
from time import sleep

# ==================== Configuration Variables ====================
NAME_PREFIX = 'pro'
START_NUMBER = 2
COUNT = 5
BEARER_TOKEN = 'xxx'  # Replace with your actual token
BASE_URL = 'https://localhost:9443/api/am/publisher/v4'
# ================================================================

# Disable SSL warnings for localhost (remove in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_api(api_name, token):
    """
    Step 1: Create API
    
    Args:
        api_name: Name of the API to create
        token: Bearer token for authentication
        
    Returns:
        tuple: (success: bool, api_id: str or None, error: str or None)
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
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

def create_revision(api_id, token):
    """
    Step 2: Create API Revision
    
    Args:
        api_id: ID of the created API
        token: Bearer token for authentication
        
    Returns:
        tuple: (success: bool, revision_id: str or None, error: str or None)
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
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

def deploy_revision(api_id, revision_id, token):
    """
    Step 3: Deploy API Revision
    
    Args:
        api_id: ID of the API
        revision_id: ID of the revision
        token: Bearer token for authentication
        
    Returns:
        tuple: (success: bool, error: str or None)
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
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

def publish_api(api_id, token):
    """
    Step 4: Publish API (Change lifecycle to Publish)
    
    Args:
        api_id: ID of the API
        token: Bearer token for authentication
        
    Returns:
        tuple: (success: bool, error: str or None)
    """
    
    headers = {
        'Authorization': f'Bearer {token}',
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

def create_and_publish_api(api_name, token):
    """
    Complete workflow: Create, Revise, Deploy, and Publish API
    
    Args:
        api_name: Name of the API to create
        token: Bearer token for authentication
        
    Returns:
        tuple: (success: bool, details: dict)
    """
    
    # Step 1: Create API
    success, api_id, error = create_api(api_name, token)
    if not success:
        return False, {'step': 'create', 'error': error}
    
    # Step 2: Create Revision
    success, revision_id, error = create_revision(api_id, token)
    if not success:
        return False, {'step': 'revision', 'error': error, 'api_id': api_id}
    
    # Step 3: Deploy Revision
    success, error = deploy_revision(api_id, revision_id, token)
    if not success:
        return False, {'step': 'deploy', 'error': error, 'api_id': api_id}
    
    # Step 4: Publish API
    success, error = publish_api(api_id, token)
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
    print('=' * 60)
    
    if BEARER_TOKEN == '<your-token-here>':
        print('❌ ERROR: Please set your BEARER_TOKEN in the script!')
        return
    
    success_count = 0
    fail_count = 0
    failed_apis = []
    
    for i in range(COUNT):
        current_number = START_NUMBER + i
        api_name = f'{NAME_PREFIX}{current_number}'
        
        print(f'{i + 1}/{COUNT}', end=' - ', flush=True)
        
        success, details = create_and_publish_api(api_name, BEARER_TOKEN)
        
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