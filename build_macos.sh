#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting AI Tools Manager build (macOS)..."

# 1. Sync resource files
echo "📦 Syncing resource files..."
# Ensure gui/assets directory exists
mkdir -p gui/assets
# Sync assets directory content to gui/assets
cp -R assets/* gui/assets/
# Sync requirements.txt
cp requirements.txt gui/requirements.txt

# 2. Clean up old builds
echo "🧹 Cleaning up old build files..."
rm -rf gui/build/macos

# 3. Execute build
echo "🔨 Starting compilation..."
source .venv/bin/activate
cd gui

# Temporarily disable set -e because flet build might throw a SystemExit: 0 traceback but actually succeed
set +e

# Ensure not entering interactive mode
unset PYTHONINSPECT

# Use python -c to call flet_cli directly, bypassing possible entry point issues, and redirect input
python -c "import sys; from flet.cli import main; main()" build macos \
    --product "AI Tools Manager" \
    --org "com.ctrler.antigravity" \
    --copyright "" \
    --build-version "1.0.0" \
    --desc "Antigravity Account Manager" < /dev/null
EXIT_CODE=$?
set -e

# Return to root directory
cd ..

# 4. Check build artifacts and package DMG
APP_NAME="AI Tools Manager"
APP_PATH="gui/build/macos/$APP_NAME.app"
DMG_NAME="$APP_NAME.dmg"
OUTPUT_DMG="gui/build/macos/$DMG_NAME"

if [ -d "$APP_PATH" ]; then
    echo "✅ App bundle detected, build successful (ignoring Flet CLI exit status)"
else
    echo "❌ Build failed, app bundle not found"
    exit $EXIT_CODE
fi

echo "📦 Creating DMG installer..."

# Create temporary directory for DMG creation
DMG_SOURCE="gui/build/macos/dmg_source"
rm -rf "$DMG_SOURCE"
mkdir -p "$DMG_SOURCE"

# Copy app to temporary directory
echo "📋 Copying app to temporary directory..."
cp -R "$APP_PATH" "$DMG_SOURCE/"

# Create Applications symlink
ln -s /Applications "$DMG_SOURCE/Applications"

# Use hdiutil to create DMG
echo "💿 Creating DMG file..."
rm -f "$OUTPUT_DMG"
TEMP_DMG="gui/build/macos/temp.dmg"
rm -f "$TEMP_DMG"

# Step 1: Create read-write DMG
hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_SOURCE" -ov -format UDRW "$TEMP_DMG"

# Step 2: Convert to compressed read-only DMG
hdiutil convert "$TEMP_DMG" -format UDZO -o "$OUTPUT_DMG"

# Cleanup
rm -f "$TEMP_DMG"
rm -rf "$DMG_SOURCE"

echo "🎉 Packaging complete!"
echo "📂 App location: $APP_PATH"
echo "💿 DMG file: $OUTPUT_DMG"
