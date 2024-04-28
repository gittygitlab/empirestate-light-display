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

message1 = "Goodbye\n\nThe system is shutdown.\n\n\n\nTo power on, unplug and replug the power cable.\n\nNote: The display may not update for 30 seconds."

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

# Wait for display to finish updating
time.sleep(10)

# Sleep
logging.info("Powering off the display")
epd.sleep()
