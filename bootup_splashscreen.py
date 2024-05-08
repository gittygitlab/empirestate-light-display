import subprocess
import logging
import sys
from crontab import CronTab

# Configure logging
logging.basicConfig(filename='setup.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_error(message):
    logging.error(message)
    print(f"Error: {message}")

def install_python_packages():
    try:
        # Install Python 3 packages
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "python3-pip", "python3-pil", "python3-numpy", "python3-git", "-y"])
        subprocess.run(["sudo", "pip3", "install", "spidev"])

        # Install Python 2 packages
        subprocess.run(["sudo", "apt-get", "install", "python-pip", "python-pil", "python-numpy", "python-git", "-y"])
        subprocess.run(["sudo", "pip", "install", "spidev"])
        logging.info("Python packages installed successfully.")
    except Exception as e:
        log_error(f"Failed to install Python packages: {str(e)}")

def install_gpiozero():
    try:
        # Install gpiozero library for Python 3
        subprocess.run(["sudo", "apt-get", "install", "python3-gpiozero", "-y"])

        # Install gpiozero library for Python 2
        subprocess.run(["sudo", "apt-get", "install", "python-gpiozero", "-y"])
        logging.info("gpiozero library installed successfully.")
    except Exception as e:
        log_error(f"Failed to install gpiozero library: {str(e)}")

def install_crontab_module():
    try:
        subprocess.run(["sudo", "pip3", "install", "python-crontab"])
        logging.info("python-crontab module installed successfully.")
    except Exception as e:
        log_error(f"Failed to install python-crontab module: {str(e)}")

