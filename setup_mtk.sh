#!/bin/bash
[ "$EUID" -ne 0 ] && exit 1
DIR="/opt/mtkclient"
USER="${SUDO_USER:-$USER}"

if [ -f /etc/arch-release ]; then
    pacman -Syu --noconfirm git python python-pip libusb
elif [ -f /etc/debian_version ]; then
    apt update && apt install -y git python3 python3-pip python3-venv libusb-1.0-0-dev
elif [ -f /etc/fedora-release ]; then
    dnf install -y git python3 python3-pip libusb1
fi

mkdir -p "$DIR"
git clone https://github.com/bkerler/mtkclient.git "$DIR"
cd "$DIR"
git submodule update --init --recursive

python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
./venv/bin/pip install .

ln -sf "$DIR/venv/bin/mtk" /usr/local/bin/mtk
chmod +x /usr/local/bin/mtk

cp Setup/Linux/*.rules /etc/udev/rules.d/ 2>/dev/null || true
udevadm control -R && udevadm trigger

for g in plugdev dialout uucp; do
    if getent group "$g" >/dev/null; then usermod -aG "$g" "$USER"; fi
done
