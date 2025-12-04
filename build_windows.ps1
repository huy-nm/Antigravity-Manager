# build_windows.ps1

Write-Host "🚀 Starting AI Tools Manager build (Windows)..." -ForegroundColor Cyan

# 1. Checking environment
if (-not (Get-Command "flet" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ flet command not found, installing..." -ForegroundColor Yellow
    pip install flet
}
if (-not (Get-Command "pyinstaller" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ pyinstaller command not found, installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Install project dependencies
if (Test-Path "requirements.txt") {
    Write-Host "📦 Installing/updating project dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

# 2. Clean up old builds
Write-Host "🧹 Cleaning old build files..." -ForegroundColor Green
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

# 3. Prepare resources
# Ensure gui/assets exists and is up to date
Write-Host "📦 Syncing resource files..." -ForegroundColor Green
if (-not (Test-Path "gui/assets")) { New-Item -ItemType Directory -Path "gui/assets" | Out-Null }
Copy-Item "assets/*" "gui/assets/" -Recurse -Force

# 4. Execute build
Write-Host "🔨 Starting compilation..." -ForegroundColor Green

# Use flet pack to package
# --icon: Specify icon
# --add-data: Add resource files (format: source;destination)
# --name: Specify output filename
# --noconsole: Do not show console window (remove this parameter if debugging is needed)
# gui/main.py: Entry file

# 4. Execute PyInstaller packaging
Write-Host "📦 Packaging..." -ForegroundColor Yellow

# Packaging directly with PyInstaller
# --onefile: Package as single file
# --windowed: No console (GUI app)
# --add-data: Add resource files (format: source;destination)
# --hidden-import: Force import of modules that might be missed
pyinstaller --noconfirm --onefile --windowed --clean `
    --name "AI Tools Manager" `
    --icon "assets/icon.ico" `
    --add-data "assets;assets" `
    --add-data "gui;gui" `
    --noconsole `
    --paths "gui" `
    --hidden-import "views" `
    --hidden-import "views.home_view" `
    --hidden-import "views.settings_view" `
    --hidden-import "account_manager" `
    --hidden-import "db_manager" `
    --hidden-import "process_manager" `
    --hidden-import "utils" `
    --hidden-import "theme" `
    --hidden-import "icons" `
    "gui/main.py"

# Check result
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Packaging failed!" -ForegroundColor Red
    exit 1
}

# 5. Check result
if (Test-Path "dist/AI Tools Manager.exe") {
    Write-Host "`n🎉 Build successful!" -ForegroundColor Green
    Write-Host "File location: dist/AI Tools Manager.exe" -ForegroundColor Cyan
} else {
    Write-Host "❌ Generated exe file not found" -ForegroundColor Red
    exit 1
}
