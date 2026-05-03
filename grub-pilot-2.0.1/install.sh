#!/bin/bash
# ============================================================================
# Grub Pilot 2.0.1 – Install Script (neu, bereinigt)
# Autor: Mario Peeß / Großenhain | mapegr@mailbox.org
# Lizenz: GPLv3
#
# Unterstützte Distributionen:
#   Ubuntu, Debian, Linux Mint / LMDE
#   Fedora, RHEL, CentOS, Rocky, AlmaLinux
#   Arch, Manjaro, EndeavourOS
#   openSUSE Leap / Tumbleweed
#
# Ausführung: sudo ./install.sh
# ============================================================================
set -e
shopt -s nullglob   # FIX: verhindert Fehler bei leeren Glob-Mustern

# ── Farben ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; NC='\033[0m'

EMERGENCY_BACKUP="/root/grub-pilot-emergency-backup-$(date +%Y%m%d_%H%M%S)"
INSTALL_DIR='/opt/grub-pilot'
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Banner ───────────────────────────────────────────────────────────────────
clear
echo -e "${CYAN}"
cat << 'BANNER'
 ██████╗ ██████╗ ██╗   ██╗██████╗     ██████╗ ██╗██╗      ██████╗ ████████╗
██╔════╝ ██╔══██╗██║   ██║██╔══██╗    ██╔══██╗██║██║     ██╔═══██╗╚══██╔══╝
██║  ███╗██████╔╝██║   ██║██████╔╝    ██████╔╝██║██║     ██║   ██║   ██║   
██║   ██║██╔══██╗██║   ██║██╔══██╗    ██╔═══╝ ██║██║     ██║   ██║   ██║   
╚██████╔╝██║  ██║╚██████╔╝██████╔╝    ██║     ██║███████╗╚██████╔╝   ██║   
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝     ╚═╝     ╚═╝╚══════╝ ╚═════╝    ╚═╝
BANNER
echo -e "${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Grub Pilot v2.0.1 – Sicheres GRUB-Konfigurationswerkzeug${NC}"
echo -e "${GREEN}  Autor: Mario Peeß / Großenhain  |  mapegr@mailbox.org${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════════════${NC}"
echo

# ── Root-Check ───────────────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}❌ Root-Rechte erforderlich!  →  sudo ./install.sh${NC}"
  exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 0. NOTFALL-BACKUP
