#Event Discovery Project
This project is designed to fetch event data from the Ticketmaster API, process the data to calculate Key Performance Indicators (KPIs) and event scores, and finally output the top 10 events into a CSV file for easy analysis.

##Overview
Due to limitations in the Ticketmaster API, reliable KPIs are not readily available. To address this, KPIs are calculated based on the venue capacity and ticket prices. The event score is then computed using the KPI, price difference, and relevance score, allowing for a ranked list of top events.



##Usage
1. Fetching Data
Run the data_fetch.py script to fetch event data from the Ticketmaster API.

2. Event Discovery
Run the event_discovery.py script to process the data and generate the top 10 events.



##Event Score Calculation
The event score is calculated using the following formula:

Event Score = (0.6 * KPI) + (0.3 * Price Difference) + (0.1 * Relevance Score)
KPI (60% weight): Indicates the potential revenue based on venue capacity and ticket prices.

Price Difference (30% weight): The difference between the maximum and minimum ticket prices.

Relevance Score (10% weight): Assesses how closely the target audience aligns with the event objectives.
KPI Definition
Due to the limitations of the Ticketmaster API, the KPI is defined as:
KPI = 80% * Venue Capacity * Mean Ticket Price

Venue Capacity: Obtained via the OpenAI API by querying the capacity of each venue.

Mean Ticket Price: Calculated as the average of the maximum and minimum ticket prices provided by the Ticketmaster API.

80% Factor: Assumes that 80% of the venue capacity will be filled, providing a conservative estimate of potential revenue.



##API Keys Management
Current Approach: API keys for OpenAI and Ticketmaster are stored in the config.ini file.
Future Improvements: Plan to use more secure methods like environment variables or GitHub Secrets to store API keys, enhancing security and compliance.



##Limitations and Future Work
Data Size: Currently limited due to the Ticketmaster API rate limits, resulting in a smaller dataset.
Future Solution: Implement methods to handle rate limiting or use batch processing to fetch more data over time.

API Key Security: While API keys are stored in a config file now, future development will focus on more secure storage solutions.

Venue Capacity Accuracy: The capacity is fetched using the OpenAI API, which may not always return accurate results.
Future Solution: Implement caching for venue capacities or use a more reliable data source.

Error Handling: The scripts have basic error handling.
Future Enhancements: Improve error logging and handling to make the scripts more robust.


Contact
For any questions or suggestions, please contact kejiali@brandeis.edu.

