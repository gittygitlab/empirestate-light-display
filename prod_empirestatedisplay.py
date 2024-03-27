## Created by Tyler Wahl with OpenAI ChatGPT
## Libraries 'requests' and 'beautifulsoup4' need to be installed first. Install scripts below:
## pip install requests
## pip install beautifulsoup4

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Set today's date
todays_date = datetime.now()

# Generate the date with suffix
def ordinal_suffix(day):
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return str(day) + suffix
# Get the day of the month with the correct ending
day_with_suffix = ordinal_suffix(todays_date.day)

# URL of the Empire State Building tower lights calendar
url = "https://www.esbnyc.com/about/tower-lights/calendar"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the event info for today
    event_info = soup.find('div', class_='day--day', string=todays_date.strftime("%d"))

    if event_info:
        # If there is an event today, print the details
        lights = event_info.find_next('div', class_='name').text.strip()
        event_description = event_info.find_next('div', class_='field_description').text.strip()

        print(todays_date.strftime("%A,"), todays_date.strftime("%B"), day_with_suffix)
        print(" Lights:", lights)
        print(" Description:", event_description)
    else:
        # If there is no event today, find the next day with an event
        next_event_date = todays_date
    
        while True:
            next_event_date += timedelta(days=1)
            current_day = next_event_date.strftime("%d")
            event_info = soup.find('div', class_='day--day', string=current_day)

            if event_info:
                lights = event_info.find_next('div', class_='name').text.strip()
                event_description = event_info.find_next('div', class_='field_description').text.strip()
                # Change the first letter of event description to lowercase
                event_description = event_description[0].lower() + event_description[1:]

                print(todays_date.strftime("%A,"), todays_date.strftime("%B"), day_with_suffix)
                print(" Lights: Signature White\n Description: There are no events scheduled for today.\n")
                print(f" The next event is {next_event_date.strftime('%A, %B %d')} {event_description}")
                break
else:
    print("Failed to retrieve data from the website.")
