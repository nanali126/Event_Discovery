import json

# Sample data (replace this with the actual data you have)
with open('../data/processed_event_kpis.json', 'r') as f:
    events_data = json.load(f)

# Define weight factors for KPI and price difference
w1 = 0.8  # Weight for KPI
w2 = 0.2  # Weight for price difference

# Function to extract prices with error handling
def extract_prices(price_range):
    try:
        # Check if price_range matches the expected format
        if price_range and 'Budget Range' in price_range:
            price_min = float(price_range.split('$')[1].split('-')[0].strip())
            price_max = float(price_range.split('$')[1].split('-')[1].strip())
            return price_min, price_max
        else:
            raise ValueError(f"Invalid price range format: {price_range}")
    except Exception as e:
        print(f"Error parsing price range: {price_range} ({e})")
        return 0, 0  # Default values in case of error

def calculate_event_score(event):
    # Extract relevant data with defaults for missing keys
    kpi = event.get('kpi', 0)
    price_range = event.get('budget_constraints', 'Budget Range: $0.0 - $0.0')

    # Extract price min and max
    price_min, price_max = extract_prices(price_range)

    # Calculate KPI component
    kpi_score = kpi

    # Calculate price difference component
    price_diff = price_max - price_min

    # Calculate the overall event score without relevance
    event_score = (w1 * kpi_score) + (w2 * price_diff)
    
    return event_score

# Sort events by calculated score
sorted_events = sorted(events_data['events'], key=calculate_event_score, reverse=True)

# Select the top 10 events
top_10_events = sorted_events[:10]

# Save the top 10 events to a new json file
with open('top_10_events.json', 'w') as outfile:
    json.dump(top_10_events, outfile, indent=4)

print("Top 10 events have been saved to 'top_10_events.json'")
