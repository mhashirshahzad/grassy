#!/bin/bash
shopt -s extglob

# --- Configuration ---
# (No external binaries like aria2/ffmpeg needed for Grassy)
# Just ensure Python and GTK dependencies are installed

# --- Install MSYS2 Dependencies ---
echo " - Installing dependencies..."
pacman -S --noconfirm --needed \
    mingw-w64-ucrt-x86_64-python \
    mingw-w64-ucrt-x86_64-gtk4 \
    mingw-w64-ucrt-x86_64-libadwaita \
    mingw-w64-ucrt-x86_64-python-gobject \
    mingw-w64-ucrt-x86_64-python-pip \
    mingw-w64-ucrt-x86_64-pyinstaller \
    mingw-w64-ucrt-x86_64-upx \
    mingw-w64-ucrt-x86_64-7zip \
    unzip

# --- Install Python Dependencies ---
echo " - Installing Python packages..."
pip install -r requirements.txt

# --- Build with PyInstaller ---
echo " - Building Windows executable..."
cd src
# Use a PyInstaller spec file for better control (see step 2)
pyinstaller grassy.spec
cd ..

echo " - Build complete."
echo " - Executable can be found in src/dist/grassy/"
