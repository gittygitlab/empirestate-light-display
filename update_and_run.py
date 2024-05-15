import os
import subprocess
import logging
from datetime import datetime

# Set up logging with date and time
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Define paths
REPO_URL = "https://github.com/gittygitlab/empirestate-light-display.git"
LOCAL_REPO_PATH = "/home/administrator/empirestate"
SCRIPT_PATH = "/home/administrator/empirestate/empirestate_display.py"

def update_repo():
    try:
        logging.info("Updating repository...")
        os.chdir(LOCAL_REPO_PATH)  # Change current working directory to repository directory
        if os.path.exists(".git"):
            # Use git command-line tool to reset local changes and pull updates
            subprocess.run(["git", "reset", "--hard", "HEAD"])  # Reset local changes
            subprocess.run(["git", "pull"])  # Pull updates
        else:
            # Clone the repository if it doesn't exist locally
            logging.info("Cloning repository...")
            subprocess.run(["git", "clone", REPO_URL, LOCAL_REPO_PATH])
    except Exception as e:
        logging.error("An error occurred while updating the repository: %s", e)

def run_script():
    try:
        logging.info("Running script...")
        subprocess.run(["python3", SCRIPT_PATH])
    except Exception as e:
        logging.error("An error occurred while running the script: %s", e)

if __name__ == "__main__":
    update_repo()
    run_script()
