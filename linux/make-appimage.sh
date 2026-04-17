#!/bin/sh
set -eu

ARCH=$(uname -m)
if git describe --tags --always 2>/dev/null; then
    VERSION=$(git describe --tags --always)
else
    VERSION="dev"
fi
export ARCH VERSION
export OUTPATH=./dist
export ADD_HOOKS="self-updater.hook"
export UPINFO="gh-releases-zsync|${GITHUB_REPOSITORY%/*}|${GITHUB_REPOSITORY#*/}|latest|*$ARCH.AppImage.zsync"

# --- Required metadata ---
export ICON="$(pwd)/assets/icon.png"
export DESKTOP="$(pwd)/assets/grassy.desktop"

# Check if files exist
if [ ! -f "$ICON" ]; then
    echo "ERROR: Icon not found at $ICON"
    exit 1
fi
if [ ! -f "$DESKTOP" ]; then
    echo "ERROR: Desktop file not found at $DESKTOP"
    exit 1
fi
if [ ! -f "./src/main.py" ]; then
    echo "ERROR: src/main.py not found"
    exit 1
fi

# --- Deployment options ---
export DEPLOY_PYTHON=1
export DEPLOY_GTK=1
export GTK_DIR=gtk-4.0
export DEPLOY_LOCALE=1
export STARTUPWMCLASS=io.github.yourusername.grassy
export GTK_CLASS_FIX=1

# --- Create AppDir structure ---
mkdir -p ./AppDir/usr/bin
mkdir -p ./AppDir/usr/share/applications
mkdir -p ./AppDir/usr/share/icons/hicolor/256x256/apps

# Copy icon and desktop file
cp "$ICON" ./AppDir/usr/share/icons/hicolor/256x256/apps/grassy.png
cp "$ICON" ./AppDir/icon.png
cp "$ICON" ./AppDir/.DirIcon
cp "$DESKTOP" ./AppDir/usr/share/applications/
cp "$DESKTOP" ./AppDir/grassy.desktop

# Copy your Python script from src/main.py
cp ./src/main.py ./AppDir/usr/bin/grassy
chmod +x ./AppDir/usr/bin/grassy

# If you have other Python modules in src/, copy them too
if [ -d "./src/grassy" ]; then
    cp -r ./src/grassy ./AppDir/usr/lib/
fi

# --- Bundle dependencies with quick-sharun ---
# These paths work on Ubuntu 22.04/24.04 (GitHub Actions runner)
quick-sharun /usr/bin/python3 \
             /usr/lib/python3/dist-packages/gi \
             /usr/lib/python3/dist-packages/requests \
             /usr/lib/python3/dist-packages/appdirs \
             /usr/lib/x86_64-linux-gnu/libgobject-2.0* \
             /usr/lib/x86_64-linux-gnu/libglib-2.0* \
             /usr/lib/x86_64-linux-gnu/libgtk-4* \
             /usr/lib/x86_64-linux-gnu/libadwaita-1* \
             /usr/lib/x86_64-linux-gnu/girepository-1.0 \
             /usr/lib/x86_64-linux-gnu/girepository-1.0/Gio-2.0.typelib \
             /usr/lib/x86_64-linux-gnu/girepository-1.0/Gtk-4.0.typelib \
             /usr/lib/x86_64-linux-gnu/girepository-1.0/Adw-1.0.typelib \
             ./AppDir/usr/bin/grassy

# --- Create AppRun wrapper ---
cat > ./AppDir/AppRun << 'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/lib/python3/dist-packages:${PYTHONPATH:-}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH:-}"
export GI_TYPELIB_PATH="${HERE}/usr/lib/girepository-1.0:${GI_TYPELIB_PATH:-}"

# Run the application
exec "${HERE}/usr/bin/python3" "${HERE}/usr/bin/grassy" "$@"
EOF
chmod +x ./AppDir/AppRun

# --- Build the AppImage ---
quick-sharun --make-appimage

# --- Move to dist directory ---
mkdir -p dist
mv *.AppImage* dist/ 2>/dev/null || true

# --- Test the AppImage ---
if ls ./dist/*.AppImage 1>/dev/null 2>&1; then
    echo "✅ AppImage built successfully!"
    ls -la ./dist/
    
    # Optional: test it
    if command -v quick-sharun &> /dev/null; then
        quick-sharun --test ./dist/*.AppImage
    fi
else
    echo "❌ Failed to build AppImage"
    exit 1
fi
