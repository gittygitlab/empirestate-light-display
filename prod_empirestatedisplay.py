import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in26

# Set debug mode for WaveShare EPD
logging.basicConfig(level=logging.DEBUG)


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

# Set today's date
todays_date = datetime.now()

# Generate the date with suffix
def ordinal_suffix(day):
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return str(day) + suffix

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
        event_description = event_description.strip()

        # Calculate text dimensions
        date_text = todays_date.strftime("%A, %B ") + ordinal_suffix(todays_date.day)
        lights_text = "Lights: " + lights
        event_description_text = "Description: " + event_description

        # Debug information
        print("Event found for today:")
        print("Date:", date_text)
        print("Lights:", lights_text)
        print("Event Description:", event_description_text)

        # Draw text on image (aligned to the left)
        text_width = width * 2 // 3
        y_position = 10
        # Underline settings
        underline_position = y_position + bold_font.getsize(date_text)[1] - 5
        underline_length = bold_font.getsize(date_text)[0]

        # Draw date text
        for line in wrap_text(draw, date_text, text_width, bold_font):
            draw.text((10, y_position), line, font=bold_font, fill=0)
            y_position += bold_font.getsize(line)[1]

        # Underline today's date
        draw.line((10, underline_position, 10 + underline_length, underline_position), fill=0, width=2)

        # Draw other text
        for line in wrap_text(draw, lights_text, text_width, font):
            draw.text((10, y_position), line, font=font, fill=0)
            y_position += font.getsize(line)[1]
        for line in wrap_text(draw, event_description_text, text_width, font):
            draw.text((10, y_position), line, font=font, fill=0)
            y_position += font.getsize(line)[1]

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
                event_description = event_description[0].lower() + event_description[1:]

                # Calculate text dimensions
                date_text = todays_date.strftime("%A, %B ") + ordinal_suffix(todays_date.day)
                lights_text = "Lights: Signature White"
                no_event_text = "Description: There are no events scheduled for today."
                next_event_text = f"The next event is {next_event_date.strftime('%A, %B %d')} {event_description}."

                # Debug information
                print("No event found for today. Showing upcoming event information:")
                print("Date:", date_text)
                print("Lights:", lights_text)
                print("No Event Description:", no_event_text)
                print("Next Event:", next_event_text)

                # Draw text on image (aligned to the left)
                text_width = width * 2 // 3
                y_position = 10
                for line in wrap_text(draw, date_text, text_width, bold_font):
                    draw.text((10, y_position), line, font=bold_font, fill=0)
                    y_position += bold_font.getsize(line)[1]

                # Underline today's date
                underline_position = y_position - 5
                underline_length = bold_font.getsize(date_text)[0]
                draw.line((10, underline_position, 10 + underline_length, underline_position), fill=0, width=2)

                # Add a blank line
                y_position += font.getsize(" ")[1]  # Add height of a single space

                for line in wrap_text(draw, lights_text, text_width, font):
                    draw.text((10, y_position), line, font=font, fill=0)
                    y_position += font.getsize(line)[1]
                for line in wrap_text(draw, no_event_text, text_width, font):
                    draw.text((10, y_position), line, font=font, fill=0)
                    y_position += font.getsize(line)[1] 
                # Add a blank line
                y_position += font.getsize(" ")[1]  # Add height of a single space
                for line in wrap_text(draw, next_event_text, text_width, font):
                    draw.text((10, y_position), line, font=font, fill=0)
                    y_position += font.getsize(line)[1]
                break
else:
    print("Failed to retrieve data from the website.")

# Load the large image
icon_path = "./empirestateicon.png"
icon = Image.open(icon_path)

# Resize the image to fit one-third of the width
icon_width = width // 4  # Adjust the divisor to change the size
icon_height = icon.size[1] * icon_width // icon.size[0]
icon = icon.resize((icon_width, icon_height), Image.ANTIALIAS)

# Calculate image position with padding
top_padding = (height - icon.height) // 3  # Adjust the divisor to change the padding
icon_x = width - icon.width - 10
icon_y = top_padding

# Paste the image onto the main image
image.paste(icon, (icon_x, icon_y), icon)

# Display image
logging.info("Displaying image on display")
epd.display(epd.getbuffer(image))

# Sleep
logging.info("Powering off the display")
epd.sleep()