def check_dependency(package_name):
    try:
        subprocess.run(["dpkg", "-l", package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info(f"{package_name} already installed.")
        return True
    except subprocess.CalledProcessError as e:
        logging.warning(f"{package_name} is not installed.")
        return False

def install_dependency(package_name):
    try:
        subprocess.run(["sudo", "apt-get", "install", package_name, "-y"])
        logging.info(f"{package_name} installed successfully.")
    except Exception as e:
        log_error(f"Failed to install {package_name}: {str(e)}")

def system_update():
    try:
        subprocess.run(["sudo", "apt", "update"])
        subprocess.run(["sudo", "apt", "upgrade", "-y"])
        logging.info("System updated successfully.")
    except Exception as e:
        log_error(f"Failed to update system: {str(e)}")

def setup_cron_jobs():
    try:
        cron = CronTab(user=True)
        
        # Check if the reboot job already exists
        existing_reboot_jobs = cron.find_comment('Reboot system at 3 am every Monday')
        if not existing_reboot_jobs:
            # Add a cron job to reboot the system at 3 am every Monday
            reboot_job = cron.new(command='sudo reboot', comment='Reboot system at 3 am every Monday')
            reboot_job.dow.on('MON')
            reboot_job.hour.on(3)
            reboot_job.minute.on(0)
            logging.info("Reboot cron job set up successfully.")
        else:
            logging.warning("Reboot cron job already exists.")
        
        # Add a cron job to run /home/administrator/empirestate/update_and_run.py at 4 am every morning
        existing_update_and_run_jobs = cron.find_comment('Run update_and_run.py at 4 am every morning')
        if not existing_update_and_run_jobs:
            update_and_run_job = cron.new(command='python3 /home/administrator/empirestate/update_and_run.py', comment='Run update_and_run.py at 4 am every morning')
            update_and_run_job.hour.on(4)
            update_and_run_job.minute.on(0)
            logging.info("update_and_run cron job set up successfully.")
        else:
            logging.warning("update_and_run cron job already exists.")
        
        # Add cron jobs to run /home/administrator/check_website.py every hour from 7 am to 11 pm every day
        for hour in range(7, 24):
            existing_check_website_jobs = cron.find_comment(f'Run check_website.py every hour from 7am until 11pm at {hour} hour')
            if not existing_check_website_jobs:
                check_website_job = cron.new(command=f'python3 /home/administrator/check_website.py', comment=f'Run check_website.py every hour from 7am until 11pm at {hour} hour')
                check_website_job.hour.on(hour)
                check_website_job.minute.on(0)
                logging.info(f"check_website cron job for hour {hour} set up successfully.")
            else:
                logging.warning(f"check_website cron job for hour {hour} already exists.")
        
        cron.write()
    except Exception as e:
        log_error(f"Failed to set up cron jobs: {str(e)}")

def setup_automatic_updates():
    try:
        # Check if the automatic updates are already set up
        existing_updates = subprocess.run(["sudo", "apt-get", "install", "--dry-run", "unattended-upgrades"], capture_output=True, text=True)
        if "unattended-upgrades is already the newest version" not in existing_updates.stdout:
            subprocess.run(["sudo", "apt-get", "install", "unattended-upgrades", "-y"])
            with open('/etc/apt/apt.conf.d/50unattended-upgrades', 'a') as f:
                f.write('APT::Periodic::Update-Package-Lists "1";\n')
                f.write('APT::Periodic::Download-Upgradeable-Packages "1";\n')
                f.write('APT::Periodic::AutocleanInterval "7";\n')
                f.write('APT::Periodic::Unattended-Upgrade "1";\n')
                # Disable automatic reboot after updates
                f.write('Unattended-Upgrade::Automatic-Reboot "false";\n')
            logging.info("Automatic updates set up successfully.")
        else:
            logging.warning("Automatic updates already set up.")
    except Exception as e:
        log_error(f"Failed to set up automatic updates: {str(e)}")

def setup_shutdown_service():
    try:
        # Check if the shutdown service already exists
        existing_shutdown_service = subprocess.run(["sudo", "systemctl", "status", "shutdown_splashscreen.service"], capture_output=True, text=True)
        if "shutdown_splashscreen.service could not be found" in existing_shutdown_service.stdout:
            # Create the service unit file
            service_unit_content = """
[Unit]
Description=Run shutdown_splashscreen.py on shutdown
DefaultDependencies=no
Before=shutdown.target reboot.target halt.target

[Service]
Type=oneshot
ExecStart=/bin/true
ExecStop=/usr/bin/python3 /home/administrator/empirestate/shutdown_splashscreen.py

[Install]
WantedBy=halt.target reboot.target shutdown.target
"""
            with open('/etc/systemd/system/shutdown_splashscreen.service', 'w') as f:
                f.write(service_unit_content)
            
            # Enable the service
            subprocess.run(["sudo", "systemctl", "enable", "shutdown_splashscreen.service"])
            logging.info("Shutdown service set up successfully.")
        else:
            logging.warning("Shutdown service already exists.")
    except Exception as e:
        log_error(f"Failed to set up shutdown service: {str(e)}")

def setup_update_and_run_service():
    try:
        # Check if the update_and_run service already exists
        existing_update_and_run_service = subprocess.run(["sudo", "systemctl", "status", "update_and_run.service"], capture_output=True, text=True)
        if "update_and_run.service could not be found" in existing_update_and_run_service.stdout:
            # Create the service unit file
            service_unit_content = """
[Unit]
Description=Run update_and_run.py after network is up
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/administrator/empirestate/update_and_run.py

[Install]
WantedBy=multi-user.target
"""
            with open('/etc/systemd/system/update_and_run.service', 'w') as f:
                f.write(service_unit_content)
            
            # Enable the service
            subprocess.run(["sudo", "systemctl", "enable", "update_and_run.service"])
            logging.info("update_and_run service set up successfully.")
        else:
            logging.warning("update_and_run service already exists.")
    except Exception as e:
        log_error(f"Failed to set up update_and_run service: {str(e)}")

def main():
    try:
        system_update()
        # Check and install dependencies
        if not check_dependency("python3-pip"):
            install_dependency("python3-pip")
        if not check_dependency("python-pip"):
            install_dependency("python-pip")
        if not check_dependency("python3-gpiozero"):
            install_dependency("python3-gpiozero")
        if not check_dependency("python-gpiozero"):
            install_dependency("python-gpiozero")
        if not check_dependency("python3-crontab"):
            install_dependency("python3-crontab")
        if not check_dependency("python3-git"):
            install_dependency("python3-git")
        if not check_dependency("python3-pil"):
            install_dependency("python3-pil")
        if not check_dependency("python3-numpy"):
            install_dependency("python3-numpy")
        if not check_dependency("spidev"):
            install_dependency("spidev")
        
        install_python_packages()
        install_gpiozero()
        install_crontab_module()
        setup_cron_jobs()
        setup_automatic_updates()
        setup_shutdown_service()
        setup_update_and_run_service()
        print("Setup completed successfully. Please check setup.log for details.")
        logging.info("Setup completed successfully.")
    except Exception as e:
        log_error(f"Setup failed: {str(e)}")


if __name__ == "__main__":
    main()
