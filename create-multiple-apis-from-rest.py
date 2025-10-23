import requests
import json
import urllib3
from time import sleep
import base64

# ==================== Configuration Variables ====================
NAME_PREFIX = 'xxs'
START_NUMBER = 2
COUNT = 20
USERNAME = 'admin'
PASSWORD = 'admin'
BASE_URL = 'https://localhost:9443/api/am/publisher/v4/apis'
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
    Create a single API using the REST API endpoint
    
    Args:
        api_name: Name of the API to create
        auth_header: Basic authentication header value
        
    Returns:
        tuple: (success: bool, response: dict or None)
    """
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header
    }
    
    payload = {
        "name": api_name,
        "description": "This is a simple API for Pizza Shack online pizza delivery store.",
        "context": api_name,
        "version": "1.0.0",
        "provider": "admin",
        "lifeCycleStatus": "CREATED",
        "responseCachingEnabled": False,
        "hasThumbnail": False,
        "isDefaultVersion": False,
        "enableSchemaValidation": False,
        "type": "HTTP",
        "transport": [
            "http",
            "https"
        ],
        "tags": [
            "substract",
            "add"
        ],
        "policies": [
            "Unlimited"
        ],
        "apiThrottlingPolicy": "Unlimited",
        "securityScheme": ["oauth2"],
        "maxTps": {
            "production": 1000,
            "sandbox": 1000
        },
        "visibility": "PUBLIC",
        "visibleRoles": [],
        "visibleTenants": [],
        "subscriptionAvailability": "CURRENT_TENANT",
        "additionalProperties": [
            {
                "name": "AdditionalProperty",
                "value": "PropertyValue",
                "display": True
            }
        ],
        "accessControl": "NONE",
        "businessInformation": {
            "businessOwner": "John Doe",
            "businessOwnerEmail": "johndoe@wso2.com",
            "technicalOwner": "Jane Roe",
            "technicalOwnerEmail": "janeroe@wso2.com"
        },
        "endpointConfig": {
            "endpoint_type": "http",
            "sandbox_endpoints": {
                "url": "https://localhost:9443/am/sample/pizzashack/v1/api/"
            },
            "production_endpoints": {
                "url": "https://localhost:9443/am/sample/pizzashack/v1/api/"
            }
        },
        "operations": [
            {
                "target": "/order/{orderId}",
                "verb": "POST",
                "authType": "Application & Application User",
                "throttlingPolicy": "Unlimited"
            },
            {
                "target": "/menu",
                "verb": "GET",
                "authType": "Application & Application User",
                "throttlingPolicy": "Unlimited"
            }
        ]
    }
    
    try:
        response = requests.post(
            BASE_URL,
            headers=headers,
            json=payload,
            verify=False  # Set to True in production with proper SSL cert
        )
        
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, {
                'status_code': response.status_code,
                'error': response.text
            }
            
    except requests.exceptions.RequestException as e:
        return False, {'error': str(e)}

def main():
    """Main execution function"""
    
    print('=' * 50)
    print('API Creation Script Started')
    print(f'Name Prefix: {NAME_PREFIX}')
    print(f'Start Number: {START_NUMBER}')
    print(f'Total Count: {COUNT}')
    print(f'Authentication: Basic Auth ({USERNAME})')
    print('=' * 50)
    
    # Generate Basic Auth header
    auth_header = get_basic_auth_header(USERNAME, PASSWORD)
    print(f'Auth Header: {auth_header}')
    print('=' * 50)
    
    success_count = 0
    fail_count = 0
    failed_apis = []
    
    for i in range(COUNT):
        current_number = START_NUMBER + i
        api_name = f'{NAME_PREFIX}{current_number}'
        
        print(f'{i + 1}/{COUNT}', end=' - ', flush=True)
        
        success, response = create_api(api_name, auth_header)
        
        if success:
            success_count += 1
            api_id = response.get('id', 'N/A')
            print(f'✅ Created: {api_name} (ID: {api_id})')
        else:
            fail_count += 1
            failed_apis.append(api_name)
            error_msg = response.get('error', 'Unknown error')
            status_code = response.get('status_code', 'N/A')
            print(f'❌ Failed: {api_name} (Status: {status_code})')
            print(f'   Error: {error_msg}')
        
        # Small delay to avoid overwhelming the server (optional)
        if i < COUNT - 1:  # Don't sleep after the last iteration
            sleep(0.5)
    
    print('=' * 50)
    print('✅ Script Completed!')
    print(f'Total APIs: {COUNT}')
    print(f'Successful: {success_count}')
    print(f'Failed: {fail_count}')
    
    if failed_apis:
        print('\nFailed APIs:')
        for api in failed_apis:
            print(f'  - {api}')
    
    print('=' * 50)

if __name__ == '__main__':
    main()