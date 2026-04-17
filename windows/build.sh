#!/bin/bash
shopt -s extglob

echo " - Installing MSYS2 dependencies..."
pacman -S --noconfirm --needed \
    mingw-w64-ucrt-x86_64-python \
    mingw-w64-ucrt-x86_64-gtk4 \
    mingw-w64-ucrt-x86_64-libadwaita \
    mingw-w64-ucrt-x86_64-python-gobject \
    mingw-w64-ucrt-x86_64-python-pip \
    mingw-w64-ucrt-x86_64-pyinstaller \
    mingw-w64-ucrt-x86_64-upx \
    mingw-w64-ucrt-x86_64-7zip \
    mingw-w64-ucrt-x86_64-cmake \
    mingw-w64-ucrt-x86_64-ninja \
    mingw-w64-ucrt-x86_64-meson \
    mingw-w64-ucrt-x86_64-toolchain \
    base-devel \
    unzip

echo " - Setting up Python virtual environment..."
cd src
python -m venv venv
source venv/bin/activate

echo " - Installing Python packages..."
pip install --upgrade pip
pip install -r ../requirements.txt

echo " - Building Windows executable with PyInstaller..."
pyinstaller ../windows/grassy.spec

echo " - Build complete."
echo " - Executable: src/dist/grassy.exe"
