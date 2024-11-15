import requests
import json
import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini')

api_key = config.get('ticketmaster', 'api')

# Define the API endpoint for searching events
url = 'https://app.ticketmaster.com/discovery/v2/events.json'

# Define the parameters for the API request
params = {
    'countryCode': 'US',  # Correct city name (Greater Boston Area assumed)
    'apikey': api_key  # Your API key
}

# Send the GET request to the Ticketmaster API
response = requests.get(url, params=params)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Create the "data" folder if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Save the response data to a file called "data.json"
    with open('../data/data.json', 'w') as f:
        json.dump(response.json(), f, indent=4)
    
    print("Data has been saved to 'data/data.json'")
else:
    print(f"Error: Unable to fetch data. Status code {response.status_code}")
    print(response.text)  # Print the response text for more details
