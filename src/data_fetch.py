import requests
import json

# Set your Eventbrite Organization ID and Personal OAuth Token
organization_id = 'YOUR_ORG_ID'  # Replace with your Eventbrite organization ID
personal_oauth_token = 'YOUR_OAUTH_TOKEN'  # Replace with your Eventbrite personal OAuth token

# Eventbrite API URL
url = f'https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/?status=ended'

# Set headers for the request
headers = {
    'Authorization': f'Bearer {personal_oauth_token}'
}

# Function to fetch data from Eventbrite API
def fetch_eventbrite_data():
    # Send GET request to Eventbrite API
    response = requests.get(url, headers=headers)

    # Check if request was successful
    if response.status_code == 200:
        data = response.json()  # Parse the response JSON
        return data
    else:
        print(f"Error fetching data from Eventbrite API: {response.status_code}")
        return None

# Fetch event data
event_data = fetch_eventbrite_data()

# If data was fetched successfully, save to a JSON file
if event_data:
    with open('../data/data.json', 'w') as json_file:
        json.dump(event_data, json_file, indent=4)

    print("Event data has been saved to '../data/data.json'")
