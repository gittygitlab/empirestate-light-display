## Setup script to run on new raspbian install. ##

import subprocess
from crontab import CronTab

def install_python_packages():
    # Install Python 3 packages
    subprocess.run(["sudo", "apt-get", "update"])
    subprocess.run(["sudo", "apt-get", "install", "python3-pip", "python3-pil", "python3-numpy", "-y"])
    subprocess.run(["sudo", "pip3", "install", "spidev"])

    # Install Python 2 packages
    subprocess.run(["sudo", "apt-get", "install", "python-pip", "python-pil", "python-numpy", "-y"])
    subprocess.run(["sudo", "pip", "install", "spidev"])

def install_gpiozero():
    # Install gpiozero library for Python 3
    subprocess.run(["sudo", "apt-get", "install", "python3-gpiozero", "-y"])

    # Install gpiozero library for Python 2
    subprocess.run(["sudo", "apt-get", "install", "python-gpiozero", "-y"])

def system_update():
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "upgrade", "-y"])

def setup_cron_jobs():
    cron = CronTab(user=True)
    # Add a cron job to reboot the system every Monday at 2 am
    reboot_job = cron.new(command='sudo reboot', comment='Reboot system every Monday at 2 am')
    reboot_job.dow.on('MON')
    reboot_job.hour.on(2)
    reboot_job.minute.on(0)
       
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

def main():
    system_update()
    install_python_packages()
    install_gpiozero()
    setup_cron_jobs()
    setup_automatic_updates()

if __name__ == "__main__":
    main()
