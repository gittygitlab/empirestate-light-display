import os
import subprocess
from datetime import datetime

print(datetime.now()) # Display datetime for crontab logging

# Define paths
REPO_URL = "https://github.com/gittygitlab/empirestate-light-display.git"
LOCAL_REPO_PATH = "/home/administrator/empirestate"
SCRIPT_PATH = "/home/administrator/empirestate/empirestate_display.py"

def update_repo():
    os.chdir(LOCAL_REPO_PATH)  # Change current working directory to repository directory
    if os.path.exists(".git"):
        # Use git command-line tool to reset local changes and pull updates
        subprocess.run(["git", "reset", "--hard", "HEAD"])  # Reset local changes
        subprocess.run(["git", "pull"])  # Pull updates
    else:
        # Clone the repository if it doesn't exist locally
        subprocess.run(["git", "clone", REPO_URL, LOCAL_REPO_PATH])

def run_script():
    subprocess.run(["python3", SCRIPT_PATH])

if __name__ == "__main__":
    update_repo()
    run_script()
