# Troubleshooting Guide

### Pi 5 eth0 loses IP after reboot
```bash
sudo ip addr add 192.168.50.1/24 dev eth0
sudo systemctl restart dnsmasq
# Permanent fix:
sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.50.1/24 ipv4.method manual
sudo nmcli con up "Wired connection 1"
```

### dnsmasq fails to start
```bash
sudo ip addr add 192.168.50.1/24 dev eth0
sudo systemctl restart dnsmasq
sudo systemctl status dnsmasq
```

### Pi 3s unreachable
```bash
# Check if dnsmasq running
sudo systemctl status dnsmasq
# Check DHCP leases
cat /var/lib/misc/dnsmasq.leases
# Ping test
for i in 1 2 3 4 5 6 7; do
  echo -n "pi3-$i: "
  ping -c 1 -W 1 192.168.50.$((90+i)) > /dev/null 2>&1 && echo "UP" || echo "DOWN"
done
```

### Multiple backend instances running
```bash
pkill -f "node /home/pi/app/backend/server.js"
sudo kubectl scale deployment backend --replicas=0
sleep 2
node ~/app/backend/server.js &
```

### Hailo device busy
```bash
pkill -f receiver_hailo
pkill -f hailo_detect
sleep 2
python3 ~/receiver_hailo.py
```

### OpenCV missing on Pi 3s
```bash
for i in 1 2 3 4 5 6 7; do
  ssh pi3-$i@192.168.50.$((90+i)) "pip3 install opencv-python-headless --break-system-packages"
done
```

### Enable internet on Pi 3s via Pi 5 NAT
```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
sudo iptables -I FORWARD 1 -i eth0 -o wlan1 -j ACCEPT
sudo iptables -I FORWARD 2 -i wlan1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

### SSH known_hosts conflict after SD card reinstall
```bash
for ip in 91 92 93 94 95 96 97; do
  ssh-keygen -f '/home/pi/.ssh/known_hosts' -R "192.168.50.$ip"
done
```

---

*Frankfurt University of Applied Sciences — Cloud Computing SS2026 — Prof. Dr. Christian Baun — Group 8*
