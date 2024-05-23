#!/usr/bin/env python3

import json
import logging
import requests
import os
import time
import subprocess
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in26

## Define Variables
# Define font paths
font_path = "/usr/share/fonts/opentype/cantarell/Cantarell-Bold.otf"
bold_font_path = "/usr/share/fonts/opentype/cantarell/Cantarell-Bold.otf"
# Define font sizes
font_size = 32
bold_font_size = 32
# URL of the Empire State Building tower lights calendar
url = "https://www.esbnyc.com/about/tower-lights/calendar"


# Set debug mode for WaveShare EPD
logging.basicConfig(level=logging.DEBUG)

# Function: Sync system time with NTP servers
def sync_ntp_time():
    try:
        subprocess.run(["sudo", "ntpdate", "-s", "time.nist.gov"])
        print("System time synchronized with NTP servers.")
    except Exception as e:
        print("Error synchronizing system time:", e)

# Function to manually set the date for testing
def set_test_date():
    # Uncomment the line below and set the desired test date (YYYY, MM, DD) for testing
    #return datetime(year=2024, month=4, day=12)
    return None  # Comment out this line if you set a test date above

# Call the set_test_date function to manually set the test date
test_date = set_test_date()

# If test date is set, use it for testing
if test_date:
    todays_date = test_date
else:
    # If test date is not set, sync system time with NTP servers and set today's date
    sync_ntp_time()
    time.sleep(5)
    todays_date = datetime.now()

# Function to export event details to a file
def export_event_details(event_details, file_path="event_details.json"):
    with open(file_path, "w") as file:
        json.dump(event_details, file)

