import json
import re

# Function to calculate KPI
def calculate_kpi(ticket_limit_info, price_range):
    # Use a regular expression to extract the number from the ticket limit info string
    match = re.search(r'\d+', ticket_limit_info)  # Find the first number in the string
    if match:
        ticket_limit = match.group()
        print(ticket_limit)
        ticket_limit = int(ticket_limit) 
        # Extract the number as an integer
    else:
        ticket_limit = 0  # Default to 0 if no number is found
    
    # Extract min and max ticket prices
    min_price = price_range.get('min', 0)
    max_price = price_range.get('max', 0)
    
    # Calculate the mean ticket price
    mean_price = (min_price + max_price) / 2 if min_price and max_price else 0
    
    # Calculate KPI: 80% of ticket limit * mean ticket price
    kpi = 0.80 * ticket_limit * mean_price
    return kpi

# Function to process each event and write the output to a new JSON
def process_events(original_data):
    events_data = {
        "events": []
    }

    for event in original_data["_embedded"]["events"]:
        # Extract the necessary information
        event_name = event["name"]
        event_url = event["url"]
        ticket_limit_info = event.get("ticketLimit", {}).get("info", "")
        price_range = event["priceRanges"][0] if event["priceRanges"] else {}

        # Calculate KPI
        kpi = calculate_kpi(ticket_limit_info, price_range)
        
        # Infer target audience based on the event's classification
        target_audience = infer_target_audience(event)
        
        # Infer objectives based on the event's genre (e.g., brand awareness for sports)
        objectives = infer_objectives(event)
        
        # Infer industry category based on the event's classification
        industry_category = infer_industry_category(event)
        
        # Extract geographic focus (city and state of the venue)
        venue_info = event["_embedded"]["venues"][0]
        geographic_focus = {
            "city": venue_info["city"]["name"],
            "state": venue_info["state"]["name"]
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
        
        # Add the new event to the list
        events_data["events"].append(new_event)

    return events_data

# Function to infer the target audience from the event's classification
def infer_target_audience(event):
    if event["classifications"]:
        genre = event["classifications"][0].get("genre", {}).get("name", "")
        if genre:
            return f"Fans of {genre}"
    return "General Audience"

# Function to infer the objectives of the event
def infer_objectives(event):
    if event["classifications"]:
        genre = event["classifications"][0].get("genre", {}).get("name", "")
        if genre:
            if "Hockey" in genre:
                return "Brand Awareness for NHL Fans"
            return "General Entertainment"
    return "General Objective"

# Function to infer the industry category from the event's classification
def infer_industry_category(event):
    if event["classifications"]:
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

# Function to write the processed events data into a new JSON file
def write_to_file(events_data, output_file):
    with open(output_file, 'w') as f:
        json.dump(events_data, f, indent=4)
    print(f"Data has been written to '{output_file}'")

# Main execution
if __name__ == "__main__":
    # Load the original JSON data from a file (change the path as needed)
    file_path = '../data/data.json'  # Modify the path as needed
    with open(file_path, 'r') as f:
        original_data = json.load(f)

    # Process the events and generate the new JSON data
    events_data = process_events(original_data)

    # Write the processed data into a new JSON file
    write_to_file(events_data, '../data/processed_event_kpis.json')
