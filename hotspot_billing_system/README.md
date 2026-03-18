# Hotspot Billing System - comprehensive setup and operation guide

## Project Structure
```
hotspot_billing_system/
├── app/                          # Flask application package
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes/                  # API routes
│   │   ├── portal.py            # Captive portal endpoints
│   │   └── admin.py             # Admin panel endpoints
│   └── utils/
│       └── firewall.py          # Firewall management
├── config/                       # Configuration files
│   ├── settings.py              # Main settings
│   ├── hostapd.conf.example     # WiFi AP configuration
│   └── dnsmasq.conf.example     # DHCP/DNS configuration
├── scripts/                      # Support scripts
│   ├── auto_expiry.py           # Session expiry daemon
│   ├── setup_network.py         # Network configuration
│   └── init_db.py               # Database initialization
├── templates/                    # HTML templates
│   ├── login.html               # Portal login page
│   └── admin_dashboard.html     # Admin interface
├── static/                       # Static files (CSS, JS)
├── run.py                       # Main application entry point
└── requirements.txt             # Python dependencies
```

## Prerequisites

### Required Packages
- Python 3.8+
- pip
- Linux system (tested on Ubuntu/Debian)
- hostapd (WiFi AP)
- dnsmasq (DHCP/DNS)
- iptables (firewall)
- Two WiFi interfaces OR one with AP+Client support

### Required Python Packages
```bash
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
python-dotenv==1.0.0
requests==2.31.0
```

## Installation Steps

### 1. System Preparation

Install required system packages:
```bash
sudo apt-get update
sudo apt-get install python3-pip hostapd dnsmasq iptables sqlite3

pip3 install -r requirements.txt
```

### 2. Configure Network Interfaces

Create virtual AP interface (if needed):
```bash
sudo iw phy phy0 interface add wlan1_ap type managed
sudo ip link set wlan1_ap up
```

Or, create udev rule for persistent interface (create `/etc/udev/rules.d/99-wlan.rules`):
```
SUBSYSTEM=="net", ACTION=="add", KERNEL=="wlan*", RUN+="/usr/sbin/iw phy %k interface add \
%k_ap type managed"
```

### 3. Configure Hostapd

Edit `/etc/hostapd/hostapd.conf`:
```bash
sudo cp config/hostapd.conf.example /etc/hostapd/hostapd.conf
sudo nano /etc/hostapd/hostapd.conf
```

Start hostapd:
```bash
sudo systemctl start hostapd
sudo systemctl enable hostapd
```

### 4. Configure Dnsmasq

Edit `/etc/dnsmasq.d/hotspot.conf`:
```bash
sudo cp config/dnsmasq.conf.example /etc/dnsmasq.d/hotspot.conf
sudo nano /etc/dnsmasq.d/hotspot.conf
```

Start dnsmasq:
```bash
sudo systemctl start dnsmasq
sudo systemctl enable dnsmasq
```

### 5. Setup Network Rules

Run the network setup script (configures IP forwarding, NAT, etc.):
```bash
sudo python3 scripts/setup_network.py
```

### 6. Initialize Database

Create sample vouchers for testing:
```bash
python3 scripts/init_db.py
```

## Running the Application

### 1. Start the Flask Application

```bash
python3 run.py
```

The portal will be available at:
- Portal: `http://192.168.10.1:8080`
- Admin: `http://192.168.10.1:8080/admin`

### 2. Start the Auto-Expiry Daemon (in another terminal)

```bash
python3 scripts/auto_expiry.py
```

Or run as a background service. Create `/etc/systemd/system/hotspot-expiry.service`:
```ini
[Unit]
Description=Hotspot Auto-Expiry Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/noel/Desktop/sideAPP/hotspot_billing_system
ExecStart=/usr/bin/python3 scripts/auto_expiry.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable hotspot-expiry
sudo systemctl start hotspot-expiry
```

## Usage

### Testing the System

1. **Connect to WiFi**: Connect a device to the `FreeHotspot` network
2. **Open Browser**: Open any website; you'll be redirected to login
3. **Enter Voucher Code**: Use a code from the database
4. **Access Internet**: You'll have internet for the specified duration

### Admin Panel

