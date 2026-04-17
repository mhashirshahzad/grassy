#!/bin/sh
set -eu

ARCH=$(uname -m)
VERSION=$(git describe --tags --always || echo "dev")
export ARCH VERSION
export OUTPATH=./dist
export ADD_HOOKS="self-updater.hook"
export UPINFO="gh-releases-zsync|${GITHUB_REPOSITORY%/*}|${GITHUB_REPOSITORY#*/}|latest|*$ARCH.AppImage.zsync"

# --- Required metadata (CHANGE THESE to match your app) ---
export ICON=/usr/share/icons/hicolor/scalable/apps/io.github.yourusername.grassy.svg
export DESKTOP=/usr/share/applications/io.github.yourusername.grassy.desktop

# --- Deployment options ---
export DEPLOY_PYTHON=1
export DEPLOY_GTK=1
export GTK_DIR=gtk-4.0
export DEPLOY_LOCALE=1
export STARTUPWMCLASS=io.github.yourusername.grassy   # Change to your app's WM class
export GTK_CLASS_FIX=1

# --- List all binaries and data your app needs ---
quick-sharun /usr/bin/grassy \          # Your main executable (if installed)
             /usr/lib/python3.*/site-packages/grassy \   # If your app is a module
             /usr/share/grassy \         # Additional data files
             /usr/bin/requests \         # Not needed, just example
             /usr/lib/libgobject* \
             /usr/lib/libglib* \
             /usr/lib/libgtk* \
             /usr/lib/libadwaita* \
             /usr/lib/girepository* \
             /usr/lib/libgirepository*

# --- If your app is a single Python script (not installed system-wide) ---
# Copy your script and any local modules into AppDir
mkdir -p ./AppDir/bin
cp /path/to/your/grassy.py ./AppDir/bin/grassy
chmod +x ./AppDir/bin/grassy

# Create a wrapper script that runs Python with the correct environment
cat << 'EOF' > ./AppDir/AppRun
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="${HERE}/usr/lib/python3.12/site-packages:${PYTHONPATH:-}"
exec "${HERE}/bin/python3" "${HERE}/bin/grassy" "$@"
EOF
chmod +x ./AppDir/AppRun

# --- Turn AppDir into AppImage ---
quick-sharun --make-appimage

# --- Test the final app ---
quick-sharun --test ./dist/*.AppImage
