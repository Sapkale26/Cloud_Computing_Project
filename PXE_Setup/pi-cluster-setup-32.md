# Raspberry Pi Cluster — PXE Boot Setup Documentation

## Cloud Computing Course SS2026

---

## Hardware

| Device                     | Role                    | OS                     | IP               |
| -------------------------- | ----------------------- | ---------------------- | ---------------- |
| Raspberry Pi 5 (8GB)       | Master node             | Raspberry Pi OS 64-bit | 192.168.50.1     |
| Raspberry Pi 4             | Sensor node             | —                      | —                |
| Raspberry Pi 3B x7         | Worker nodes            | 32-bit via NFS/PXE     | 192.168.50.91–97 |
| TL-SG108E 8-port switch    | Network backbone        | —                      | 192.168.50.55    |
| WD Black SN7100 NVMe 500GB | Fast storage (NFS+TFTP) | —                      | /mnt/nvme        |

---

## Network Topology

```
Internet
    |
    | (WiFi - 5GHz)
    |
[Pi 5 Master]  192.168.50.1
    |
    | (Ethernet)
    |
[TL-SG108E Switch]
    |----[Pi 3 - pi3-1]  192.168.50.91
    |----[Pi 3 - pi3-2]  192.168.50.92
    |----[Pi 3 - pi3-3]  192.168.50.93
    |----[Pi 3 - pi3-4]  192.168.50.94
    |----[Pi 3 - pi3-5]  192.168.50.95
    |----[Pi 3 - pi3-6]  192.168.50.96
    |----[Pi 3 - pi3-7]  192.168.50.97
```

---

## Overview

All 7 Raspberry Pi 3B worker nodes boot entirely over the network using **PXE boot**. They have no operating system on their SD cards — only a minimal `bootcode.bin` file to initiate the PXE boot process.

The boot process:

1. Pi 3 powers on, reads `bootcode.bin` from SD card
2. Pi 3 sends DHCP broadcast over ethernet
3. Pi 5 (dnsmasq) assigns IP and points to TFTP server
4. Pi 3 downloads kernel and boot files via TFTP
5. Pi 3 mounts root filesystem from Pi 5 via NFS
6. Pi 3 boots fully from NFS root on Pi 5's NVMe SSD

---

## Pi 5 Setup

### 1. NVMe SSD Setup

Mount the NVMe SSD and create directories:

```bash
sudo mkfs.ext4 /dev/sda
sudo mkdir -p /mnt/nvme
sudo mount /dev/sda /mnt/nvme
echo '/dev/sda /mnt/nvme ext4 defaults 0 2' | sudo tee -a /etc/fstab

sudo mkdir -p /mnt/nvme/nfs/piroot
sudo mkdir -p /mnt/nvme/tftp
```

Create symlinks:

```bash
sudo ln -s /mnt/nvme/tftp /srv/tftp
sudo ln -s /mnt/nvme/nfs/piroot /nfs/piroot
```

### 2. Download and Mount Raspberry Pi OS (32-bit)

```bash
wget -O /tmp/raspios.img.xz https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2024-11-19/2024-11-19-raspios-bookworm-armhf-lite.img.xz
xz -d /tmp/raspios.img.xz

sudo losetup -fP /tmp/raspios.img
sudo mkdir -p /mnt/pi3boot /mnt/pi3root
sudo mount /dev/loop1p1 /mnt/pi3boot
sudo mount /dev/loop1p2 /mnt/pi3root
```

### 3. Copy Boot and Root Filesystems

```bash
sudo rsync -xa --progress /mnt/pi3boot/ /mnt/nvme/tftp/
sudo rsync -xa --progress /mnt/pi3root/ /mnt/nvme/nfs/piroot/
```

### 4. Fix fstab in NFS Root

```bash
sudo nano /mnt/nvme/nfs/piroot/etc/fstab
```

Comment out PARTUUID lines:

```
proc            /proc           proc    defaults          0       0
#PARTUUID=xxxxxxxx-01  /boot/firmware  vfat    defaults  0       2
#PARTUUID=xxxxxxxx-02  /               ext4    defaults  0       1
```

### 5. Configure cmdline.txt for NFS Boot

```bash
sudo nano /mnt/nvme/tftp/cmdline.txt
```

Content:

