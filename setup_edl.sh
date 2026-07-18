#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Ejecuta con sudo."
    exit 1
fi

echo "[*] Preparando sistema..."

if [ -f /etc/debian_version ]; then
    apt update
    apt install -y adb fastboot python3-dev python3-pip liblzma-dev git
    apt purge -y modemmanager
elif [ -f /etc/fedora-release ]; then
    dnf install -y adb fastboot python3-devel python3-pip xz-devel git
elif [ -f /etc/arch-release ]; then
    pacman -Syu --noconfirm android-tools python python-pip git xz
    pacman -Rns --noconfirm modemmanager
fi

systemctl stop ModemManager
systemctl disable ModemManager

INSTALL_DIR="/opt/edl"
mkdir -p $INSTALL_DIR

echo "[*] Descargando edl..."
cd $INSTALL_DIR
git clone https://github.com/bkerler/edl.git .
git submodule update --init --recursive

echo "[*] Instalando..."
pip3 install -r requirements.txt
pip3 install .

chmod +x autoinstall.sh
./autoinstall.sh

echo "[*] Instalación completada."
