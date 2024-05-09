import os
import subprocess
import RPi.GPIO as GPIO
import time

# Define paths
REPO_URL = "https://github.com/gittygitlab/empirestate-light-display.git"
LOCAL_REPO_PATH = "/home/administrator/empirestate"
SCRIPT_PATH = "/home/administrator/empirestate/empirestate_display.py"
FIRST_SERVICE_NAME = "bootup_splashscreen.service"
SECOND_SERVICE_NAME = "update_and_run.service"
GPIO_PIN = 18  # Example GPIO pin used by the first service

def update_repo():
    os.chdir(LOCAL_REPO_PATH)  # Change current working directory to repository directory
    if os.path.exists(".git"):
        # Use git command-line tool to reset local changes and pull updates
        subprocess.run(["git", "reset", "--hard", "HEAD"])  # Reset local changes
        subprocess.run(["git", "pull"])  # Pull updates
    else:
        # Clone the repository if it doesn't exist locally
        subprocess.run(["git", "clone", REPO_URL, LOCAL_REPO_PATH])

def check_gpio_availability():
    GPIO.setmode(GPIO.BCM)
    gpio_function = GPIO.gpio_function(GPIO_PIN)
    GPIO.cleanup()
    return gpio_function == GPIO.IN

def stop_first_service():
    subprocess.run(["sudo", "systemctl", "stop", FIRST_SERVICE_NAME])

def start_second_service():
    subprocess.run(["sudo", "systemctl", "start", SECOND_SERVICE_NAME])

def run_script():
    subprocess.run(["python3", SCRIPT_PATH])

if __name__ == "__main__":
    if check_gpio_availability():
        start_second_service()
    else:
        stop_first_service()
        time.sleep(1)  # Adjust the delay time as needed
        start_second_service()
    update_repo()
    run_script()
