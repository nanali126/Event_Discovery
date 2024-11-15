import json
import openai
import re
import csv
import configparser
import os

config = configparser.ConfigParser()
config.read('config.ini')

openai.api_key = config.get('openai', 'api_key')

# Define weight factors for KPI, price difference, and relevance score
w1 = 0.6  # Weight for KPI
w2 = 0.3  # Weight for price difference
w3 = 0.1  # Weight for relevance score

# Function to get the venue capacity from OpenAI API
def get_venue_capacity(venue_name, venue_city, venue_state):
    prompt = f"Can you provide the seating capacity of {venue_name} in {venue_city}, {venue_state}?"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{
            "role": "system", 
            "content": "You are a helpful assistant."
        }, {
            "role": "user",
            "content": prompt
        }],
    )
    
    # Extract the capacity from the OpenAI response
    capacity_text = response['choices'][0]['message']['content'].strip()

    try:
        capacity = int(re.search(r'\d+', capacity_text.replace(',', '')).group())
    except AttributeError:
        capacity = 0  
    
    return capacity

# Function to calculate KPI using venue capacity instead of ticket limit
def calculate_kpi(venue_name, venue_city, venue_state, price_range):
    # Get the venue capacity from OpenAI API
    venue_capacity = get_venue_capacity(venue_name, venue_city, venue_state)
    
    min_price = price_range.get('min', 0)
    max_price = price_range.get('max', 0)

    mean_price = (min_price + max_price) / 2 if min_price and max_price else 0
    
    # Calculate KPI: 80% of venue capacity * mean ticket price
    kpi = 0.80 * venue_capacity * mean_price
    return round(kpi, 2)

# Function to infer the target audience from the event's classification
def infer_target_audience(event):
    if event.get("classifications"):
        genre = event["classifications"][0].get("genre", {}).get("name", "")
        if genre:
            return f"Fans of {genre}"
    return "General Audience"

# Function to infer the objectives of the event
def infer_objectives(event):
    if event.get("classifications"):
        genre = event["classifications"][0].get("genre", {}).get("name", "")
        segment = event["classifications"][0].get("segment", {}).get("name", "")

        # Define objectives based on genre or segment
        if "Hockey" in genre:
            return "Brand Awareness for NHL Fans"
        elif "Sports" in genre:
            return "Engagement for Sports Fans"
        elif "Music" in genre:
            return "Entertainment and Enjoyment for Music Lovers"
        elif "Theater" in genre:
            return "Cultural Engagement and Artistic Expression"
        elif "Charity" in segment:
            return "Fundraising for a Cause"
        elif "Education" in segment:
            return "Learning and Knowledge Sharing"
        else:
            return "General Entertainment"
    
    return "General Objective"

# Function to infer the industry category from the event's classification
def infer_industry_category(event):
    if event.get("classifications"):
        segment = event["classifications"][0].get("segment", {}).get("name", "")
        if segment:
            return segment
    return "General"

# Function to infer budget constraints from the ticket prices
def infer_budget_constraints(price_range):
    min_price = price_range.get("min", 0)
    max_price = price_range.get("max", 0)
    if min_price and max_price:
        return f"Budget Range: ${min_price} - ${max_price}"
    return "Unknown Budget"

# Function to get relevance score using OpenAI API
def get_relevance_score(target_audience, objectives):
    prompt = f"Is the target audience '{target_audience}' closely related to the objectives '{objectives}'? Answer with 1 for strong relation, 0.5 for mutual relation, and 0 for no relation. Return the number only."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10
    )

    try:
        relevance_score = float(response['choices'][0]['message']['content'].strip())
    except ValueError:
        relevance_score = 0.5  # Default to mutual if parsing fails
    
    return relevance_score

# Function to calculate event score
def calculate_event_score(event):
    # Extract relevant data
    kpi = event.get("kpi", 0)
    price_range = event.get("budget_constraints", "")
    target_audience = event.get("target_audience", "General Audience")
    objectives = event.get("objectives", "General Objective")
    
    price_min = 0
    price_max = 0

    if price_range and "Budget Range:" in price_range:
        prices = re.findall(r'\$\s*([\d\.]+)', price_range)
        
        if len(prices) == 2:
            try:
                price_min = float(prices[0])
                price_max = float(prices[1])
            except ValueError:
                print(f"Error parsing price range for event '{event['name']}': Invalid numeric value")
        else:
            print(f"Error parsing price range for event '{event['name']}': Invalid format")
    
    # Calculate price difference
    price_diff = price_max - price_min
    
    relevance_score = get_relevance_score(target_audience, objectives)
    event_score = (w1 * kpi) + (w2 * price_diff) + (w3 * relevance_score)
    
    return event_score

# Function to process each event and prepare for scoring
def process_events(original_data):
    events_data = {
        "events": []
    }

    for event in original_data["_embedded"]["events"]:
        event_name = event.get("name", "Unknown Event")
        event_url = event.get("url", "")
        price_range = event["priceRanges"][0] if event.get("priceRanges") else {}

        venue_info = event["_embedded"]["venues"][0] if event.get("_embedded") else {}
        venue_name = venue_info.get("name", "Unknown Venue")
        venue_city = venue_info.get("city", {}).get("name", "Unknown City")
        venue_state = venue_info.get("state", {}).get("name", "Unknown State")

        kpi = calculate_kpi(venue_name, venue_city, venue_state, price_range)
        
        target_audience = infer_target_audience(event)

        objectives = infer_objectives(event)
        
        industry_category = infer_industry_category(event)
        
        # Extract geographic focus (city and state of the venue)
        geographic_focus = {
            "city": venue_city,
            "state": venue_state
        }
        
        # Infer budget constraints from the min and max ticket prices
        budget_constraints = infer_budget_constraints(price_range)

        # Construct the new event object
        new_event = {
            "name": event_name,
            "url": event_url,
            "target_audience": target_audience,
            "objectives": objectives,
            "industry_category": industry_category,
            "geographic_focus": geographic_focus,
            "budget_constraints": budget_constraints,
            "kpi": kpi
        }
        
        events_data["events"].append(new_event)

    return events_data

# Function to select top 10 events based on event score and write to CSV
def select_top_10_events(events_data):
    for event in events_data['events']:
        event['event_score'] = calculate_event_score(event)
    
    sorted_events = sorted(events_data['events'], key=lambda x: x['event_score'], reverse=True)
    
    # Select the top 10 events
    top_10_events = sorted_events[:10]
    
    with open('top_10_events.json', 'w') as outfile:
        json.dump(top_10_events, outfile, indent=4)
    
    with open('../top_10_events.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Event Name', 'Event URL', 'Event Score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for event in top_10_events:
            writer.writerow({
                'Event Name': event['name'],
                'Event URL': event['url'],
                'Event Score': f"{event['event_score']:.2f}"
            })
        
        formula = f"Event Score = (0.6 * KPI) + (0.3 * Price Difference) + (0.1 * Relevance Score)"
        writer.writerow({'Event Name': '', 'Event URL': '', 'Event Score': formula})
    
    print("Top 10 events have been saved to 'top_10_events.json' and 'top_10_events.csv'")

if __name__ == "__main__":
    # Load the original JSON data from a file (change the path as needed)
    file_path = '../data/data.json'  # Modify the path as needed
    with open(file_path, 'r') as f:
        original_data = json.load(f)
    
    events_data = process_events(original_data)
    
    processed_file = '../data/processed_event_kpis.json'
    with open(processed_file, 'w') as f:
        json.dump(events_data, f, indent=4)
    print(f"Processed event data has been written to '{processed_file}'")
    
    select_top_10_events(events_data)
