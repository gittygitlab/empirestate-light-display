import logging
from waveshare_epd import epd4in26

def clear_screen_and_power_off():
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    try:
        # Initialize e-ink display
        logging.info("Initializing e-ink display")
        epd = epd4in26.EPD()
        epd.init()

        # Clear the screen
        logging.info("Clearing the screen")
        epd.Clear()

        # Power off the display
        logging.info("Powering off the display")
        epd.sleep()


    except Exception as e:
        logging.error("Error: " + str(e))

if __name__ == "__main__":
    clear_screen_and_power_off()
