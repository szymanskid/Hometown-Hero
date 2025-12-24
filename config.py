"""
Configuration management for Hometown Hero Banner Management System.

This module centralizes all configuration paths and environment variable handling,
making it easy to deploy the application on shared drives with external data storage.
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from dotenv import load_dotenv
import warnings


def load_configuration():
    """
    Load configuration from environment variables and .env files.
    
    Search order:
    1. Environment variables from OS
    2. If HH_CONFIG_DIR is set, load .env from that directory
    3. Otherwise, load .env from repo root if it exists
    """
    # First check if HH_CONFIG_DIR is set (for external config folder)
    config_dir = os.getenv('HH_CONFIG_DIR')
    
    if config_dir:
        env_file = Path(config_dir) / '.env'
        if env_file.exists():
            load_dotenv(env_file)
        else:
            warnings.warn(f"HH_CONFIG_DIR set to {config_dir} but no .env file found there")
    else:
        # Load from repo root if it exists
        repo_root = Path(__file__).parent
        env_file = repo_root / '.env'
        if env_file.exists():
            load_dotenv(env_file)


# Load configuration when module is imported
load_configuration()


def get_db_path() -> str:
    """
    Get the database file path.
    
    Returns:
        Path to SQLite database file (default: ./hometown_hero.db)
    """
    return os.getenv('HH_DB_PATH', 'hometown_hero.db')


def get_m365_config_path() -> str:
    """
    Get the Microsoft 365 configuration file path.
    
    Returns:
        Path to M365 config JSON file (default: ./m365_config.json)
    """
    return os.getenv('HH_M365_CONFIG', 'm365_config.json')


def get_export_dir() -> str:
    """
    Get the export directory for generated files.
    
    Returns:
        Path to export directory (default: ./exports)
    """
    return os.getenv('HH_EXPORT_DIR', 'exports')


def get_config_dir() -> Optional[str]:
    """
    Get the external configuration directory if set.
    
    Returns:
        Path to external config directory or None if using defaults
    """
    return os.getenv('HH_CONFIG_DIR')


def validate_db_path() -> Tuple[bool, str]:
    """
    Validate database path accessibility.
    
    Returns:
        Tuple of (is_valid, message)
    """
    db_path = get_db_path()
    path_obj = Path(db_path)
    
    # Check if directory exists (for creating new DB)
    parent_dir = path_obj.parent
    if not parent_dir.exists():
        return False, f"Database directory does not exist: {parent_dir}"
    
    # Check if parent directory is writable
    if not os.access(parent_dir, os.W_OK):
        return False, f"Database directory is not writable: {parent_dir}"
    
    # If DB exists, check if it's accessible
    if path_obj.exists():
        if not os.access(db_path, os.R_OK):
            return False, f"Database file is not readable: {db_path}"
        if not os.access(db_path, os.W_OK):
            return False, f"Database file is not writable: {db_path}"
    
    return True, f"Database path OK: {db_path}"


def validate_m365_config_path() -> Tuple[bool, str]:
    """
    Validate M365 config path accessibility.
    
    Returns:
        Tuple of (is_valid, message)
    """
    config_path = get_m365_config_path()
    path_obj = Path(config_path)
    
    # It's OK if the file doesn't exist yet (can be created)
    if not path_obj.exists():
        # Check if parent directory is writable
        parent_dir = path_obj.parent
        if not parent_dir.exists():
            return False, f"M365 config directory does not exist: {parent_dir}"
        if not os.access(parent_dir, os.W_OK):
            return False, f"M365 config directory is not writable: {parent_dir}"
        return True, f"M365 config path OK (not yet created): {config_path}"
    
    # If file exists, check if it's readable
    if not os.access(config_path, os.R_OK):
        return False, f"M365 config file is not readable: {config_path}"
    
    return True, f"M365 config path OK: {config_path}"


def is_network_path(path: str) -> bool:
    """
    Check if a path is on a network drive.
    
    On Windows, checks for UNC paths (\\server\share) or mapped drives that resolve to UNC.
    On Unix-like systems, checks for NFS/SMB mount points.
    
    Returns:
        True if path appears to be on network storage
    """
    path_obj = Path(path).resolve()
    
    # Windows UNC path check
    if os.name == 'nt':
        # UNC paths start with \\
        path_str = str(path_obj)
        if path_str.startswith('\\\\'):
            return True
        
        # Check if drive letter maps to network (requires additional libs, so basic check)
        # This is a simple heuristic - not perfect but good enough
        try:
            import ctypes
            drive = path_str[:3] if len(path_str) >= 3 else None
            if drive and drive[1] == ':':
                # GetDriveType returns 4 for network drives
                drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
                return drive_type == 4
        except Exception:
            pass
    
    # Unix-like systems: check mount points (basic check)
    # A more thorough check would parse /proc/mounts or use platform-specific APIs
    try:
        import subprocess
        result = subprocess.run(['df', '-T', str(path_obj)], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            # Check for network filesystem types
            network_fs = ['nfs', 'cifs', 'smb', 'smbfs', 'nfs4', 'fuse.sshfs']
            for fs_type in network_fs:
                if fs_type in result.stdout.lower():
                    return True
    except Exception:
        pass
    
    return False


def get_configuration_warnings() -> list:
    """
    Get list of configuration warnings.
    
    Returns:
        List of warning messages
    """
    warnings_list = []
    
    # Check DB path
    db_valid, db_msg = validate_db_path()
    if not db_valid:
        warnings_list.append(f"⚠️ Database: {db_msg}")
    
    # Check M365 config path
    m365_valid, m365_msg = validate_m365_config_path()
    if not m365_valid:
        warnings_list.append(f"⚠️ M365 Config: {m365_msg}")
    
    # Check for network paths (concurrent access warning)
    db_path = get_db_path()
    if is_network_path(db_path):
        warnings_list.append(
            f"⚠️ Database is on network storage ({db_path}). "
            "Ensure only one user writes at a time to avoid corruption."
        )
    
    return warnings_list


def get_configuration_summary() -> dict:
    """
    Get a summary of current configuration.
    
    Returns:
        Dictionary with configuration details
    """
    return {
        'db_path': get_db_path(),
        'm365_config_path': get_m365_config_path(),
        'export_dir': get_export_dir(),
        'config_dir': get_config_dir(),
        'db_valid': validate_db_path()[0],
        'm365_valid': validate_m365_config_path()[0],
        'db_on_network': is_network_path(get_db_path()),
        'warnings': get_configuration_warnings()
    }
