#!/bin/bash
# Grub Pilot – Notfall-Wiederherstellung
# Stellt die gesicherten Systemdateien wieder her und entfernt den Dienst.
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}❌ Bitte als root ausführen: sudo $0${NC}"; exit 1
fi

echo -e "${YELLOW}🔧 Grub Pilot – Notfall-Wiederherstellung${NC}"
echo

# Dienst stoppen und deaktivieren
systemctl stop    grub-pilot-backend.service 2>/dev/null || true
systemctl disable grub-pilot-backend.service 2>/dev/null || true

# Grub Pilot Systemdateien entfernen
rm -f /usr/share/polkit-1/actions/org.grubpilot.policy
rm -f /etc/dbus-1/system.d/org.grubpilot.backend.conf
rm -f /etc/systemd/system/grub-pilot-backend.service

# Gesicherte Originaldateien zurückschreiben
echo -e "${YELLOW}↩  Stelle gesicherte Konfigurationsdateien wieder her...${NC}"
RESTORED=0
while IFS= read -r -d '' file; do
  [[ "$(basename "$file")" == "restore-emergency.sh" ]] && continue
  target="${file#"$SCRIPT_DIR"}"
  if [ -z "$target" ] || [ "$target" = "/" ]; then continue; fi
  mkdir -p "$(dirname "$target")"
  cp -a "$file" "$target" 2>/dev/null && RESTORED=$((RESTORED+1)) || true
done < <(find "$SCRIPT_DIR" -type f -print0)

echo -e "${GREEN}   ✅ ${RESTORED} Datei(en) wiederhergestellt${NC}"

# Dienste neu laden
systemctl daemon-reload
systemctl reload dbus 2>/dev/null || systemctl restart dbus 2>/dev/null || true
systemctl restart polkit 2>/dev/null || systemctl restart policykit-1 2>/dev/null || true

echo
echo -e "${GREEN}✅ Notfall-Wiederherstellung abgeschlossen!${NC}"
echo -e "${YELLOW}   Bitte System neu starten, um alle Änderungen zu aktivieren.${NC}"