# ═══════════════════════════════════════════════════════════════════════════════
create_emergency_backup() {
  echo -e "${YELLOW}🔒 [0/9] Erstelle Notfall-Backup...${NC}"
  mkdir -p "${EMERGENCY_BACKUP}"

  # nullglob ist aktiv – leere Globs werden sicher ignoriert
  for file in \
    /etc/dbus-1/system.d/org.grubpilot.backend.conf \
    /usr/share/polkit-1/actions/org.grubpilot.policy \
    /etc/systemd/system/grub-pilot-backend.service \
    /etc/sudoers \
    /etc/sudoers.d/* \
    /etc/default/grub \
    /boot/grub/grub.cfg \
    /boot/grub2/grub.cfg; do
    [ -f "$file" ] || continue
    dest="${EMERGENCY_BACKUP}${file}"
    mkdir -p "$(dirname "$dest")"
    cp -a "$file" "$dest" 2>/dev/null || true
  done

  # Wiederherstellungs-Skript ins Backup kopieren
  cp -a "${SRC_DIR}/restore-emergency.sh" "${EMERGENCY_BACKUP}/" 2>/dev/null || true
  chmod +x "${EMERGENCY_BACKUP}/restore-emergency.sh" 2>/dev/null || true

  echo -e "${GREEN}   ✅ Backup: ${EMERGENCY_BACKUP}${NC}"
  echo -e "${YELLOW}   ℹ️  Wiederherstellung: sudo ${EMERGENCY_BACKUP}/restore-emergency.sh${NC}"
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 1. SYSTEM ERKENNEN
# ═══════════════════════════════════════════════════════════════════════════════
detect_system() {
  echo -e "${BLUE}📋 [1/9] System-Erkennung...${NC}"
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_ID="${ID:-unknown}"
    OS_NAME="${NAME:-Unknown Linux}"
    # Direktes Mapping für bekannte Derivate (LMDE, Pop!_OS usw.)
    case "${ID}" in
      linuxmint|lmde|pop|elementary|zorin|kali|parrot) OS_ID='debian' ;;
    esac
    # Fallback: ID_LIKE auswerten (LMDE hat ID=linuxmint ID_LIKE=debian)
    if [[ "${OS_ID}" == "unknown" ]] && [ -n "${ID_LIKE:-}" ]; then
      for like in ${ID_LIKE}; do
        case "${like}" in
          debian|ubuntu) OS_ID="${like}"; break ;;
          fedora|rhel)   OS_ID="${like}"; break ;;
          arch)          OS_ID="${like}"; break ;;
          opensuse*|suse) OS_ID="${like}"; break ;;
        esac
      done
    fi
  else
    OS_ID='unknown'; OS_NAME='Unknown Linux'
  fi

  echo -e "   • Distribution: ${YELLOW}${OS_NAME}${NC}"
  echo -e "   • Architektur:  ${YELLOW}$(uname -m)${NC}"

  if [ -d /sys/firmware/efi ]; then
    echo -e "   • Boot-Modus:   ${YELLOW}UEFI${NC}"
  else
    echo -e "   • Boot-Modus:   ${YELLOW}Legacy BIOS${NC}"
  fi
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 2. ABHÄNGIGKEITEN
# ═══════════════════════════════════════════════════════════════════════════════
install_dependencies() {
  echo -e "${BLUE}📦 [2/9] Installiere Abhängigkeiten...${NC}"

  case "${OS_ID}" in
    debian|ubuntu|linuxmint|lmde|pop|elementary|zorin|kali|parrot)
      echo -e "   Paketmanager: ${YELLOW}APT${NC}"
      apt-get update -qq
      # Versionsabhängige Pakete vorher ermitteln
      _PV=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "3")
      DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        python3 python3-pip python3-venv python3-dev \
        python3-dbus python3-gi python3-pil \
        python3-tk "python${_PV}-tk" python3-setuptools \
        dbus dbus-x11 policykit-1 \
        grub2-common \
        git curl libgtk-3-0 libgdk-pixbuf2.0-0 \
        2>/dev/null || echo -e "${YELLOW}   ⚠ Einige APT-Pakete nicht verfügbar (wird fortgesetzt)${NC}"
      ;;
    fedora|rhel|centos|rocky|almalinux)
      echo -e "   Paketmanager: ${YELLOW}DNF${NC}"
      dnf install -y -q \
        python3 python3-pip python3-devel \
        python3-dbus python3-gobject python3-pillow \
        python3-tkinter python3-setuptools \
        dbus dbus-x11 polkit \
        grub2-tools git curl gtk3 \
        2>/dev/null || true
      ;;
    arch|manjaro|endeavouros|garuda|arcolinux)
      echo -e "   Paketmanager: ${YELLOW}Pacman${NC}"
      pacman -S --noconfirm --needed \
        python python-pip python-setuptools \
        python-dbus python-gobject python-pillow \
        tk dbus polkit grub git curl gtk3 \
        2>/dev/null || true
      ;;
    opensuse*|suse)
      echo -e "   Paketmanager: ${YELLOW}Zypper${NC}"
      zypper --non-interactive install -l \
        python3 python3-pip python3-devel \
        python3-dbus-python python3-gobject python3-Pillow \
        python3-tk python3-setuptools \
        dbus-1 polkit grub2 git curl gtk3 \
        2>/dev/null || true
      ;;
    *)
      echo -e "${YELLOW}   ⚠ Distribution '${OS_ID}' nicht bekannt.${NC}"
      read -r -p "   Trotzdem fortfahren? (j/N): " REPLY
      [[ "${REPLY,,}" =~ ^j ]] || exit 1
      ;;
  esac

  echo -e "${GREEN}   ✅ Systemabhängigkeiten installiert${NC}"
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 3. VERZEICHNISSE
# ═══════════════════════════════════════════════════════════════════════════════
create_directories() {
  echo -e "${BLUE}📁 [3/9] Erstelle Verzeichnisstruktur...${NC}"
  for dir in \
    "${INSTALL_DIR}" \
    /etc/grub-pilot \
    /var/log/grub-pilot \
    /var/backups/grub-pilot \
    /usr/share/applications \
    /usr/share/icons/grub-pilot \
    /etc/dbus-1/system.d \
    /usr/share/polkit-1/actions; do
    mkdir -p "$dir"
  done
  chmod 755 "${INSTALL_DIR}" /var/log/grub-pilot /var/backups/grub-pilot
  echo -e "${GREEN}   ✅ Verzeichnisse erstellt${NC}"
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 4. PYTHON VIRTUAL ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════
setup_python() {
  echo -e "${BLUE}🐍 [4/9] Richte Python-Umgebung ein...${NC}"

  # Exakte Python-Version ermitteln (z.B. "3.13")
  PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  echo -e "   Python-Version: ${YELLOW}${PY_VER}${NC}"

  # Sicherstellen, dass das versionsabhängige venv-Paket installiert ist
  # (Debian/Ubuntu: python3.13-venv, python3.12-venv usw.)
  case "${OS_ID}" in
    debian|ubuntu|linuxmint|lmde|pop|elementary|zorin|kali|parrot)
      VENV_PKG="python${PY_VER}-venv"
      echo -e "   Installiere ${YELLOW}${VENV_PKG}${NC} (falls fehlend)..."
      apt-get install -y -qq "${VENV_PKG}" 2>/dev/null || \
        echo -e "${YELLOW}   ⚠ ${VENV_PKG} nicht gefunden – versuche python3-venv${NC}"
      apt-get install -y -qq python3-venv 2>/dev/null || true
      # ensurepip-Fallback
      apt-get install -y -qq python3-pip 2>/dev/null || true
      ;;
  esac

  # Altes venv sichern, falls vorhanden
  if [ -d "${INSTALL_DIR}/venv" ]; then
    mv "${INSTALL_DIR}/venv" "${INSTALL_DIR}/venv.bak.$(date +%s)" 2>/dev/null || true
  fi

  # venv erstellen – erst mit ensurepip, dann ohne als Fallback
  if ! python3 -m venv "${INSTALL_DIR}/venv" --system-site-packages 2>/dev/null; then
    echo -e "${YELLOW}   ⚠ venv mit ensurepip fehlgeschlagen – versuche --without-pip${NC}"
    python3 -m venv "${INSTALL_DIR}/venv" --system-site-packages --without-pip
    # pip manuell bootstrappen
    python3 -m ensurepip --root "${INSTALL_DIR}/venv" 2>/dev/null || \
    curl -sS https://bootstrap.pypa.io/get-pip.py | \
      "${INSTALL_DIR}/venv/bin/python3" 2>/dev/null || \
    echo -e "${YELLOW}   ⚠ pip-Bootstrap fehlgeschlagen – nur System-pip verfügbar${NC}"
  fi

  # pip upgraden & customtkinter installieren
  PIP="${INSTALL_DIR}/venv/bin/pip"
  if [ -x "${PIP}" ]; then
    "${PIP}" install --quiet --upgrade pip setuptools wheel 2>/dev/null || true
    echo -e "   Installiere ${YELLOW}customtkinter${NC} ins venv..."
    "${PIP}" install --quiet customtkinter pillow dbus-python 2>/dev/null || \
    "${PIP}" install --quiet --break-system-packages \
      customtkinter pillow dbus-python 2>/dev/null || \
    echo -e "${YELLOW}   ⚠ pip ins venv fehlgeschlagen – versuche System-pip${NC}"
  fi

  # Wenn customtkinter immer noch fehlt: systemweit installieren als Fallback
  if ! "${INSTALL_DIR}/venv/bin/python3" -c "import customtkinter" 2>/dev/null && \
     ! python3 -c "import customtkinter" 2>/dev/null; then
    echo -e "   ${YELLOW}customtkinter fehlt systemweit – installiere mit --break-system-packages${NC}"
    pip3 install --quiet --break-system-packages customtkinter pillow 2>/dev/null || \
    pip3 install --quiet customtkinter pillow 2>/dev/null || \
    echo -e "${YELLOW}   ⚠ customtkinter konnte nicht installiert werden${NC}"
  fi

  # Prüfen
  if "${INSTALL_DIR}/venv/bin/python3" -c "import customtkinter" 2>/dev/null; then
    echo -e "${GREEN}   ✅ Python-Umgebung bereit (customtkinter gefunden)${NC}"
  else
    echo -e "${YELLOW}   ⚠ customtkinter nicht im venv – GUI nutzt System-Python${NC}"
  fi
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 5. QUELLDATEIEN KOPIEREN
# ═══════════════════════════════════════════════════════════════════════════════
install_files() {
  echo -e "${BLUE}📂 [5/9] Installiere Programmdateien...${NC}"

  # Python-Module
  for f in \
    grub_pilot_backend.py \
    grub_pilot_service.py \
    grub_pilot_gui.py \
    grub_pilot_cli.py \
    grub_pilot_colors.py \
    grub_pilot_lang.py \
    grub_pilot_config_manager.py \
    grub_pilot_grub_utils.py \
    grub_pilot_backup.py \
    grub_pilot_dbus_client.py \
    grub_pilot_toast.py \
    grub_pilot_sidebar.py \
    grub_pilot_page_home.py \
    grub_pilot_page_entries.py \
    grub_pilot_page_timeout.py \
    grub_pilot_page_themes.py \
    grub_pilot_page_backups.py \
    grub_pilot_page_settings.py \
    grub_pilot_page_help.py \
    grub_pilot_page_about.py \
    grub_pilot_create_icon.py \
    grub_pilot_theme_installer.py \
    grub_pilot_page_kernel.py \
    grub_pilot_page_repair.py \
    grub_pilot_page_wallpaper.py \
    grub_pilot_page_display.py \
    grub_pilot_page_efi.py \
    grub_pilot_page_logs.py \
    grub_pilot_page_custom.py \
    grub_pilot_page_profiles.py; do
    if [ -f "${SRC_DIR}/${f}" ]; then
      cp "${SRC_DIR}/${f}" "${INSTALL_DIR}/${f}"
      chmod 644 "${INSTALL_DIR}/${f}"
    else
      echo -e "${YELLOW}   ⚠ ${f} nicht gefunden – übersprungen${NC}"
    fi
  done

  # Ausführbarkeit setzen
  chmod +x "${INSTALL_DIR}/grub_pilot_backend.py"
  chmod +x "${INSTALL_DIR}/grub_pilot_gui.py"
  chmod +x "${INSTALL_DIR}/grub_pilot_cli.py"

  # Launcher-Wrapper installieren (kein Symlink – findet Python mit customtkinter)
  install -m 755 "${SRC_DIR}/grub-pilot-gui" /usr/local/bin/grub-pilot-gui
  ln -sf "${INSTALL_DIR}/grub_pilot_cli.py" /usr/local/bin/grub-pilot

  # Konfigurationsdatei (nicht überschreiben wenn vorhanden)
  if [ ! -f /etc/grub-pilot/config.ini ]; then
    cp "${SRC_DIR}/config.ini" /etc/grub-pilot/config.ini 2>/dev/null || true
  fi

  echo -e "${GREEN}   ✅ Dateien installiert${NC}"
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 6. SYSTEMDATEIEN
# ═══════════════════════════════════════════════════════════════════════════════
install_system_files() {
  echo -e "${BLUE}🔧 [6/9] Installiere Systemkonfiguration...${NC}"

  # D-Bus Policy
  cp "${SRC_DIR}/org.grubpilot.backend.conf" \
     /etc/dbus-1/system.d/org.grubpilot.backend.conf

  # PolKit Policy
  cp "${SRC_DIR}/org.grubpilot.policy" \
     /usr/share/polkit-1/actions/org.grubpilot.policy

  # systemd Service
  cp "${SRC_DIR}/grub-pilot-backend.service" \
     /etc/systemd/system/grub-pilot-backend.service

  # Desktop-Eintrag
  cp "${SRC_DIR}/grub-pilot.desktop" \
     /usr/share/applications/grub-pilot.desktop

  echo -e "${GREEN}   ✅ Systemdateien installiert${NC}"
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 7. ICON
# ═══════════════════════════════════════════════════════════════════════════════
create_icon() {
  echo -e "${BLUE}🎨 [7/9] Erstelle Anwendungsicon...${NC}"
  # Icon-Generator liegt als separate Datei neben install.sh
  ICON_SCRIPT="${SRC_DIR}/grub_pilot_create_icon.py"
  if [ -f "${ICON_SCRIPT}" ]; then
    "${INSTALL_DIR}/venv/bin/python3" "${ICON_SCRIPT}" 2>/dev/null || \
    python3 "${ICON_SCRIPT}" 2>/dev/null || \
    echo -e "${YELLOW}   ⚠ Icon konnte nicht erstellt werden (PIL nicht verfügbar)${NC}"
  else
    echo -e "${YELLOW}   ⚠ grub_pilot_create_icon.py nicht gefunden – übersprungen${NC}"
  fi
  echo -e "${GREEN}   ✅ Icon bereit${NC}"
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 8. DIENSTE AKTIVIEREN
# ═══════════════════════════════════════════════════════════════════════════════
activate_services() {
  echo -e "${BLUE}🚀 [8/9] Aktiviere Dienste...${NC}"

  # Stoppe ggf. laufende Instanz
  systemctl stop grub-pilot-backend.service 2>/dev/null || true

  # D-Bus und Polkit neu laden
  systemctl reload dbus 2>/dev/null || systemctl restart dbus 2>/dev/null || true
  systemctl restart polkit 2>/dev/null || \
  systemctl restart policykit-1 2>/dev/null || true

  systemctl daemon-reload
  systemctl enable grub-pilot-backend.service 2>/dev/null || true

  # Kurz warten bis D-Bus-Registrierung abgeschlossen
  systemctl start grub-pilot-backend.service 2>/dev/null || true
  for i in 1 2 3 4 5; do
    sleep 1
    if systemctl is-active --quiet grub-pilot-backend.service 2>/dev/null; then
      echo -e "   ${GREEN}✅ Backend-Service läuft${NC}"
      break
    fi
    [ "$i" -eq 5 ] && \
      echo -e "   ${YELLOW}⚠ Backend-Service nicht aktiv – prüfe: journalctl -u grub-pilot-backend${NC}"
  done

  echo -e "${GREEN}   ✅ Dienste konfiguriert${NC}"
  echo
}

# ═══════════════════════════════════════════════════════════════════════════════
# 9. ABSCHLUSS
# ═══════════════════════════════════════════════════════════════════════════════
finish() {
  echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║  ✅  Grub Pilot v2.0.1 erfolgreich installiert!              ║${NC}"
  echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
  echo
  echo -e "${CYAN}  GUI starten:${NC}   grub-pilot-gui"
  echo -e "${CYAN}  CLI nutzen: ${NC}   grub-pilot --help"
  echo -e "${CYAN}  Logs:       ${NC}   /var/log/grub-pilot/fehler.log"
  echo -e "${CYAN}  Backup:     ${NC}   ${EMERGENCY_BACKUP}"
  echo

  # GUI automatisch starten, wenn eine Display-Session aktiv ist
  if [ -n "${DISPLAY:-}" ] || [ -n "${WAYLAND_DISPLAY:-}" ]; then
    echo -e "${CYAN}  → Display erkannt – starte GUI...${NC}"
    # Als aufrufenden Benutzer starten (nicht als root)
    REAL_USER="${SUDO_USER:-${USER}}"
    if [ -n "${REAL_USER}" ] && [ "${REAL_USER}" != "root" ]; then
      su -c "DISPLAY=${DISPLAY:-:0} ${INSTALL_DIR}/venv/bin/python3 \
             ${INSTALL_DIR}/grub_pilot_gui.py &" "${REAL_USER}" 2>/dev/null || \
      "${INSTALL_DIR}/venv/bin/python3" "${INSTALL_DIR}/grub_pilot_gui.py" &
    else
      "${INSTALL_DIR}/venv/bin/python3" "${INSTALL_DIR}/grub_pilot_gui.py" &
    fi
  fi
}

# ═══════════════════════════════════════════════════════════════════════════════
# HAUPTABLAUF
# ═══════════════════════════════════════════════════════════════════════════════
main() {
  echo -e "${MAGENTA}╔══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${MAGENTA}║   Grub Pilot v2.0.1 – Installation startet                  ║${NC}"
  echo -e "${MAGENTA}╚══════════════════════════════════════════════════════════════╝${NC}"
  echo

  create_emergency_backup
  detect_system
  install_dependencies
  create_directories
  setup_python
  install_files
  install_system_files
  create_icon
  activate_services
  finish
}

main "$@"