```
console=serial0,115200 console=tty1 root=/dev/nfs nfsroot=192.168.50.1:/mnt/nvme/nfs/piroot,vers=3,tcp rw ip=dhcp rootwait rootdelay=60 elevator=deadline fsck.repair=yes rootfstype=nfs init=/sbin/init
```

### 6. Install Required Services

```bash
sudo apt update
sudo apt install -y dnsmasq nfs-kernel-server
```

### 7. Configure dnsmasq (DHCP + TFTP)

`/etc/dnsmasq.conf`:

```ini
interface=eth0
bind-interfaces
dhcp-range=192.168.50.50,192.168.50.150,12h
enable-tftp
tftp-root=/srv/tftp
dhcp-boot=bootcode.bin
dhcp-option=66,192.168.50.1
dhcp-option=17,/nfs/piroot
dhcp-host=b8:27:eb:39:15:74,192.168.50.91,pi3-1
dhcp-host=b8:27:eb:e7:78:92,192.168.50.92,pi3-2
dhcp-host=b8:27:eb:4b:43:2c,192.168.50.93,pi3-3
dhcp-host=b8:27:eb:d4:aa:d7,192.168.50.94,pi3-4
dhcp-host=b8:27:eb:06:07:55,192.168.50.95,pi3-5
dhcp-host=b8:27:eb:31:7a:10,192.168.50.96,pi3-6
dhcp-host=b8:27:eb:e3:a8:e9,192.168.50.97,pi3-7
tftp-max=100
```

```bash
sudo systemctl enable dnsmasq
sudo systemctl restart dnsmasq
```

### 8. Configure NFS Exports

`/etc/exports`:

```
/mnt/nvme/nfs/piroot *(rw,sync,no_subtree_check,no_root_squash)
/mnt/nvme/tftp *(rw,sync,no_subtree_check,no_root_squash)
```

```bash
sudo exportfs -ra
sudo systemctl enable nfs-kernel-server
sudo systemctl restart nfs-kernel-server
```

### 9. Enable SSH on Pi 3s

```bash
sudo ln -s /lib/systemd/system/ssh.service \
  /mnt/nvme/nfs/piroot/etc/systemd/system/multi-user.target.wants/ssh.service
```

### 10. Create Pi User in NFS Root

Add to `/mnt/nvme/nfs/piroot/etc/passwd`:

```
pi:x:1000:1000::/home/pi:/bin/bash
```

Add to `/mnt/nvme/nfs/piroot/etc/shadow`:

```
pi:$6$rBoByrWP$4aBpNwmvnTp7t7sBJPmTlNhWKQXlGf0pVoXO3WPAe4Cjnb1yHPNASnrnc9s1bv/Np/4JjYO5v8GrWVYgz0R71:19776:0:99999:7:::
```

> Password: `raspberry`

Add to `/mnt/nvme/nfs/piroot/etc/group` — find sudo line and add pi:

```
sudo:x:27:pi
```

Create home directory:

```bash
sudo mkdir -p /mnt/nvme/nfs/piroot/home/pi
sudo chmod 755 /mnt/nvme/nfs/piroot/home/pi
```

---

## Pi 3B Setup

### 1. Enable Network Boot (OTP Burn)

On each Pi 3B (with OS SD card inserted), run:

```bash
echo "program_usb_boot_mode=1" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

Verify OTP is burned:

```bash
vcgencmd otp_dump | grep 17:
# Must show: 17:3020000a
```

Remove the line from config.txt after confirming, then remove the OS SD card.

### 2. Prepare SD Card for PXE Boot

Format a small SD card as FAT32 and copy only `bootcode.bin`:

```bash
# On Pi 5 via USB SD card reader:
sudo mkfs.vfat /dev/sdX
sudo mount /dev/sdX /mnt/sdcard
sudo cp /mnt/nvme/tftp/bootcode.bin /mnt/sdcard/
sudo umount /mnt/sdcard
```

Insert this minimal SD card into each Pi 3B.

---

## File Structure on Pi 5

```
/mnt/nvme/
├── tftp/                    # TFTP boot files (symlinked from /srv/tftp)
│   ├── bootcode.bin         # Pi 3 bootloader
│   ├── start.elf            # GPU firmware
│   ├── fixup.dat            # GPU firmware fix
│   ├── kernel7.img          # Linux kernel (32-bit ARMv7)
│   ├── initramfs7           # Initial RAM filesystem
│   ├── cmdline.txt          # Kernel boot parameters
│   ├── config.txt           # Pi boot configuration
│   ├── bcm2710-rpi-3-b.dtb  # Device tree for Pi 3B
│   └── overlays/            # Device tree overlays
└── nfs/
    └── piroot/              # Root filesystem for all Pi 3s
        ├── bin/             # Binaries (32-bit ARM)
        ├── etc/             # Configuration files
        ├── lib/             # Libraries
        ├── home/pi/         # Pi user home
        └── ...
