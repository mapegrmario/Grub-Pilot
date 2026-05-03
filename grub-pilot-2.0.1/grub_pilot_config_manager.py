#!/usr/bin/env python3
"""Grub Pilot - App Configuration Manager"""
import configparser, os, logging

LOG = logging.getLogger(__name__)

SYSTEM_CONFIG = '/etc/grub-pilot/config.ini'
USER_CONFIG   = os.path.expanduser('~/.config/grub-pilot/config.ini')

_DEFAULTS = {
    'grub-pilot': {'version': '2.0.1', 'language': 'de', 'theme': 'dark'},
    'paths':      {'backup_dir': '/var/backups/grub-pilot',
                   'log_dir':    '/var/log/grub-pilot'},
    'security':   {'require_admin': 'true',
                   'validate_before_write': 'true',
                   'auto_backup': 'true'},
}

def load_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    for section, values in _DEFAULTS.items():
        cfg[section] = values
    for path in (SYSTEM_CONFIG, USER_CONFIG):
        if os.path.exists(path):
            try:
                cfg.read(path)
            except Exception as e:
                LOG.warning(f"Config read error {path}: {e}")
    return cfg

def get(section: str, key: str, fallback=None) -> str:
    try:
        return load_config()[section][key]
    except Exception:
        return fallback

def save_user_config(section: str, key: str, value: str) -> bool:
    try:
        cfg = configparser.ConfigParser()
        os.makedirs(os.path.dirname(USER_CONFIG), exist_ok=True)
        if os.path.exists(USER_CONFIG):
            cfg.read(USER_CONFIG)
        if section not in cfg:
            cfg[section] = {}
        cfg[section][key] = value
        with open(USER_CONFIG, 'w') as f:
            cfg.write(f)
        return True
    except Exception as e:
        LOG.error(f"save_user_config: {e}")
        return False
