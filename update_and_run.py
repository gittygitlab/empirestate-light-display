import os
import git
import subprocess

# Define paths
REPO_URL = "https://github.com/gittygitlab/empirestate-light-display.git"
LOCAL_REPO_PATH = "/home/administrator/empirestate"
SCRIPT_PATH = "/home/administrator/empirestate/empirestate_display.py"

def update_repo():
    os.chdir(LOCAL_REPO_PATH)  # Change current working directory to repository directory
    if os.path.exists(".git"):
        repo = git.Repo(LOCAL_REPO_PATH)
        try:
            repo.remotes.origin.pull()
        except git.exc.GitCommandError as e:
            if "Your local changes to the following files would be overwritten by merge" in str(e):
                # Discard local changes and overwrite
                subprocess.run(["git", "reset", "--hard", "HEAD"])
                repo.remotes.origin.pull()
            else:
                raise e
    else:
        git.Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)

def run_script():
    subprocess.run(["python3", SCRIPT_PATH])

if __name__ == "__main__":
    update_repo()
    run_script()
