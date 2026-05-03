#!/usr/bin/env python3
"""Grub Pilot - Color Theme (Windows 11 inspired, einziges Theme)"""

COLORS = {
    # Hintergründe
    'bg':           '#f3f3f3',   # fast weißes Seitengrau
    'sidebar':      '#fafafa',   # fast weiße Sidebar
    'card':         '#ffffff',   # reine weiße Cards
    'card_hover':   '#f0f5ff',   # zarter Blauschimmer beim Hover

    # Akzent (Windows-Blau)
    'accent':       '#0067c0',
    'accent_hover': '#0052a3',
    'accent_light': '#dbeafe',   # ganz helles Blau für Tags / Badges

    # Status
    'success':      '#107c10',
    'success_hover':'#0a5e0a',
    'warning':      '#c45911',
    'warning_hover':'#9e4710',
    'error':        '#c42b1c',

    # Text
    'text':         '#1a1a1a',
    'text_dim':     '#767676',
    'text_sidebar': '#2b2b2b',   # leicht gedämpft für Sidebar-Links

    # Rahmen & Trennlinien
    'border':       '#e0e0e0',
    'border_light': '#f0f0f0',

    # Sidebar aktiver Button
    'button_active': '#e5efff',   # Sidebar hover (Alias)
    'btn_active_bg': '#e5efff',  # zartes Blau
    'btn_active_fg': '#0067c0',  # Akzentblau

    # Overlay für In-App-Dialoge
    'overlay':      '#00000055',
}

APP_VERSION = '2.0.1'
APP_NAME    = 'Grub Pilot'
INSTALL_DIR = '/opt/grub-pilot'
LOG_FILE    = '/var/log/grub-pilot/fehler.log'
BACKUP_DIR  = '/var/backups/grub-pilot'
CONFIG_PATH = '/etc/grub-pilot/config.ini'