1. **Access Admin**: Go to `http://192.168.10.1:8080/admin`
2. **Login**: Use credentials from `config/settings.py`
3. **Create Vouchers**: Generate voucher codes
4. **Monitor Sessions**: View active users and their remaining time
5. **Disconnect Users**: End sessions manually
6. **View Logs**: Check all system events

### API Endpoints

#### Portal
- `GET /` - Login page
- `POST /login` - Validate voucher and grant access
- `GET /status` - Check user session status
- `POST /logout` - End session

#### Admin
- `POST /admin/login` - Admin authentication
- `GET /admin/dashboard` - Admin interface
- `GET /admin/api/stats` - Get system statistics
- `GET /admin/api/vouchers` - List vouchers
- `POST /admin/api/vouchers` - Create new vouchers
- `GET /admin/api/sessions` - List active sessions
- `POST /admin/api/sessions/<id>/disconnect` - Disconnect user
- `GET /admin/api/logs` - Get system logs

## Database Schema

### Vouchers Table
- `id` - Primary key
- `code` - Unique voucher code
- `allowed_minutes` - Connection duration
- `status` - unused/used/disabled
- `user_info` - Optional user information
- `created_at` - Creation timestamp
- `used_at` - When voucher was used

### Sessions Table
- `id` - Primary key
- `voucher_id` - Foreign key to voucher
- `user_ip` - Client IP address
- `user_mac` - Client MAC address
- `start_time` - Session start
- `expiry_time` - Session end time
- `bandwidth_limit_mbps` - Optional bandwidth limit
- `is_active` - Current session status
- `end_time` - Actual end time

### Logs Table
- `id` - Primary key
- `session_id` - Related session
- `event_type` - login/expired/disconnect/etc
- `user_ip` - Client IP
- `details` - Event details
- `timestamp` - Event time

## Troubleshooting

### Clients Can't Connect
- Check hostapd is running: `sudo systemctl status hostapd`
- Check dnsmasq is running: `sudo systemctl status dnsmasq`
- Verify interface is up: `ip addr show wlan1_ap`

### No Internet Access
- Check IP forwarding: `cat /proc/sys/net/ipv4/ip_forward` (should be 1)
- Check NAT rules: `sudo iptables -t nat -L -n -v`
- Ensure primary interface (wlan1) is connected

### Captive Portal Not Showing
- Check iptables redirect: `sudo iptables -t nat -L PREROUTING -n -v`
- Verify Flask is running on port 8080
- Try accessing directly: `http://192.168.10.1:8080`

### Sessions Not Expiring
- Check auto-expiry daemon: `ps aux | grep auto_expiry`
- Check database time: `python3 -c "from datetime import datetime; print(datetime.utcnow())"`
- View logs: `SELECT * FROM logs WHERE event_type='auto_expired';`

## Security Considerations

1. **Change Default Credentials**: Edit `config/settings.py` and set strong admin password
2. **Use HTTPS**: Deploy with SSL/TLS in production
3. **Validate Input**: All user input is validated before processing
4. **Database**: Use strong encryption for sensitive data in production
5. **Firewall**: Restrict access to admin panel to trusted networks

## Optional Enhancements

1. **Bandwidth Limiting**: Use `tc` (traffic control) for per-user limits
2. **MAC Address Filtering**: Whitelist/blacklist MAC addresses
3. **Multi-AP Setup**: Run multiple instances for scaling
4. **Analytics**: Add graphing and usage reports
5. **Mobile App**: Create dedicated mobile app for voucher redemption
6. **SMS Notifications**: Send expiry notifications to users
7. **Integration**: Connect to payment gateway for paid vouchers

## Production Deployment

For production deployment:

1. Use production WSGI server (gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 run:app
   ```

2. Use PostgreSQL instead of SQLite

3. Set `DEBUG = False` in `config/settings.py`

4. Use proper SSL certificates

5. Run auto-expiry as systemd service

6. Use system firewall (UFW) instead of manual iptables

7. Monitor with tools like Prometheus + Grafana

## License

This project is provided as-is for educational and deployment purposes.

## Support

For issues or questions, refer to the inline code documentation and adjust configurations
based on your specific network setup.
