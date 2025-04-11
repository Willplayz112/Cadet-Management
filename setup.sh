#!/bin/bash

# Update and install dependencies
sudo apt update
sudo apt install -y python3 python3-pip samba krb5-config winbind libnss-winbind libpam-winbind

# Install Python packages
pip3 install -r requirements.txt

# Setup Samba if not already configured
if [ ! -f /etc/samba/smb.conf.bak ]; then
    sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
    sudo cp samba/smb.conf /etc/samba/smb.conf
fi

# Set executable permissions for GPO scripts
chmod +x gpo-scripts/*.bat
chmod +x gpo-scripts/*.ps1

echo "Setup complete. Run 'python3 webadmin/app.py' to start the web interface."