import json
import logging
import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess

# Set debug mode
logging.basicConfig(level=logging.DEBUG)

# Function to load event details from file
def load_event_details(file_path="/home/administrator/empirestate/empirestate-light-display/event_details.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

# Function to export event details to a file
def export_event_details(event_details, file_path="/home/administrator/empirestate/empirestate-light-display/event_details.json"):
    with open(file_path, "w") as file:
        json.dump(event_details, file)

# Function to check for changes and run display script if needed
def check_and_run_display():
    # Set URL of the Empire State Building tower lights calendar
    url = "https://www.esbnyc.com/about/tower-lights/calendar"

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find today's event info
        todays_date = datetime.now()
        event_info = soup.find('div', class_='day--day', string=todays_date.strftime("%d"))

        if event_info:
            # If there's an event today, compare with existing event details
            lights = event_info.find_next('div', class_='name').text.strip()
            event_description = event_info.find_next('div', class_='field_description').text.strip()
            event_description = event_description.replace("Description:", "").strip()

            event_details_new = {
                "date": todays_date.strftime("%Y-%m-%d"),
                "lights": lights,
                "event_description": event_description
            }

            event_details_old = load_event_details()

            # Compare event details
            if event_details_old != event_details_new:
                # If there's a change, update event details file and run display script
                export_event_details(event_details_new)
                logging.info("Event details have changed. Running display script.")
                # Run display script
                display_script_path = "/home/administrator/empirestate/empirestate-light-display/empirestate_display.py"
                subprocess.run(["python3", display_script_path])
            else:
                logging.info("No change in event details.")
        else:
            logging.info("No event found for today.")
    else:
        logging.error("Failed to retrieve data from the website.")

if __name__ == "__main__":
    check_and_run_display()