# Function to load event details from a file
def load_event_details(file_path="event_details.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None

# Define wrap_text function
def wrap_text(draw, text, width, font):
    """Wrap text to fit within a given width."""
    wrapped_lines = []
    if draw.textbbox((0, 0), text, font=font)[2] <= width:
        return [text]
    words = text.split()
    wrapped_line = ''
    for word in words:
        if draw.textbbox((0, 0), wrapped_line + word, font=font)[2] <= width:
            wrapped_line += word + ' '
        else:
            wrapped_lines.append(wrapped_line.strip())
            wrapped_line = word + ' '
    wrapped_lines.append(wrapped_line.strip())
    return wrapped_lines

try:
    # Initialize e-ink display
    logging.info("Initializing e-ink display")
    epd = epd4in26.EPD()
    epd.init()

    # Define font
    font = ImageFont.truetype(font_path, font_size)
    bold_font = ImageFont.truetype(bold_font_path, bold_font_size)

    # Initialize image and draw
    width, height = epd.width, epd.height
    image = Image.new("1", (width, height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    # Create directory if it doesn't exist
    directory = '/home/administrator/empirestate'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the path to the event details file
    event_details_file = '/home/administrator/empirestate/event_details.json'

    # Check if the file exists, if not, create it
    if not os.path.exists(event_details_file):
        try:
            # Create the file with write permissions for the owner
            with open(event_details_file, 'w') as f:
                pass
            # Set file permissions to 644
            os.chmod(event_details_file, 0o644)
        except Exception as e:
            print(f"Failed to create {event_details_file}: {e}")

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the event info for today
        event_info = soup.find('div', class_='day--day', string=todays_date.strftime("%d"))

        # Clear the display and wait 5 seconds
        epd.Clear()
        time.sleep(5)

        if event_info:
            # If there is an event today, print the details
            lights = event_info.find_next('div', class_='name').text.strip()
            event_description = event_info.find_next('div', class_='field_description').text.strip()

            # Remove leading and trailing whitespace from event description
            event_description = event_description.replace("Description:", "").strip()

            # Calculate text dimensions
            date_text = todays_date.strftime("%A, %B ") + str(todays_date.day)
            lights_text = "Lights: " + lights
            event_description_text = "Description: " + event_description

            # Debug information
            print("Event found for today:")
            print("Date:", date_text)
            print("Lights:", lights_text)
            print("Event Description:", event_description_text)

            # Export event details to a file
            event_details = {
                "date": todays_date.strftime("%Y-%m-%d"),
                "lights": lights,
                "event_description": event_description
            }
            export_event_details(event_details, event_details_file)

            # Load the background image for days with an event
            background_image_path = "/home/administrator/empirestate/media/empirestatespire.png"
            background_image = Image.open(background_image_path)
            background_image = background_image.resize((width, height), Image.LANCZOS)

            # Create a new image to draw text over the loaded background image
            final_image = Image.new("1", (width, height), 255)  # 255: clear the frame
            final_image.paste(background_image, (0, 0))

            # Initialize draw
            draw = ImageDraw.Draw(final_image)

            # Calculate text dimensions
            date_text_width, date_text_height = draw.textbbox((0, 0), date_text, font=font)[2:]

            # Draw today's date on the upper left corner
            draw.text((20, 20), date_text, font=bold_font, fill=0)

            ## Draw underline below today's date ##
            underline_y = 20 + date_text_height - 5
            draw.line((20, underline_y, 20 + date_text_width, underline_y), fill=0, width=2)

            ## Add a blank line after the underline ##
            y_position = underline_y + 10

            ## Draw a blank line ##
            draw.text((20, y_position), "", font=font, fill=0)

            ## Adjust y_position to add a blank line above the lights description ##
            y_position += font.getbbox(" ")[3] // 2

            ## Combine "Lights:" title and lights description with a space ##
            lights_text = "Lights: " + lights

            # Calculate wrap width for lights text
            lights_wrap_width = (width * 7 // 10)

            # Calculate starting y-position for light text
            lights_start_y = y_position

            # Calculate starting x-position for light text
            lights_start_x = 20

            # Draw light text with the predefined font size
            lights_lines = wrap_text(draw, lights_text, lights_wrap_width, font)
            max_line_height = max(draw.textbbox((0, 0), line, font=font)[3] for line in lights_lines)  # Calculate the maximum line height
            line_spacing = -5.0  # Adjust the line spacing as needed
            for line in lights_lines:
                draw.text((lights_start_x, lights_start_y), line, font=font, fill=0)
                lights_start_y += max_line_height + line_spacing  # Use the maximum line height for consistent spacing
            
            ## Adjust y_position to add a blank line after the lights description ##
            y_position = max(y_position + font.getbbox(" ")[3], lights_start_y) + 10

            ## Draw a blank line ##
            draw.text((20, y_position), "", font=font, fill=0)

            ## Adjust y_position to add a blank line after the lights description ##
            y_position += font.getbbox(" ")[3] // 2

            ## Combine "Description:" title and event description ##
            event_description_text = "Description: " + event_description

            # Calculate wrap width for event description text
            event_description_wrap_width = (width * 7 // 10)  # 70% of the screen width

            # Draw event description text with the predefined font size
            event_description_lines = wrap_text(draw, event_description_text, event_description_wrap_width, font)
            max_line_height = max(draw.textbbox((0, 0), line, font=font)[3] for line in event_description_lines)  # Calculate the maximum line height
            for line in event_description_lines:
                draw.text((20, y_position), line, font=font, fill=0)
                y_position += max_line_height + line_spacing  # Use the maximum line height for consistent spacing
            
            # Display the final image
            logging.info("Displaying image on display")
            epd.display(epd.getbuffer(final_image))
        else:
            # If there is no event today, show the new image with "No events today" message

            # Load the new image
            new_image_path = "/home/administrator/empirestate/media/empirestateskyline.png"
            new_image = Image.open(new_image_path)
            new_image = new_image.resize((width, height), Image.LANCZOS)

            # Create a new image to draw text over the loaded image
            final_image = Image.new("1", (width, height), 255)  # 255: clear the frame
            final_image.paste(new_image, (0, 0))

            # Initialize draw
            draw = ImageDraw.Draw(final_image)

            # Calculate text dimensions for today's date
            date_text = todays_date.strftime("%A, %B ") + str(todays_date.day)
            date_text_width, date_text_height = draw.textbbox((0, 0), date_text, font=font)[2:]

            # Draw today's date on the upper left corner
            draw.text((width - date_text_width - 30, 10), date_text, font=bold_font, fill=0)

            # Draw underline below today's date
            underline_y = 10 + date_text_height
            draw.line((width - date_text_width - 30, underline_y, width - 30, underline_y), fill=0, width=2)

            # Draw "No events today" text below today's date
            no_events_text = "Signature White"
            text_width, text_height = draw.textbbox((0, 0), no_events_text, font=font)[2:]
            draw.text((width - text_width - 30, underline_y + 10), no_events_text, font=font, fill=0)

            # Display the final image
            logging.info("Displaying image on display")
            epd.display(epd.getbuffer(final_image))

    else:
        print("Failed to retrieve data from the website.")

    # Sleep
    logging.info("Powering off the display")
    epd.sleep()

except Exception as e:
    error_message = "An error has occurred. Please power-cycle the device.\nSystem will attempt an auto repair overnight.\n"
    error_reason = f"Error: {e}"
    print(error_reason)
    print(error_message)
    logging.error(error_reason)

    try:
        # Display error message on the e-ink display
        error_image = Image.new("1", (width, height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(error_image)
        error_font_size = 24
        bold_font = ImageFont.truetype(bold_font_path, error_font_size)
        message_width, message_height = draw.textbbox((0, 0), error_message, font=bold_font)[2:]
        reason_width, reason_height = draw.textbbox((0, 0), error_reason, font=bold_font)[2:]
        draw.text(((width - message_width) // 2, (height - message_height) // 2 - 20), error_message, font=bold_font, fill=0)
        draw.text(((width - reason_width) // 2, (height - reason_height) // 2 + 20), error_reason, font=bold_font, fill=0)
        epd.display(epd.getbuffer(error_image))
        # Sleep for a while before putting the display to sleep
        time.sleep(5)
    except:
        pass  # Ignore any errors that occur during error message display
    finally:
        # Put the display to sleep
        logging.info("Powering off the display due to error")
        epd.sleep()
