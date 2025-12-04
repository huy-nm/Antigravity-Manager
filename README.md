# 🚀 Antigravity Manager

> **A modern Antigravity multi-account management tool designed for macOS & Windows**

Antigravity Manager is a powerful utility designed to address the pain point of the Antigravity client's lack of native support for multi-account switching. By taking over the application's configuration state, it allows users to seamlessly switch between infinite accounts with a single click, while providing automatic backup, process guardianship, and a visual management interface.

---

## ✨ Core Features

### 🛡️ Account Security & Management
*   **Unlimited Account Snapshots**: Create any number of account backups, fully preserving login credentials, user configurations, and local state.
*   **Smart Recognition**: Automatically reads the email and ID of the currently logged-in account from the database, eliminating manual entry.
*   **Automatic Backup Mechanism**:
    *   **Startup Backup**: Automatically backs up the current state every time the manager is started to prevent accidental overwrites.
    *   **Switch Backup**: Automatically saves the latest state of the current account before switching accounts.
*   **Detailed Metadata**: Records the creation time, last used time, email, and unique ID for each archive.

### ⚡️ Seamless Experience
*   **One-Click Switching**: Complete the entire "Close App -> Replace Data -> Restart App" process with just one click.
*   **Process Guardian**:
    *   **Graceful Exit**: Prioritizes using AppleScript (macOS) or taskkill (Windows) to notify the application to exit normally, protecting data integrity.
    *   **Forceful Fallback**: If the application hangs, it automatically upgrades to a forced termination strategy to ensure successful switching.
*   **Cross-Platform Support**: Perfectly adapted for macOS (Intel/Apple Silicon) and Windows 10/11.

### 🎨 Modern Interface
*   **Flet Powered**: High-performance GUI based on Flutter, with rapid response.
*   **Native Integration**: Automatically adapts to the system's Dark/Light mode, providing a native window experience.
*   **User-Friendly**: Clear list views, intuitive action buttons, and friendly confirmation popups.

---

## 🛠️ Quick Start

### Requirements
*   **OS**: macOS 10.15+ or Windows 10+
*   **Python**: 3.10 or higher
*   **Antigravity**: Must be installed and run at least once

### 1. Install Dependencies
Run the following command in the project root directory to install the required libraries:

```bash
pip install -r requirements.txt
```

### 2. Run Application

#### 🖥️ GUI Mode (Recommended)
Launch the graphical interface to experience full interactive features:

```bash
# macOS / Linux
python gui/main.py

# Windows
python gui\main.py
```

#### ⌨️ CLI Mode
Suitable for script integration or power users.

**Interactive Menu**:
```bash
python main.py
```

**Common Commands**:
```bash
# List all archives
python main.py list

# Backup current account (auto-detect name)
python main.py add

# Backup with specific name
python main.py add -n "Work Account"

# Switch account (use ID or list index)
python main.py switch -i 1

# Delete backup
python main.py delete -i 1
```

---

## 📦 Packaging & Deployment

This project includes automated build scripts to generate standalone executables that do not require a Python environment.

### 🍎 macOS Packaging
Build `.app` application and `.dmg` installer.

```bash
# 1. Grant execution permissions
chmod +x build_macos.sh

# 2. Run build
./build_macos.sh
```
*   **Output Path**: `gui/build/macos/`
*   **Includes**: `Antigravity Manager.app`, `Antigravity Manager.dmg`
*   **Architecture**: Universal Binary (Supports Intel & M1/M2/M3)

### 🪟 Windows Packaging
Build single-file `.exe` executable.

```powershell
# Run in PowerShell
./build_windows.ps1
```
*   **Output Path**: `dist/`
*   **Includes**: `Antigravity Manager.exe`
*   **Features**: No console window, single-file portable execution.

---

## 🧩 Technical Architecture

### Directory Structure
```
antigravity_manager/
├── assets/                 # Static resources (icons, etc.)
├── gui/                    # Core codebase
│   ├── main.py             # GUI entry point
│   ├── account_manager.py  # Account logic (CRUD)
│   ├── process_manager.py  # Process control (Cross-platform process management)
│   ├── db_manager.py       # Data persistence (File operations)
│   ├── views/              # UI view components
│   └── utils.py            # General utilities
├── main.py                 # CLI entry point
├── build_macos.sh          # macOS build script
├── build_windows.ps1       # Windows build script
└── requirements.txt        # Python dependencies
```

### Data Storage
*   **Configuration**: `~/.antigravity-agent/accounts.json` (Stores account list index)
*   **Backup Data**: `~/.antigravity-agent/backups/*.json` (Actual account data snapshots)
*   **Log File**: `~/.antigravity-agent/app.log`

---

## ❓ FAQ

**Q: Antigravity doesn't restart automatically after switching accounts?**
A: Ensure Antigravity is installed in the standard path (`/Applications` for macOS, default installation directory for Windows). If a custom path is used, the program attempts to launch via the URI protocol (`antigravity://`).

**Q: Where are backup files stored?**
A: All data is stored in the `.antigravity-agent` folder in the user's home directory. You can manually backup this folder at any time.

**Q: Why does antivirus software flag it on Windows?**
A: Single-file exes packaged with PyInstaller are occasionally false-flagged. This is a known issue with PyInstaller. Please whitelist the application or run directly from Python source code.

---

## 📄 License

This project is licensed under the MIT License. Issues and Pull Requests are welcome.

Copyright (c) 2025 Ctrler. All rights reserved.
