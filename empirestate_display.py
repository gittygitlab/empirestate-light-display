import logging
import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in26

# Set debug mode for WaveShare EPD
logging.basicConfig(level=logging.DEBUG)

# Manual input for today's date (for testing purposes)
manual_input = input("Enter today's date in YYYY-MM-DD format (leave empty for current date): ").strip()
if manual_input:
    todays_date = datetime.strptime(manual_input, "%Y-%m-%d")
else:
    todays_date = datetime.now()

# Define wrap_text function
def wrap_text(draw, text, width, font):
    """Wrap text to fit within a given width."""
    wrapped_lines = []
    if draw.textsize(text, font=font)[0] <= width:
        return [text]
    words = text.split()
    wrapped_line = ''
    for word in words:
        if draw.textsize(wrapped_line + word, font=font)[0] <= width:
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
    font_path = "/usr/share/fonts/opentype/cantarell/Cantarell-Bold.otf"
    font_size = 32
    bold_font_size = 36
    font = ImageFont.truetype(font_path, font_size)
    bold_font = ImageFont.truetype(font_path, bold_font_size)

    # Initialize image and draw
    width, height = epd.width, epd.height
    image = Image.new("1", (width, height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

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

            # Load the background image for days with an event
            background_image_path = "/home/administrator/empirestate/empirestate-light-display/empirestatespire.png"
            background_image = Image.open(background_image_path)
            background_image = background_image.resize((width, height), Image.ANTIALIAS)

            # Create a new image to draw text over the loaded background image
            final_image = Image.new("1", (width, height), 255)  # 255: clear the frame
            final_image.paste(background_image, (0, 0))

            # Initialize draw
            draw = ImageDraw.Draw(final_image)

            # Calculate text dimensions
            date_text_width, date_text_height = draw.textsize(date_text, font=font)

            # Draw today's date on the upper left corner
            draw.text((10, 10), date_text, font=font, fill=0)

            # Draw underline below today's date
            underline_y = 10 + date_text_height
            draw.line((10, underline_y, 10 + date_text_width, underline_y), fill=0, width=2)

            # Draw other text
            y_position = underline_y + 10
            for line in wrap_text(draw, lights_text, width * 2 // 3, font):
                draw.text((10, y_position), line, font=font, fill=0)
                y_position += font.getsize(line)[1]
            for line in wrap_text(draw, event_description_text, width * 2 // 3, font):
                draw.text((10, y_position), line, font=font, fill=0)
                y_position += font.getsize(line)[1]

            # Display the final image
            logging.info("Displaying image on display")
            epd.display(epd.getbuffer(final_image))

        else:
            # If there is no event today, show the new image with "No events today" message

            # Load the new image
            new_image_path = "/home/administrator/empirestate/empirestate-light-display/empirestateskyline.png"
            new_image = Image.open(new_image_path)
            new_image = new_image.resize((width, height), Image.ANTIALIAS)

            # Create a new image to draw text over the loaded image
            final_image = Image.new("1", (width, height), 255)  # 255: clear the frame
            final_image.paste(new_image, (0, 0))

            # Initialize draw
            draw = ImageDraw.Draw(final_image)

            # Calculate text dimensions for today's date
            date_text = todays_date.strftime("%A, %B ") + str(todays_date.day)
            date_text_width, date_text_height = draw.textsize(date_text, font=font)

            # Draw today's date on the upper left corner
            draw.text((width - date_text_width - 10, 10), date_text, font=font, fill=0)

            # Draw underline below today's date
            underline_y = 10 + date_text_height
            draw.line((width - date_text_width - 10, underline_y, width - 10, underline_y), fill=0, width=2)

            # Draw "No events today" text below today's date
            no_events_text = "No events today"
            text_width, text_height = draw.textsize(no_events_text, font=font)
            draw.text((width - text_width - 10, underline_y + 10), no_events_text, font=font, fill=0)

            # Display the final image
            logging.info("Displaying image on display")
            epd.display(epd.getbuffer(final_image))

    else:
        print("Failed to retrieve data from the website.")

    # Sleep
    logging.info("Powering off the display")
    epd.sleep()

except Exception as e:
    print('Error: ', e)
