# Raspberry Pi 4 PXE Boot Server Setup

## Architecture

| Device         | Role                           |
| -------------- | ------------------------------ |
| Raspberry Pi 4 | PXE / DHCP / TFTP / NFS Server |
| Raspberry Pi 3 | PXE Boot Client                |
| TP-Link Switch | Network Switch                 |

---

# Network Layout

Pi4:

- eth0 → Static PXE Network
- wlan0 → Internet/WiFi

Pi3:

- Connected to switch
- Boots without SD card

---

# STEP 1 — Install Required Packages

Update system:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y dnsmasq nfs-kernel-server rsync tcpdump
```

# STEP 2 - Configure Static Ethernet IP

```bash
sudo nano /etc/dhcpcd.conf
```

add this

```bash
interface eth0
static ip_address=192.168.50.1/24
```

reboot

```bash
sudo reboot
```

verify the static ip

```bash
ip a
```

# STEP 3 — Create TFTP Directory

```bash
sudo mkdir -p /srv/tftp
```

# STEP 4 — Create NFS Root

```bash
sudo mkdir -p /nfs/piroot
```

# STEP 5 — Copy Raspberry Pi Filesystem

```bash
sudo rsync -xa --progress / /nfs/piroot \
--exclude /nfs/piroot \
--exclude /proc \
--exclude /sys \
--exclude /dev \
--exclude /tmp \
--exclude /run \
--exclude /mnt \
--exclude /media \
--exclude /lost+found
```

# STEP 6 — Configure NFS

```bash
sudo nano /etc/exports
```

add this

```bash
/nfs/piroot *(rw,sync,no_subtree_check,no_root_squash)
```

run this

```bash
sudo exportfs -rv
sudo systemctl restart nfs-kernel-server
```

# STEP 7 — Copy Boot Files

```bash
sudo cp -r /boot/firmware/* /srv/tftp/
```

# STEP 8 — Configure cmdline.txt

```bash
sudo nano /srv/tftp/cmdline.txt
```

add this:

```bash
console=serial0,115200 console=tty1 root=/dev/nfs nfsroot=192.168.50.1:/nfs/piroot,vers=3,tcp rw ip=dhcp rootwait rootdelay=10 elevator=deadline fsck.repair=yes rootfstype=nfs init=/sbin/init
```

# STEP 9 — Configure dnsmasq

```bash
sudo nano /etc/dnsmasq.conf
```

add this:

```bash
interface=eth0
bind-interfaces

dhcp-range=192.168.50.50,192.168.50.150,255.255.255.0,24h

enable-tftp
tftp-root=/srv/tftp

pxe-service=0,"Raspberry Pi Boot"

dhcp-boot=bootcode.bin
```

run

```bash
sudo systemctl restart dnsmasq
sudo systemctl status dnsmasq
sudo journalctl -fu dnsmasq
```

connect hardware
first start pi5 and turn on switch and wait 35 second and turn on pi3s and watch logs
