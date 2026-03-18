Absolutely! I’ve combined **everything into a single Markdown file** so you can save it as, for example, `hotspot_billing_system.md`. It includes the system overview, network setup, captive portal, voucher system, auto-expiry, admin panel, and the Cursor AI task list—all in one file.

---

````markdown
# Hotspot Billing System Specification & Cursor AI Task List

---

## 1. System Overview

This hotspot billing system uses a voucher-based captive portal with auto-expiry.

**Main Components:**
1. **Internet Input (`wlan1`)** – connects to Airtel WiFi.
2. **Hotspot Output (`wlan1_ap`)** – virtual AP for clients.
3. **Captive Portal / Voucher System** – HTTP redirection for login.
4. **Auto-expiry System** – revokes access when voucher expires.
5. **Admin Panel** – web interface for monitoring and management.

---

## 2. Network Setup

### 2.1 Interfaces
- **wlan1 (Client)** – connects to Airtel WiFi.
- **wlan1_ap (AP)** – virtual interface broadcasting hotspot.

### 2.2 Network Services
- **NAT + IP Forwarding** – allows clients to use the internet.
- **DHCP Server** – assigns local IPs (192.168.10.x).
- **Firewall (iptables)** – manages access per user and enforces auto-expiry rules.

**Important:** If using a single WiFi card, AP channel must match the upstream WiFi channel.

---

## 3. Captive Portal

### 3.1 Workflow
1. User connects to `wlan1_ap`.
2. DHCP assigns temporary IP.
3. HTTP requests redirected to login page.
4. User enters voucher code.
5. Backend validates voucher:
   - Valid → grants internet for limited time.
   - Invalid → shows error.
6. Store session start time and expiry in DB.
7. Firewall rules applied per user IP.

### 3.2 Features
- Optional: Bandwidth limits per voucher.
- Log user sessions (IP, MAC, start/end).

---

## 4. Voucher System

### 4.1 Database
- SQLite (or MySQL/PostgreSQL).
- Table: `vouchers`
  - `code` (TEXT, UNIQUE)
  - `allowed_minutes` (INTEGER)
  - `status` (TEXT: unused/used)
  - Optional: `user_info` (TEXT)

### 4.2 Workflow
1. Admin creates voucher.
2. User enters voucher at captive portal.
3. System calculates expiry.
4. Access granted via firewall rules.
5. Auto-expiry revokes access.

---

## 5. Auto-Expiry Mechanism

- Background process runs every 30 seconds.
- Checks all active sessions.
- Compares current time with `expiry_time`.
- Revokes access by removing firewall rules.
- Logs expired sessions.

---

## 6. Admin Panel

### 6.1 Dashboard
- Active users
- Bandwidth usage per user
- Voucher statistics (used/unused)

### 6.2 Voucher Management
- Create, delete, disable vouchers
- Export vouchers for printing/email

### 6.3 User Management
- List active users (IP, start time, expiry)
- Disconnect user manually
- Search by IP or voucher

### 6.4 System Monitoring
- Hotspot status
- Logs of connections/disconnections
- Optional: Bandwidth/session graphs

**Security:** Protected with username/password. Use HTTPS if possible.

---

## 7. Workflow Summary

1. User connects → DHCP IP assigned.
2. Redirected to captive portal → voucher entered.
3. System validates voucher → internet granted.
4. Auto-expiry task revokes access after expiry.
5. Admin panel allows monitoring and manual intervention.

---

## 8. Key Design Considerations

- **Stability:** Prefer two WiFi adapters for large deployments.
- **Security:** Prevent users from bypassing captive portal.
- **Scalability:** ~15 users per WiFi card; add extra adapters for more.
- **Logging:** Track voucher usage and IPs for accountability.
- **Ease of Use:** Simple, clear login page and messages.

---

## 9. Cursor AI Task List

> Each task is actionable and sequential.

### 9.1 System Preparation
1. Install required software:
   - `hostapd`, `dnsmasq`, `iptables`, Python 3 + pip
   - Web framework (Flask or Django)
   - SQLite (or MySQL/PostgreSQL)
2. Test `wlan1` supports AP + client mode.

### 9.2 Network Configuration
1. Configure `wlan1` as client.
2. Create `wlan1_ap` in AP mode.
3. Set AP SSID and channel.
4. Enable IP forwarding:
   ```bash
   echo 1 > /proc/sys/net/ipv4/ip_forward
````

5. Configure NAT:

   ```bash
   iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
   ```
6. Configure `dnsmasq`:

   * IP range: 192.168.10.10–192.168.10.50
   * Gateway: 192.168.10.1

### 9.3 Captive Portal

1. Create HTML login page for voucher input.
2. Redirect all HTTP requests to login page:

   ```bash
   iptables -t nat -A PREROUTING -i wlan1_ap -p tcp --dport 80 -j REDIRECT --to-port 8080
   ```
3. Implement backend API:

   * Verify voucher
   * Grant/deny access
4. Apply firewall rules per user IP on successful login.

### 9.4 Voucher System

1. Create `vouchers` table in DB.
2. Implement voucher creation script.
3. Implement voucher validation API:

   * Mark voucher as used
   * Record session start and expiry

### 9.5 Auto-Expiry

1. Create Python script to:

   * Check active sessions every 30s
   * Remove firewall rules for expired sessions
   * Log expired sessions
2. Run as background service/daemon.

### 9.6 Admin Panel

1. Build web interface with:

   * Dashboard, voucher management, user management, logs
2. Protect with username/password authentication
3. Optional: display graphs for bandwidth/session duration

### 9.7 Logging & Monitoring

1. Log all voucher usage: IP, MAC, start/end times.
2. Log failed login attempts.
3. Optional: real-time hotspot monitoring.

### 9.8 Optional Enhancements

1. Bandwidth limits per user (iptables/tc)
2. HTTPS support for captive portal
3. Multi-AP setup for scaling
4. Export detailed usage reports

### 9.9 Testing & Validation

1. Connect multiple devices to `wlan1_ap`.
2. Test voucher login and internet access.
3. Verify auto-expiry works.
4. Test admin panel: voucher creation, monitoring, disconnect.
5. Confirm logs capture all sessions.

---

**End of Hotspot Billing System Specification & Task List**

```

---

If you want, I can also **add a network flow diagram in Markdown + ASCII** so the Cursor AI can “visualize” the entire hotspot workflow before building. It makes it much easier for step-by-step implementation.  

Do you want me to add that diagram?
```
