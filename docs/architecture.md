# Architecture

| Device | Model | IP Address | Role |
|--------|-------|-----------|------|
| Pi 5 | Raspberry Pi 5 (8GB) | 192.168.50.1 | Master node, backend, Hailo AI HAT+ |
| Pi 4 | Raspberry Pi 4 (4GB) | 192.168.50.98 | Camera node (IMX500) + ZeroMQ sender |
| Pi 3-1 | Raspberry Pi 3B (1GB) | 192.168.50.91 | Worker node |
| Pi 3-2 | Raspberry Pi 3B (1GB) | 192.168.50.92 | Worker node |
| Pi 3-3 | Raspberry Pi 3B (1GB) | 192.168.50.93 | Worker node |
| Pi 3-4 | Raspberry Pi 3B (1GB) | 192.168.50.94 | Worker node |
| Pi 3-5 | Raspberry Pi 3B (1GB) | 192.168.50.95 | Worker node |
| Pi 3-6 | Raspberry Pi 3B (1GB) | 192.168.50.96 | Worker node |
| Pi 3-7 | Raspberry Pi 3B (1GB) | 192.168.50.97 | Worker node |
| Switch | TP-Link TL-SG108E | 192.168.50.104 | 8-port Gigabit switch |

### Additional Hardware
- **Hailo AI HAT+** (8L, 13 TOPS) — connected to Pi 5 via PCIe
- **Sony IMX500 AI Camera Module** — connected to Pi 4
- **NVMe SSD (500GB)** — connected to Pi 5 for MinIO storage
- **Gigabit Ethernet switch** — TL-SG108E connecting all nodes

### SSH Credentials

| Device | Username | Password |
|--------|----------|---------|
| Pi 5 | pi | < hidden > |
| Pi 3-1 | pi3-1    | < hidden > |
| Pi 3-2 | pi3-2    | < hidden > |
| Pi 3-3 | pi3-3    | < hidden > |
| Pi 3-4 | pi3-4    | < hidden > |
| Pi 3-5 | pi3-5    | < hidden > |
| Pi 3-6 | pi3-6    | < hidden > |
| Pi 3-7 | pi3-7    | < hidden > |
| Pi 4   | pi       | < hidden > |

---

---

All nodes are connected via a private Gigabit LAN on the 192.168.50.0/24 subnet.

### DHCP/DNS Server (dnsmasq on Pi 5)

Pi 5 acts as DHCP server for the entire cluster. Configuration at `/etc/dnsmasq.conf`:

```
interface=eth0
bind-interfaces
dhcp-range=192.168.50.50,192.168.50.150,12h
dhcp-host=b8:27:eb:4b:43:2c,192.168.50.91,pi3-1
dhcp-host=b8:27:eb:39:15:74,192.168.50.92,pi3-2
dhcp-host=b8:27:eb:e7:78:92,192.168.50.93,pi3-3
dhcp-host=b8:27:eb:31:7a:10,192.168.50.94,pi3-4
dhcp-host=b8:27:eb:d4:aa:d7,192.168.50.95,pi3-5
dhcp-host=b8:27:eb:a5:ff:f4,192.168.50.96,pi3-6
dhcp-host=b8:27:eb:e3:a8:e9,192.168.50.97,pi3-7
```

### MAC Address Table

| Hostname | MAC Address | IP |
|----------|------------|-----|
| pi3-1 | b8:27:eb:4b:43:2c | 192.168.50.91 |
| pi3-2 | b8:27:eb:39:15:74 | 192.168.50.92 |
| pi3-3 | b8:27:eb:e7:78:92 | 192.168.50.93 |
| pi3-4 | b8:27:eb:31:7a:10 | 192.168.50.94 |
| pi3-5 | b8:27:eb:d4:aa:d7 | 192.168.50.95 |
| pi3-6 | b8:27:eb:a5:ff:f4 | 192.168.50.96 |
| pi3-7 | b8:27:eb:e3:a8:e9 | 192.168.50.97 |

### Static IP for Pi 5 eth0

Pi 5's ethernet interface must have a static IP. Configured via NetworkManager:

```bash
sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.50.1/24 ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

### Internet Sharing (NAT)

Pi 5 shares internet from wlan1 to all Pi 3s via NAT:

```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
sudo iptables -I FORWARD 1 -i eth0 -o wlan1 -j ACCEPT
sudo iptables -I FORWARD 2 -i wlan1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

### Passwordless SSH

SSH keys are distributed from Pi 5 to all Pi 3s:

```bash
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
for i in 1 2 3 4 5 6 7; do
  sshpass -p "$PI_PASSWORD" ssh-copy-id -o StrictHostKeyChecking=no pi3-$i@192.168.50.$((90+i))
done
```

---
