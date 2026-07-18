#!/bin/bash
[ "$EUID" -ne 0 ] && exit 1
DIR="/opt/edl"

if [ -f /etc/arch-release ]; then
    pacman -Syu --noconfirm android-tools python python-pip git xz
    pacman -Rns --noconfirm modemmanager || true
elif [ -f /etc/debian_version ]; then
    apt update && apt install -y adb fastboot python3-dev python3-pip liblzma-dev git
    apt purge -y modemmanager
elif [ -f /etc/fedora-release ]; then
    dnf install -y adb fastboot python3-devel python3-pip xz-devel git
fi

systemctl stop ModemManager
systemctl disable ModemManager

mkdir -p "$DIR"
git clone https://github.com/bkerler/edl.git "$DIR"
cd "$DIR"
git submodule update --init --recursive

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install .

chmod +x autoinstall.sh
./autoinstall.sh

ln -sf "$DIR/venv/bin/edl" /usr/local/bin/edl
chmod +x /usr/local/bin/edl
