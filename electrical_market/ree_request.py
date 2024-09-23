import requests

# Function connection to  API
def get_data_from_api(url):
    
    # API Key (obtained by REE) 
    api_key = "fbfd13345575ac521663e367df30483d271e0a8cab8fc83ff0d61607754ddf17"     
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None