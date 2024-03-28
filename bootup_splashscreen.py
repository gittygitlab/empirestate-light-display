import logging
import time
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in26  # Import the e-Paper library

# Set debug mode for WaveShare EPD
logging.basicConfig(level=logging.DEBUG)

# Initialize e-ink display
logging.info("Initializing e-ink display")
epd = epd4in26.EPD()
epd.init()

# Define font and messages
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font_size = 24
font = ImageFont.truetype(font_path, font_size)

message1 = "Hello\n\nnow booting..."
message2 = "please hold\n\nawaiting network connection and script update"

# Create an image with a white background
width, height = epd.width, epd.height
image = Image.new("1", (width, height), 255)  # 255: clear the frame
draw = ImageDraw.Draw(image)

# Calculate text size and position for message1
text_width, text_height = draw.textsize(message1, font=font)
x = (width - text_width) // 2
y = (height - text_height) // 2 - 10  # Slightly above center

# Draw message1 on the image
draw.multiline_text((x, y), message1, font=font, fill=0, align="center")

# Display the image on the e-ink display
logging.info("Displaying splash screen")
epd.display(epd.getbuffer(image))

# Wait for 5 seconds
time.sleep(5)

# Clear the image
draw.rectangle((0, 0, width, height), fill=255)

# Calculate text size and position for message2
text_width, text_height = draw.textsize(message2, font=font)
x = (width - text_width) // 2
y = (height - text_height) // 2 - 10  # Slightly above center

# Draw message2 on the image
draw.multiline_text((x, y), message2, font=font, fill=0, align="center")

# Display the updated image on the e-ink display
logging.info("Displaying 'Please hold' message")
epd.display(epd.getbuffer(image))

# Sleep
logging.info("Powering off the display")
epd.sleep()
