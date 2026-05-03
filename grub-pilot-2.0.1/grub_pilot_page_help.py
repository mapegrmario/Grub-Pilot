#!/usr/bin/env python3
"""Grub Pilot - Help Page (aktualisiert v2.0.1)"""
import customtkinter as ctk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t, get_lang

_HELP_DE = """
🛡️  GRUB PILOT v2.0.1 – HILFE & DOKUMENTATION
══════════════════════════════════════════════════════════════

ÜBERSICHT
─────────
Grub Pilot ist ein sicheres Verwaltungswerkzeug für den GRUB-
Bootloader. Alle Änderungen werden automatisch gesichert, bevor
sie angewendet werden.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏠  START
  Zeigt Systeminformationen: UEFI/BIOS, Secure Boot, BLS-Boot
  und GRUB-Version als Übersichtskacheln.

📋  BOOT-EINTRÄGE
  Listet alle erkannten Booteinträge auf. Mit „Als Standard"
  legen Sie fest, welches OS beim nächsten Start automatisch
  gestartet wird.

⏱️   BOOT-TIMEOUT
  Steuert die Wartezeit im GRUB-Menü.
    -1  → Menü wird übersprungen (direkter Start)
     0  → Sofortiger Start ohne Verzögerung
   1–30 → Sekunden bis zum automatischen Start

⚙️   KERNEL-PARAMETER
  Editor für GRUB_CMDLINE_LINUX_DEFAULT.
  Schnell-Toggles für häufige Parameter:
    • quiet / splash         – Boot-Ausgabe unterdrücken
    • nomodeset              – Grafikprobleme beheben
    • nvidia-drm.modeset=1   – NVIDIA DRM
    • acpi=off               – ACPI deaktivieren
    • mitigations=off        – CPU-Mitigationen (schneller)
    • mem=4G                 – RAM-Limit setzen
  Der Wert wird direkt bearbeitbar als Textfeld angezeigt.

🎨  THEMES
  Listet installierte GRUB-Themes auf und aktiviert sie.
  Außerdem können Theme-Archive (.tar.xz) direkt installiert
  werden – Grub Pilot sucht automatisch nach theme.txt.
  Installationsort: /boot/grub/themes/

🖼️   HINTERGRUNDBILD
  Setzt GRUB_BACKGROUND auf ein eigenes Bild.
  Unterstützte Formate: PNG, JPG, TGA, BMP
  Eine Vorschau wird direkt in der GUI angezeigt.

🖥️   ANZEIGE / VIDEO
  GRUB_GFXMODE:          Auflösung des GRUB-Menüs (z.B. 1920x1080)
  GRUB_GFXPAYLOAD_LINUX: Videomodus nach dem Boot
    text → Textmodus  |  keep → Auflösung beibehalten
  os-prober:             Dual-Boot-Erkennung ein-/ausschalten
    Aktivieren wenn Windows oder andere OS nicht erkannt werden.

🔒  EFI BOOT-REIHENFOLGE  (nur UEFI-Systeme)
  Listet alle EFI-Boot-Einträge auf.
  Reihenfolge per Pfeil-Buttons ändern, Einträge löschen.
  Änderungen werden mit efibootmgr geschrieben.

📝  EIGENE BOOT-EINTRÄGE
  Direkteditor für /etc/grub.d/40_custom.
  Mit der Vorlage-Schaltfläche wird ein fertiges menuentry-
  Gerüst eingefügt. Speichern aktualisiert GRUB automatisch.
  Nützlich für: Memtest, Chainloading, Recovery-Systeme.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WERKZEUGE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾  BACKUPS
  Vor jeder Änderung wird automatisch ein Backup erstellt.
  Ältere Backups können hier wiederhergestellt werden.
  Speicherort: /var/backups/grub-pilot/

📤  PROFILE
  Exportiert die komplette GRUB-Konfiguration als JSON-Datei.
  Importiert ein gespeichertes Profil und wendet es an.
  Nützlich für: Sicherung, Übertragung auf andere Rechner.

📄  LIVE LOG-VIEWER
  Zeigt /var/log/grub-pilot/fehler.log in Echtzeit an.
  Filter: ALL / INFO / WARN / ERROR
  ▶ Live starten: neue Einträge erscheinen sofort.
  Export: Log als Datei speichern.

🔧  REPARATUR
  grub-install: Bootloader auf ein Laufwerk schreiben.
    → Laufwerk aus Dropdown wählen (z.B. /dev/sda)
    → Ausgabe erscheint direkt in der GUI
  GRUB aktualisieren: update-grub / grub-mkconfig ausführen.
  ⚠️  Achtung: Immer das richtige Laufwerk prüfen!

⚙️   EINSTELLUNGEN
  Sprache: Deutsch / Englisch

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FEHLERBEHEBUNG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend nicht verbunden:
  sudo systemctl start grub-pilot-backend
  sudo systemctl status grub-pilot-backend

Logs anzeigen:
  sudo journalctl -u grub-pilot-backend -n 30
  cat /var/log/grub-pilot/fehler.log

Installations-Analyse:
  cd ~/Projekte/in Arbeit/grub-pilot-2.0.1
  sudo bash grub-pilot-analyse.sh

Notfall-Wiederherstellung:
  sudo /root/grub-pilot-emergency-backup-*/restore-emergency.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEMANFORDERUNGEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Linux mit GRUB 2 (Legacy oder UEFI)
  • Python 3.10+ | customtkinter 5.x | dbus-python | Pillow
  • Unterstützte Distributionen:
    Ubuntu, Debian, Linux Mint, LMDE
    Fedora, RHEL, openSUSE, Arch, Manjaro

Autor:   Mario Peeß / Großenhain
E-Mail:  mapegr@mailbox.org
Lizenz:  GPLv3
Version: 2.0.1
"""

