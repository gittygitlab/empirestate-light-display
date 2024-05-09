import logging
import time
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd4in26  # Import the e-Paper library

# Set debug mode for WaveShare EPD
logging.basicConfig(level=logging.DEBUG)

def draw_message(epd, message):
    # Define font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 24
    font = ImageFont.truetype(font_path, font_size)

    # Create an image with a white background
    width, height = epd.width, epd.height
    image = Image.new("1", (width, height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)

    # Calculate text size and position
    text_width, text_height = draw.textsize(message, font=font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 10  # Slightly above center

    # Draw message on the image
    draw.multiline_text((x, y), message, font=font, fill=0, align="center")

    # Display the image on the e-ink display
    logging.info(f"Displaying message: {message}")
    epd.display(epd.getbuffer(image))

def main():
    # Initialize e-ink display
    logging.info("Initializing e-ink display")
    epd = epd4in26.EPD()
    epd.init()

    # Define messages
    messages = [
        "Hello, now booting...\n\nEstimated time remaining:\n90 secs\n\n\n\n\nProject by: Tyler Wahl (2024)\nhttps://github.com/gittygitlab/empirestate-light-display",
        "awaiting network connection...\n\nEstimated time remaining:\n60 secs",
        "almost there...\n\nEstimated time remaining:\n30 secs"
    ]

    # Display messages
    for i, message in enumerate(messages):
        draw_message(epd, message)
        if i < len(messages) - 1:
            time.sleep(30)  # Wait for 30 seconds before displaying the next message
        else:
            time.sleep(5)  # Wait 5 seconds before putting display to sleep

    # Power off the display
    logging.info("Powering off the display")
    epd.sleep()

if __name__ == "__main__":
    main()
