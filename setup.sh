#!/bin/bash

# Update and install dependencies
sudo apt update
sudo apt install -y samba samba-common-bin krb5-config krb5-user winbind libpam-winbind libnss-winbind

# Provision Samba as AD DC
sudo samba-tool domain provision --use-rfc2307 --realm=CADET.LOCAL --domain=CADET --server-role=dc --dns-backend=SAMBA_INTERNAL --adminpass='StrongPassword123!'

# Configure Kerberos
cat <<EOF | sudo tee /etc/krb5.conf
[libdefaults]
    default_realm = CADET.LOCAL
    dns_lookup_realm = false
    dns_lookup_kdc = true
EOF

# Configure Samba with DNS settings
cat <<EOF | sudo tee /etc/samba/smb.conf
[global]
    workgroup = CADET
    realm = CADET.LOCAL
    server role = active directory domain controller
    idmap_ldb:use rfc2307 = yes
    dns forwarder = 8.8.8.8  # Forward DNS queries to Google DNS

[sysvol]
    path = /var/lib/samba/sysvol
    read only = No

[netlogon]
    path = /var/lib/samba/sysvol/cadet.local/scripts
    read only = No
EOF

# Start Samba AD DC service
sudo systemctl stop smbd nmbd winbind
sudo systemctl disable smbd nmbd winbind
sudo systemctl enable samba-ad-dc
sudo systemctl start samba-ad-dc

# Restart Samba to apply changes
sudo systemctl restart samba-ad-dc

echo "Samba AD DC setup complete. Join Windows clients to the domain CADET.LOCAL"