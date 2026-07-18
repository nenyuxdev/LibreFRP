# LibreFRP

LibreFRP es una Interfaz de Usuario de Terminal (TUI) ligera, escrita en Python, diseñada para automatizar tareas de servicio técnico (como bypass de FRP) en dispositivos MediaTek (MTK) y Qualcomm.

Esta herramienta actúa como un frontend limpio para `mtkclient` y `edl`, eliminando la necesidad de escribir comandos largos y manejando los privilegios de root de forma segura.

## ⚠️ Requisitos previos

Para que la herramienta funcione correctamente, debes tener instalados en tu sistema:
- **Python 3.x**
- **mtkclient**: Instalado y accesible en el PATH.
- **edl**: (Qualcomm Firehose/Sahara Client) instalado.
- **usbutils**: Para la detección de dispositivos (`lsusb`).

## 🚀 Instalación

1. Clona el repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/LibreFRP.git](https://github.com/TU_USUARIO/LibreFRP.git)
   cd LibreFRP
