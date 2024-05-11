import subprocess
import logging
import os

def install_python_packages():
    try:
        # Install Python 3 packages
        subprocess.run(["sudo", "apt-get", "update"])
        subprocess.run(["sudo", "apt-get", "install", "python3-pip", "python3-pil", "python3-numpy", "python3-git", "-y"])

        # Install Python 2 packages
        subprocess.run(["sudo", "apt-get", "install", "python-pip", "python-pil", "python-numpy", "python-git", "-y"])

        logging.info("Python packages installed successfully.")
    except Exception as e:
        log_error(f"Failed to install Python packages: {str(e)}")

def install_crontab_module():
    # Install python3-crontab using apt
    subprocess.run(["sudo", "apt-get", "install", "python3-crontab", "-y"])

def install_gpiozero():
    # Install gpiozero library for Python 3
    subprocess.run(["sudo", "apt-get", "install", "python3-gpiozero", "-y"])

    # Install gpiozero library for Python 2
    subprocess.run(["sudo", "apt-get", "install", "python-gpiozero", "-y"])

def install_ntpdate():
    # Install ntpdate
    subprocess.run(["sudo", "apt-get", "install", "ntpdate", "-y"])

def system_update():
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "upgrade", "-y"])

def setup_cron_jobs():
    try:
        from crontab import CronTab
    except ImportError as e:
        log_error(f"Failed to import CronTab: {e}. Make sure python-crontab module is installed.")
        return
    
    try:
        cron = CronTab(user=True)
    except Exception as e:
        log_error(f"Failed to instantiate CronTab: {e}. Make sure python-crontab module is correctly installed.")
        return

    # Check if the reboot job already exists
    reboot_job_exists = False
    update_and_run_job_exists = False
    check_website_job_exists = False
    clear_screen_job_exists = False
    
    for job in cron:
        if job.comment == 'Reboot system at 3 am every Monday':
            reboot_job_exists = True
        elif job.comment == 'Run update_and_run.py at 4 am every morning':
            update_and_run_job_exists = True
        elif job.comment == 'Run check_website.py every hour from 7am until 11pm':
            check_website_job_exists = True
        elif job.comment == 'Run clear_screen.py at 2 am every morning':
            clear_screen_job_exists = True
    
    # Add the reboot job if it doesn't exist
    if not reboot_job_exists:
        reboot_job = cron.new(command='sbin/reboot', comment='Reboot system at 3 am every Monday')
        reboot_job.dow.on('1')
        reboot_job.hour.on(3)
        reboot_job.minute.on(0)
    
    # Add the update_and_run job if it doesn't exist
    if not update_and_run_job_exists:
        update_and_run_job = cron.new(command='python3 /home/administrator/empirestate/update_and_run.py', comment='Run update_and_run.py at 4 am every morning')
        update_and_run_job.hour.on(4)
        update_and_run_job.minute.on(0)
    
    # Add the check_website job if it doesn't exist
    if not check_website_job_exists:
        for hour in range(7, 24):
            check_website_job = cron.new(command='python3 /home/administrator/check_website.py', comment=f'Run check_website.py every hour from 7am until 11pm')
            check_website_job.hour.on(hour)
            check_website_job.minute.on(0)
    
    # Add the clear_screen job if it doesn't exist
    if not clear_screen_job_exists:
        clear_screen_job = cron.new(command='python3 /home/administrator/empirestate/clear_screen.py', comment='Run clear_screen.py at 2 am every morning')
        clear_screen_job.hour.on(2)
        clear_screen_job.minute.on(0)

    cron.write()

def setup_automatic_updates():
    subprocess.run(["sudo", "apt-get", "install", "unattended-upgrades", "-y"])
    with open('/etc/apt/apt.conf.d/50unattended-upgrades', 'a') as f:
        f.write('APT::Periodic::Update-Package-Lists "1";\n')
        f.write('APT::Periodic::Download-Upgradeable-Packages "1";\n')
        f.write('APT::Periodic::AutocleanInterval "7";\n')
        f.write('APT::Periodic::Unattended-Upgrade "1";\n')
        # Disable automatic reboot after updates
        f.write('Unattended-Upgrade::Automatic-Reboot "false";\n')

def setup_shutdown_service():
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

def setup_bootup_service():
    # Create the service unit file
    service_unit_content = """
[Unit]
Description=Run bootup_splashscreen.py on startup

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/administrator/empirestate/bootup_splashscreen.py

[Install]
WantedBy=basic.target
"""
    with open('/etc/systemd/system/bootup_splashscreen.service', 'w') as f:
        f.write(service_unit_content)
    
    # Enable the service
    subprocess.run(["sudo", "systemctl", "enable", "bootup_splashscreen.service"])

def setup_update_and_run_service():
    # Create the service unit file
    service_unit_content = """
[Unit]
Description=Run update_and_run.py after startup and internet connection
After=network-online.target

[Service]
Type=simple
ExecStartPre=/bin/sleep 10
ExecStart=/usr/bin/python3 /home/administrator/empirestate/update_and_run.py

[Install]
WantedBy=multi-user.target
"""
    with open('/etc/systemd/system/update_and_run.service', 'w') as f:
        f.write(service_unit_content)
    
    # Enable the service
    subprocess.run(["sudo", "systemctl", "enable", "update_and_run.service"])

def log_error(message):
    print(f"ERROR: {message}")

def main():
    install_crontab_module()  # Install crontab module
    subprocess.run(["sudo", "chown", "-R", "administrator:administrator", "/home/administrator/empirestate"])
    subprocess.run(["sudo", "chmod", "-R", "777", "/home/administrator/empirestate"])  # Set permissions to 777
    
    system_update()
    install_ntpdate()
    install_python_packages()
    install_gpiozero()
    setup_cron_jobs()
    setup_automatic_updates()
    setup_shutdown_service()
    setup_bootup_service()  # Setup the bootup service
    setup_update_and_run_service()  # Setup the update_and_run service
    
    # Create the event_details.json file and set permissions
    event_details_file = "/home/administrator/empirestate/event_details.json"
    try:
        open(event_details_file, "w").close()  # Create an empty file
        os.chmod(event_details_file, 0o777)  # Set permissions to 777
        logging.info("event_details.json file created and permissions set successfully.")
    except Exception as e:
        log_error(f"Failed to create event_details.json file: {str(e)}")

if __name__ == "__main__":
    main()