_HELP_EN = """
🛡️  GRUB PILOT v2.0.1 – HELP & DOCUMENTATION
══════════════════════════════════════════════════════════════

OVERVIEW
────────
Grub Pilot is a secure management tool for the GRUB bootloader.
All changes are automatically backed up before being applied.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏠  HOME
  Shows system information: UEFI/BIOS, Secure Boot, BLS Boot
  and GRUB version as overview tiles.

📋  BOOT ENTRIES
  Lists all detected boot entries. Use "Set Default" to choose
  which OS starts automatically on next boot.

⏱️   BOOT TIMEOUT
  Controls how long the GRUB menu is visible.
    -1  → Menu is skipped (boot immediately)
     0  → Instant boot without delay
   1–30 → Seconds until automatic boot

⚙️   KERNEL PARAMETERS
  Editor for GRUB_CMDLINE_LINUX_DEFAULT.
  Quick toggles for common parameters:
    • quiet / splash         – Suppress boot output
    • nomodeset              – Fix graphics issues
    • nvidia-drm.modeset=1   – NVIDIA DRM
    • acpi=off               – Disable ACPI
    • mitigations=off        – Disable CPU mitigations (faster)
    • mem=4G                 – Limit RAM
  The value is also shown as an editable text field.

🎨  THEMES
  Lists installed GRUB themes and activates them.
  Theme archives (.tar.xz) can be installed directly –
  Grub Pilot automatically locates theme.txt.
  Installation path: /boot/grub/themes/

🖼️   WALLPAPER
  Sets GRUB_BACKGROUND to a custom image.
  Supported formats: PNG, JPG, TGA, BMP
  A preview is shown directly in the GUI.

🖥️   DISPLAY / VIDEO
  GRUB_GFXMODE:          GRUB menu resolution (e.g. 1920x1080)
  GRUB_GFXPAYLOAD_LINUX: Video mode after booting
    text → text mode  |  keep → keep resolution
  os-prober:             Enable/disable dual-boot detection
    Enable if Windows or other OS are not detected.

🔒  EFI BOOT ORDER  (UEFI systems only)
  Lists all EFI boot entries.
  Change order with arrow buttons, delete entries.
  Changes are written with efibootmgr.

📝  CUSTOM BOOT ENTRIES
  Direct editor for /etc/grub.d/40_custom.
  The template button inserts a ready-made menuentry skeleton.
  Saving automatically updates GRUB.
  Useful for: Memtest, chainloading, recovery systems.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOOLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾  BACKUPS
  A backup is created automatically before every change.
  Older backups can be restored here.
  Location: /var/backups/grub-pilot/

📤  PROFILES
  Exports the complete GRUB configuration as a JSON file.
  Imports a saved profile and applies it.
  Useful for: backup, transfer to another machine.

📄  LIVE LOG VIEWER
  Shows /var/log/grub-pilot/fehler.log in real time.
  Filter: ALL / INFO / WARN / ERROR
  ▶ Start live: new entries appear immediately.
  Export: save log as a file.

🔧  REPAIR
  grub-install: write bootloader to a drive.
    → Select drive from dropdown (e.g. /dev/sda)
    → Output appears directly in the GUI
  Update GRUB: run update-grub / grub-mkconfig.
  ⚠️  Warning: always verify the correct drive!

⚙️   SETTINGS
  Language: German / English

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend not connected:
  sudo systemctl start grub-pilot-backend
  sudo systemctl status grub-pilot-backend

View logs:
  sudo journalctl -u grub-pilot-backend -n 30
  cat /var/log/grub-pilot/fehler.log

Installation analysis:
  sudo bash grub-pilot-analyse.sh

Emergency restore:
  sudo /root/grub-pilot-emergency-backup-*/restore-emergency.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Linux with GRUB 2 (Legacy or UEFI)
  • Python 3.10+ | customtkinter 5.x | dbus-python | Pillow
  • Supported distributions:
    Ubuntu, Debian, Linux Mint, LMDE
    Fedora, RHEL, openSUSE, Arch, Manjaro

Author:  Mario Peeß / Großenhain
E-Mail:  mapegr@mailbox.org
License: GPLv3
Version: 2.0.1
"""


class HelpPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('help_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0, 12))

        box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family='monospace', size=12),
            fg_color=COLORS['card'],
            text_color=COLORS['text'],
            corner_radius=12,
            wrap='word',
            activate_scrollbars=True,
            border_width=1,
            border_color=COLORS['border'],
        )
        box.pack(expand=True, fill='both')

        content = _HELP_DE if get_lang() == 'de' else _HELP_EN
        box.insert('1.0', content.strip())
        box.configure(state='disabled')

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
