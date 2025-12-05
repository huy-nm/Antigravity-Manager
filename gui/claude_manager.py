# -*- coding: utf-8 -*-
import os
import json
import platform
import subprocess
import uuid
from pathlib import Path
from datetime import datetime

# Use relative imports
from utils import info, error, warning, debug

# Configuration
BACKUP_DIR = Path.home() / ".claude-switch-backup"
SEQUENCE_FILE = BACKUP_DIR / "sequence.json"

def get_claude_config_path():
    """Get Claude configuration file path with fallback"""
    primary_config = Path.home() / ".claude" / ".claude.json"
    fallback_config = Path.home() / ".claude.json"
    
    if primary_config.exists():
        try:
            with open(primary_config, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'oauthAccount' in data:
                    return primary_config
        except:
            pass
            
    return fallback_config

def get_current_account_email():
    """Get current account email from config"""
    config_path = get_claude_config_path()
    if not config_path.exists():
        return None
        
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('oauthAccount', {}).get('emailAddress')
    except:
        return None

def read_credentials():
    """Read credentials based on platform"""
    system = platform.system()
    if system == "Darwin":
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            error(f"Error reading credentials: {e}")
    elif system == "Linux":
        cred_path = Path.home() / ".claude" / ".credentials.json"
        if cred_path.exists():
            try:
                with open(cred_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                pass
    return None

def write_credentials(credentials):
    """Write credentials based on platform"""
    if not credentials:
        return False
        
    system = platform.system()
    if system == "Darwin":
        try:
            user = os.environ.get("USER", "unknown")
            subprocess.run(
                ["security", "add-generic-password", "-U", "-s", "Claude Code-credentials", "-a", user, "-w", credentials],
                check=True
            )
            return True
        except Exception as e:
            error(f"Error writing credentials: {e}")
            return False
    elif system == "Linux":
        cred_path = Path.home() / ".claude" / ".credentials.json"
        cred_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(cred_path, 'w', encoding='utf-8') as f:
                f.write(credentials)
            os.chmod(cred_path, 0o600)
            return True
        except:
            return False
    return False

def setup_directories():
    """Setup backup directories"""
    BACKUP_DIR.mkdir(exist_ok=True)
    (BACKUP_DIR / "configs").mkdir(exist_ok=True)
    (BACKUP_DIR / "credentials").mkdir(exist_ok=True)
    os.chmod(BACKUP_DIR, 0o700)
    os.chmod(BACKUP_DIR / "configs", 0o700)
    os.chmod(BACKUP_DIR / "credentials", 0o700)

def init_sequence_file():
    """Initialize sequence.json if it doesn't exist"""
    if not SEQUENCE_FILE.exists():
        setup_directories()
        init_content = {
            "activeAccountNumber": None,
            "lastUpdated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sequence": [],
            "accounts": {}
        }
        with open(SEQUENCE_FILE, 'w', encoding='utf-8') as f:
            json.dump(init_content, f, indent=2)

def get_next_account_number():
    """Get next account number"""
    init_sequence_file()
    try:
        with open(SEQUENCE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            accounts = data.get("accounts", {})
            if not accounts:
                return 1
            keys = [int(k) for k in accounts.keys()]
            return max(keys) + 1 if keys else 1
    except:
        return 1

def add_account_snapshot():
    """Add current account snapshot"""
    setup_directories()
    init_sequence_file()
    
    current_email = get_current_account_email()
    if not current_email:
        error("No active Claude account found config file.")
        return False
        
    # Check if account exists
    with open(SEQUENCE_FILE, 'r', encoding='utf-8') as f:
        seq_data = json.load(f)
        for acc_num, acc_data in seq_data.get("accounts", {}).items():
            if acc_data.get("email") == current_email:
                info(f"Account {current_email} is already managed (Account-{acc_num}). Updating...")
                account_num = acc_num
                break
        else:
            account_num = str(get_next_account_number())
            
    current_creds = read_credentials()
    if not current_creds:
        error("No credentials found for current account")
        return False
        
    config_path = get_claude_config_path()
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            current_config = f.read()
            config_json = json.loads(current_config)
            account_uuid = config_json.get('oauthAccount', {}).get('accountUuid')
    except Exception as e:
        error(f"Error reading config: {e}")
        return False

    # Write backups
    system = platform.system()
    if system == "Darwin":
        user = os.environ.get("USER", "unknown")
        subprocess.run(
            ["security", "add-generic-password", "-U", "-s", f"Claude Code-Account-{account_num}-{current_email}", "-a", user, "-w", current_creds],
            check=True
        )
    elif system == "Linux":
        cred_file = BACKUP_DIR / "credentials" / f".claude-credentials-{account_num}-{current_email}.json"
        with open(cred_file, 'w', encoding='utf-8') as f:
            f.write(current_creds)
        os.chmod(cred_file, 0o600)
        
    config_file = BACKUP_DIR / "configs" / f".claude-config-{account_num}-{current_email}.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(current_config)
    os.chmod(config_file, 0o600)
    
    # Update sequence
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    with open(SEQUENCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    if str(account_num) not in data.get("accounts", {}):
        data.setdefault("accounts", {})[str(account_num)] = {
            "email": current_email,
            "uuid": account_uuid,
            "added": now
        }
        if int(account_num) not in data.get("sequence", []):
            data.setdefault("sequence", []).append(int(account_num))
            
    data["activeAccountNumber"] = int(account_num)
    data["lastUpdated"] = now
    
    with open(SEQUENCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    info(f"Added/Updated Account {account_num}: {current_email}")
    return True

def list_accounts_data():
    """List accounts for UI"""
    if not SEQUENCE_FILE.exists():
        return []
        
    try:
        with open(SEQUENCE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        accounts_map = data.get("accounts", {})
        result = []
        
        for acc_num, acc_data in accounts_map.items():
            result.append({
                "id": str(acc_num),
                "name": f"Account {acc_num}",
                "email": acc_data.get("email"),
                "last_used": acc_data.get("added"), # Using 'added' as last interaction time proxy
                "real_id": str(acc_num) # Keep track of the sequence number
            })
            
        # Sort by ID
        result.sort(key=lambda x: int(x["id"]))
        return result
    except Exception as e:
        error(f"Error listing accounts: {e}")
        return []

def switch_account(account_id):
    """Switch to account by ID (sequence number)"""
    # 1. Backup current first
    if not add_account_snapshot():
        warning("Failed to backup current account before switching. Proceeding anyway...")
    
    # 2. Read target data
    init_sequence_file()
    with open(SEQUENCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    account_info = data.get("accounts", {}).get(str(account_id))
    if not account_info:
        error(f"Account {account_id} not found")
        return False
        
    email = account_info.get("email")
    
    # Read config
    config_file = BACKUP_DIR / "configs" / f".claude-config-{account_id}-{email}.json"
    if not config_file.exists():
        error(f"Config file missing for account {account_id}")
        return False
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            target_config_str = f.read()
            target_config = json.loads(target_config_str)
    except Exception as e:
        error(f"Error reading target config: {e}")
        return False
        
    # Read credentials
    target_creds = None
    system = platform.system()
    if system == "Darwin":
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", f"Claude Code-Account-{account_id}-{email}", "-w"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                target_creds = result.stdout.strip()
        except:
            pass
    elif system == "Linux":
        cred_file = BACKUP_DIR / "credentials" / f".claude-credentials-{account_id}-{email}.json"
        if cred_file.exists():
            with open(cred_file, 'r', encoding='utf-8') as f:
                target_creds = f.read()
                
    if not target_creds:
        error(f"Credentials missing for account {account_id}")
        return False
        
    # 3. Apply
    if not write_credentials(target_creds):
        return False
        
    # Merge oauthAccount into current config file
    live_config_path = get_claude_config_path()
    try:
        # Read current live config structure (to preserve other settings)
        if live_config_path.exists():
            with open(live_config_path, 'r', encoding='utf-8') as f:
                live_data = json.load(f)
        else:
            live_data = {}
            
        # Update only oauthAccount
        if 'oauthAccount' in target_config:
            live_data['oauthAccount'] = target_config['oauthAccount']
            
        with open(live_config_path, 'w', encoding='utf-8') as f:
            json.dump(live_data, f, indent=2)
            
    except Exception as e:
        error(f"Error updating config file: {e}")
        return False
        
    # 4. Update active state
    data["activeAccountNumber"] = int(account_id)
    data["lastUpdated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    with open(SEQUENCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    info(f"Switched to Account {account_id} ({email})")
    return True

def delete_account(account_id):
    """Delete account by ID"""
    init_sequence_file()
    with open(SEQUENCE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    account_info = data.get("accounts", {}).get(str(account_id))
    if not account_info:
        error(f"Account {account_id} not found")
        return False
        
    email = account_info.get("email")
    
    # Remove files
    config_file = BACKUP_DIR / "configs" / f".claude-config-{account_id}-{email}.json"
    if config_file.exists():
        os.remove(config_file)
        
    system = platform.system()
    if system == "Darwin":
        try:
            subprocess.run(
                ["security", "delete-generic-password", "-s", f"Claude Code-Account-{account_id}-{email}"],
                check=False
            )
        except:
            pass
    elif system == "Linux":
        cred_file = BACKUP_DIR / "credentials" / f".claude-credentials-{account_id}-{email}.json"
        if cred_file.exists():
            os.remove(cred_file)
            
    # Update sequence
    if str(account_id) in data.get("accounts", {}):
        del data["accounts"][str(account_id)]
        
    if "sequence" in data:
        data["sequence"] = [x for x in data["sequence"] if x != int(account_id)]
        
    with open(SEQUENCE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    info(f"Deleted Account {account_id}")
    return True
