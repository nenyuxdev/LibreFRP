#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Ejecuta con sudo."
    exit 1
fi

echo "[*] Preparando sistema..."

if [ -f /etc/debian_version ]; then
    apt update
    apt install -y git python3 python3-pip libusb-1.0-0-dev
elif [ -f /etc/fedora-release ]; then
    dnf install -y git python3 python3-pip libusb1
elif [ -f /etc/arch-release ]; then
    pacman -Syu --noconfirm git python python-pip libusb
fi

INSTALL_DIR="/opt/mtkclient"
mkdir -p $INSTALL_DIR

echo "[*] Descargando mtkclient..."
git clone https://github.com/bkerler/mtkclient.git $INSTALL_DIR
cd $INSTALL_DIR
git submodule update --init --recursive

echo "[*] Instalando..."
pip3 install -r requirements.txt
pip3 install .

echo "[*] Configurando reglas y permisos..."
cp Setup/Linux/*.rules /etc/udev/rules.d/
udevadm control -R && udevadm trigger

usermod -aG plugdev,dialout "$SUDO_USER"

echo "[*] Instalación completada."
echo "[!] Reinicia tu sesión para aplicar los cambios de grupo."
