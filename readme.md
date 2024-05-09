# Empire State Light Display

The Empire State Light Display project retrieves information about the Empire State Building tower lights schedule from its official website and displays it on an e-ink display.

## Features

- Retrieves tower lights schedule information from the Empire State Building website.
- Displays the schedule information on an e-ink display.
- Checks throughout the day for changes.
- Automatically runs system updates and reboots once a week

## Setup
### Note: 
### Setup directions and project files are built on the user being named 'administrator'. Current code will not work with a different username.

### Enable SPI Interface
Open the Raspberry Pi terminal and enter the following command in the config interface:
	  ```
      sudo raspi-config
      ```

Choose Interfacing Options -> SPI -> Yes Enable SPI interface

Reboot your Raspberry Pi:
	  ```
      sudo reboot
      ```

Check /boot/config.txt, and you can see 'dtparam=spi=on' was written in.

### Update system
      sudo apt update
	  sudo apt upgrade
#### If update fails, see troubleshooting below.

### Clone Repo and run setup script
Clone repo to /home/administrator/empirestate: 
	  ```
      sudo git clone https://github.com/gittygitlab/empirestate-light-display.git /home/administrator/empirestate
      ```
      
Run setup script: 
	  ```
      sudo python ./empirestate/setup.py
      ```
    


## Troubleshooting
### If system update stalls reading changelogs, swap file may be too small.
1. Before we can increase our Raspberry Pis swap file, we must first temporarily stop it.
	  sudo dphys-swapfile swapoff

2. Next, we need to modify the swap file configuration file.
	  sudo nano /etc/dphys-swapfile

3. Within this config file, find the following line of text.
	CONF_SWAPSIZE=100

	This number is the size of the swap in megabytes.
	CONF_SWAPSIZE=1024  # This would be 1GB

	Whatever size you set, you must have that space available on your SD card. Check file directory with:
   	df -h 

5. Once you have made the change, save the file by pressing CTRL + X, followed by Y, then ENTER.

6. We can now re-initialize the Raspberry Pis swap file by running the command below.
	  sudo dphys-swapfile setup

7. With the swap now recreated to the newly defined size, we can now turn the swap back on.
	  sudo dphys-swapfile swapon

8. If you want all programs to be reloaded with access to the new memory pool, then the easiest way is to restart your device.
	  sudo reboot
