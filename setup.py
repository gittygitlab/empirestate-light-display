import subprocess

def install_python_packages():
    # Install Python 3 packages
    subprocess.run(["sudo", "apt-get", "update"])
    subprocess.run(["sudo", "apt-get", "install", "python3-pip", "python3-pil", "python3-numpy", "python3-git", "-y"])
    subprocess.run(["sudo", "pip3", "install", "spidev"])

    # Install Python 2 packages
    subprocess.run(["sudo", "apt-get", "install", "python-pip", "python-pil", "python-numpy", "python-git", "-y"])
    subprocess.run(["sudo", "pip", "install", "spidev"])

def install_gpiozero():
    # Install gpiozero library for Python 3
    subprocess.run(["sudo", "apt-get", "install", "python3-gpiozero", "-y"])

    # Install gpiozero library for Python 2
    subprocess.run(["sudo", "apt-get", "install", "python-gpiozero", "-y"])

def install_crontab_module():
    subprocess.run(["sudo", "pip3", "install", "python-crontab"])

def system_update():
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "upgrade", "-y"])

def setup_cron_jobs():
    from crontab import CronTab
    
    cron = CronTab(user=True)
    # Add a cron job to reboot the system at 3 am every Monday
    reboot_job = cron.new(command='sudo reboot', comment='Reboot system at 3 am every Monday')
    reboot_job.dow.on('MON')
    reboot_job.hour.on(3)
    reboot_job.minute.on(0)
    
    # Add a cron job to run /home/administrator/empirestate/update_and_run.py at 4 am every morning
    update_and_run_job = cron.new(command='python3 /home/administrator/empirestate/update_and_run.py', comment='Run update_and_run.py at 4 am every morning')
    update_and_run_job.hour.on(4)
    update_and_run_job.minute.on(0)
    
    # Add cron jobs to run /home/administrator/check_website.py every hour from 7 am to 11 pm every day
    for hour in range(7, 24):
        check_website_job = cron.new(command='python3 /home/administrator/check_website.py', comment=f'Run check_website.py every hour from 7am until 11pm')
        check_website_job.hour.on(hour)
        check_website_job.minute.on(0)
    
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

def main():
    system_update()
    install_python_packages()
    install_gpiozero()
    install_crontab_module()
    setup_cron_jobs()
    setup_automatic_updates()
    setup_shutdown_service()

if __name__ == "__main__":
    main()
