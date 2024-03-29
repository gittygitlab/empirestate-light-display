import os
import git
import subprocess

# Define paths
REPO_URL = "https://github.com/gittygitlab/empirestate-light-display.git"
LOCAL_REPO_PATH = "/home/administrator/empirestate/empirestate-light-display"
SCRIPT_PATH = "/home/administrator/empirestate/empirestate-light-display/empirestate_display.py"

def update_repo():
    if os.path.exists(LOCAL_REPO_PATH):
        repo = git.Repo(LOCAL_REPO_PATH)
        repo.remotes.origin.pull()
    else:
        git.Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)

def run_script():
    subprocess.run(["python3", SCRIPT_PATH])

if __name__ == "__main__":
    update_repo()
    run_script()
