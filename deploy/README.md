# XENOScribe Server Deployment

This directory contains scripts for deploying XENOScribe as a production service on a Linux server.

## Prerequisites

- Ubuntu/Debian-based server (tested on Ubuntu 20.04/22.04)
- Root access to the server
- A domain name pointing to your server's IP address

## Setup Instructions

1. **Copy the application files to your server**
   ```bash
   git clone https://github.com/yourusername/xenoscribe.git /opt/xenoscribe
   ```

2. **Make the setup script executable**
   ```bash
   chmod +x /opt/xenoscribe/deploy/setup_server.sh
   ```

3. **Run the setup script as root**
   ```bash
   sudo /opt/xenoscribe/deploy/setup_server.sh
   ```
   The script will:
   - Install required system packages
   - Set up a systemd service
   - Configure Nginx as a reverse proxy
   - Optionally set up SSL with Let's Encrypt

4. **Configure your domain**
   - Ensure your domain's DNS A record points to your server's IP address
   - If you chose to set up SSL, Certbot will handle the certificate issuance

## Managing the Service

- **Start service**: `sudo systemctl start xenoscribe`
- **Stop service**: `sudo systemctl stop xenoscribe`
- **Restart service**: `sudo systemctl restart xenoscribe`
- **View logs**: `sudo journalctl -u xenoscribe -f`

## Updating

To update to the latest version:

```bash
cd /opt/xenoscribe
git pull
sudo systemctl restart xenoscribe
```

## Security Considerations

- The application runs as a non-root user (`xenoscribe`)
- Firewall rules are automatically configured if `ufw` is active
- SSL is strongly recommended for production use
- Keep your system and dependencies updated

## Troubleshooting

- Check service status: `systemctl status xenoscribe`
- View Nginx error logs: `tail -f /var/log/nginx/error.log`
- Check application logs: `journalctl -u xenoscribe -f`
- If you encounter permission issues, ensure the `xenoscribe` user has proper access to the application directory