```

---

## MAC Address to IP Mapping

| Hostname | IP Address    | MAC Address       |
| -------- | ------------- | ----------------- |
| pi3-1    | 192.168.50.91 | b8:27:eb:39:15:74 |
| pi3-2    | 192.168.50.92 | b8:27:eb:e7:78:92 |
| pi3-3    | 192.168.50.93 | b8:27:eb:4b:43:2c |
| pi3-4    | 192.168.50.94 | b8:27:eb:d4:aa:d7 |
| pi3-5    | 192.168.50.95 | b8:27:eb:06:07:55 |
| pi3-6    | 192.168.50.96 | b8:27:eb:31:7a:10 |
| pi3-7    | 192.168.50.97 | b8:27:eb:e3:a8:e9 |

---

## Installed Software on Pi 3s

All Pi 3s share the same NFS root, so installing on one installs for all.

```bash
sudo apt-get install -y libopenmpi-dev openmpi-bin libatlas-base-dev hpcc mpich
```

| Package           | Purpose                        |
| ----------------- | ------------------------------ |
| openmpi-bin       | MPI runtime (4.1.4)            |
| libopenmpi-dev    | MPI development libraries      |
| libatlas-base-dev | Optimised BLAS/LAPACK          |
| hpcc              | HPL benchmark suite            |
| mpich             | Alternative MPI implementation |

---

## SSH Key Setup (Pi 5 → Pi 3s)

```bash
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa

for ip in 91 92 93 94 95 96 97; do
  ssh-copy-id -o StrictHostKeyChecking=no pi@192.168.50.$ip
done
```

---

## Verification Commands

Check all Pi 3s are reachable:

```bash
for ip in 91 92 93 94 95 96 97; do
  echo -n "pi3 192.168.50.$ip: "
  ping -c 1 -W 1 192.168.50.$ip > /dev/null && echo "UP" || echo "DOWN"
done
```

Check DHCP leases:

```bash
cat /var/lib/misc/dnsmasq.leases
```

Check NFS exports:

```bash
sudo exportfs -v
showmount -e localhost
```

Check TFTP is running:

```bash
sudo ss -ulnp | grep :69
```

---

## Known Issues and Solutions

| Issue                                 | Cause                      | Solution                                  |
| ------------------------------------- | -------------------------- | ----------------------------------------- |
| Pi 3 not booting via PXE              | OTP not burned             | Run `program_usb_boot_mode=1` and reboot  |
| Switch port delay causes timeout      | Switch STP/init delay      | Added `rootdelay=60` to cmdline.txt       |
| Multiple Pi 3s failing simultaneously | TFTP congestion            | Stagger power-on by 30–60 seconds         |
| NFS mount fails                       | Wrong IP in cmdline.txt    | Ensure nfsroot IP matches Pi 5's eth0 IP  |
| chroot fails from Pi 5                | 32-bit/64-bit mismatch     | Install packages directly via SSH to Pi 3 |
| MPI version mismatch                  | Pi 5 vs Pi 3 different MPI | Run MPI jobs from Pi 3-1 as master        |

---

## Current Status

- [x] Task 1: PXE boot infrastructure — **COMPLETE**
  - 7/8 Pi 3s booting reliably via network
  - NFS root on NVMe SSD
  - Static IP assignment via MAC address
- [ ] Task 2: HPL benchmark
- [ ] Task 3: MPI cluster
- [ ] Task 4: Amdahl's and Gustafson's Law
- [ ] Task 5: Monitoring
- [ ] Task 6: Object detection model
- [ ] Task 7: Kubernetes (k3s) + Docker
- [ ] Task 8: Frontend
- [ ] Task 9: Telegram bot
- [ ] Task 10: Documentation

---

## Current issue

- hpl is not working due to miss-machting of os, pi3-32, pi5-64

_Last updated: May 2026 | Frankfurt University of Applied Sciences — Cloud Computing SS2026_
