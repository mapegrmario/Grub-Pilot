#!/bin/bash
# =============================================================================
# Grub Pilot v2.0.1 – VOLLSTÄNDIGE INSTALLATIONS-ANALYSE
# 12 Prüfbereiche | Erstellt: ~/grub-pilot-analyse-DATUM.log + grub-pilot-kurz.txt
# Aufruf: sudo bash grub-pilot-analyse.sh
# Autor: Mario Peeß / Großenhain  |  mapegr@mailbox.org
# =============================================================================

set -uo pipefail
shopt -s nullglob

INSTALL_DIR="/opt/grub-pilot"
BIN_GUI="/usr/local/bin/grub-pilot-gui"
BIN_CLI="/usr/local/bin/grub-pilot"
VENV_PYTHON="${INSTALL_DIR}/venv/bin/python3"
SERVICE_FILE="/etc/systemd/system/grub-pilot-backend.service"
DBUS_CONF="/etc/dbus-1/system.d/org.grubpilot.backend.conf"
POLKIT_POLICY="/usr/share/polkit-1/actions/org.grubpilot.policy"
SYSTEM_CONFIG="/etc/grub-pilot/config.ini"
BACKUP_DIR="/var/backups/grub-pilot"
LOG_DIR="/var/log/grub-pilot"
GRUB_DEFAULTS="/etc/default/grub"
GRUB_CFG="/boot/grub/grub.cfg"
GRUB_CFG2="/boot/grub2/grub.cfg"

LOG_USER="${SUDO_USER:-${USER:-$(logname 2>/dev/null || echo root)}}"
LOG_HOME=$(eval echo "~${LOG_USER}")
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="${LOG_HOME}/grub-pilot-analyse-${TIMESTAMP}.log"
SHORT_FILE="${LOG_HOME}/grub-pilot-analyse-kurz.txt"

RED='\033[1;31m'; GREEN='\033[1;32m'; YELLOW='\033[1;33m'
BLUE='\033[1;34m'; CYAN='\033[1;36m'; BOLD='\033[1m'; RESET='\033[0m'

ERRORS=0; WARNINGS=0; PASSED=0
declare -a ERROR_LIST=()
declare -a WARN_LIST=()

_log()  { echo "$*" >> "${LOG_FILE}"; }
OK()    { echo -e "  ${GREEN}✅  $*${RESET}";  _log "  [OK]   $*"; ((PASSED++));   }
FAIL()  { echo -e "  ${RED}❌  $*${RESET}";   _log "  [FAIL] $*"; ((ERRORS++));
          ERROR_LIST+=("$*"); }
WARN()  { echo -e "  ${YELLOW}⚠️   $*${RESET}"; _log "  [WARN] $*"; ((WARNINGS++));
          WARN_LIST+=("$*"); }
INFO()  { echo -e "  ${CYAN}ℹ️   $*${RESET}";  _log "  [INFO] $*"; }
HEAD()  {
    echo -e "\n${BOLD}${BLUE}╔══  $*  ══╗${RESET}"
    _log ""; _log "══════════════════════════════════════════════════"
    _log "  $*"; _log "══════════════════════════════════════════════════"
}

# ── Distro erkennen ──────────────────────────────────────────────────────────
OS_ID="unknown"; OS_NAME="Unknown Linux"
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_ID="${ID:-unknown}"; OS_NAME="${NAME:-Unknown Linux}"
    case "${ID}" in
        linuxmint|lmde|pop|elementary|zorin|kali|parrot) OS_ID='debian' ;;
    esac
    [[ "${OS_ID}" == "unknown" ]] && [[ -n "${ID_LIKE:-}" ]] && \
        for like in ${ID_LIKE}; do
            case "${like}" in
                debian|ubuntu) OS_ID="${like}"; break ;;
                fedora|rhel)   OS_ID="${like}"; break ;;
                arch)          OS_ID="${like}"; break ;;
                opensuse*|suse) OS_ID="${like}"; break ;;
            esac
        done
fi

PY="${VENV_PYTHON}"
command -v "${PY}" &>/dev/null || PY="python3"

# ── Banner ───────────────────────────────────────────────────────────────────
clear
echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Grub Pilot v2.0.1 – Vollständige Installations-Analyse   ║"
echo "║   Autor: Mario Peeß / Großenhain  |  mapegr@mailbox.org    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${RESET}"
_log "=============================================================="
_log "  GRUB PILOT v2.0.1 – INSTALLATIONS-ANALYSE"
_log "  Datum: $(date '+%d.%m.%Y %H:%M:%S') | Host: $(hostname) | User: $(whoami)"
_log "  Distribution: ${OS_NAME} (${OS_ID})"
_log "=============================================================="
echo "  Datum: $(date '+%d.%m.%Y %H:%M:%S')  |  Log: ${LOG_FILE}"
echo "  Distribution: ${BOLD}${OS_NAME}${RESET}  |  Architektur: $(uname -m)"

# ══════════════════════════════════════════════════════════════════════════════
HEAD "1  INSTALLATIONS-VERZEICHNISSE & STARTER"
# ══════════════════════════════════════════════════════════════════════════════

if [[ -d "${INSTALL_DIR}" ]]; then
    PY_COUNT=$(find "${INSTALL_DIR}" -maxdepth 1 -name "*.py" 2>/dev/null | wc -l)
    OK "Installationsordner: ${INSTALL_DIR}  (${PY_COUNT} Python-Dateien)"
else
    FAIL "Installationsordner fehlt: ${INSTALL_DIR}"
fi

[[ -f "${BIN_GUI}" && -x "${BIN_GUI}" ]]  && OK "GUI-Starter:  ${BIN_GUI}"  || FAIL "GUI-Starter fehlt oder nicht ausführbar"
[[ -f "${BIN_CLI}" ]]                     && OK "CLI-Starter:  ${BIN_CLI}"  || FAIL "CLI-Starter fehlt"
[[ -f "${SERVICE_FILE}" ]]                && OK "systemd-Unit: ${SERVICE_FILE}" || FAIL "systemd-Unit fehlt"
[[ -f "${DBUS_CONF}" ]]                   && OK "D-Bus Policy: ${DBUS_CONF}"    || FAIL "D-Bus Policy fehlt"
[[ -f "${POLKIT_POLICY}" ]]               && OK "PolKit Policy: ${POLKIT_POLICY}" || WARN "PolKit Policy fehlt"
[[ -f "${SYSTEM_CONFIG}" ]]               && OK "Konfig-Datei: ${SYSTEM_CONFIG}"  || WARN "Konfig-Datei fehlt (wird beim ersten Start erstellt)"

[[ -d "${BACKUP_DIR}" ]] \
    && OK "Backup-Ordner: ${BACKUP_DIR}  ($(find "${BACKUP_DIR}" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l) Backup(s))" \
    || WARN "Backup-Ordner fehlt: ${BACKUP_DIR}"

[[ -d "${LOG_DIR}" ]] \
    && OK "Log-Ordner: ${LOG_DIR}" \
    || WARN "Log-Ordner fehlt: ${LOG_DIR}"

[[ -f "/usr/share/applications/grub-pilot.desktop" ]] \
    && OK "Desktop-Eintrag vorhanden" \
    || WARN "Desktop-Eintrag fehlt"

[[ -x "${VENV_PYTHON}" ]] \
    && OK "Python venv: $("${VENV_PYTHON}" --version 2>&1)" \
    || WARN "venv nicht gefunden (${VENV_PYTHON}) – nutzt System-Python"

# ══════════════════════════════════════════════════════════════════════════════
HEAD "2  PYTHON-DATEIEN: ZEILEN, MD5, SYNTAX"
# ══════════════════════════════════════════════════════════════════════════════

declare -A REF_LINES=(
    ["grub_pilot_backend.py"]=55
    ["grub_pilot_service.py"]=175
    ["grub_pilot_gui.py"]=68
    ["grub_pilot_cli.py"]=82
    ["grub_pilot_colors.py"]=32
    ["grub_pilot_lang.py"]=145
    ["grub_pilot_config_manager.py"]=46
    ["grub_pilot_grub_utils.py"]=86
    ["grub_pilot_backup.py"]=58
    ["grub_pilot_theme_installer.py"]=92
    ["grub_pilot_page_kernel.py"]=110
    ["grub_pilot_page_repair.py"]=100
    ["grub_pilot_page_wallpaper.py"]=95
    ["grub_pilot_page_display.py"]=100
    ["grub_pilot_page_efi.py"]=115
    ["grub_pilot_page_logs.py"]=110
    ["grub_pilot_page_custom.py"]=80
    ["grub_pilot_page_profiles.py"]=100
    ["grub_pilot_dbus_client.py"]=34
    ["grub_pilot_toast.py"]=32
    ["grub_pilot_sidebar.py"]=72
    ["grub_pilot_page_home.py"]=62
    ["grub_pilot_page_entries.py"]=56
    ["grub_pilot_page_timeout.py"]=55
    ["grub_pilot_page_themes.py"]=140
    ["grub_pilot_page_backups.py"]=76
    ["grub_pilot_page_settings.py"]=68
    ["grub_pilot_page_help.py"]=66
    ["grub_pilot_page_about.py"]=80
)

printf "  %-38s %7s %7s  %-14s  %s\n" "Datei" "Ref-Z" "Ist-Z" "MD5(12)" "Status"
printf "  %-38s %7s %7s  %-14s  %s\n" \
    "──────────────────────────────────────" "───────" "───────" "──────────────" "──────"
_log ""

FILE_ERRORS=0
for fn in "${!REF_LINES[@]}"; do
    fp="${INSTALL_DIR}/${fn}"
    ref="${REF_LINES[$fn]}"
    if [[ ! -f "${fp}" ]]; then
        printf "  %-38s %7s %7s  %-14s  " "${fn}" "${ref}" "FEHLT" "–"
        echo -e "${RED}❌ FEHLT${RESET}"
        _log "  ${fn}: FEHLT"
        ((ERRORS++)); ((FILE_ERRORS++))
        ERROR_LIST+=("${fn}: Datei fehlt")
        continue
    fi
    ist=$(wc -l < "${fp}")
    md=$(md5sum "${fp}" | cut -c1-12)
    if ! ${PY} -m py_compile "${fp}" 2>/tmp/gp_syn_$$.txt; then
        printf "  %-38s %7s %7s  %-14s  " "${fn}" "${ref}" "${ist}" "${md}"
        echo -e "${RED}❌ SYNTAXFEHLER: $(head -1 /tmp/gp_syn_$$.txt)${RESET}"
        ((ERRORS++)); ((FILE_ERRORS++))
        ERROR_LIST+=("${fn}: Syntaxfehler")
    elif [[ "${ist}" -lt $((ref - 15)) ]]; then
        printf "  %-38s %7s %7s  %-14s  " "${fn}" "${ref}" "${ist}" "${md}"
        echo -e "${RED}❌ KÜRZER als erwartet${RESET}"
        _log "  ${fn}: KÜRZER (${ist} statt ${ref})"
        ((ERRORS++)); ((FILE_ERRORS++))
        ERROR_LIST+=("${fn}: Nur ${ist} statt ${ref} Zeilen")
    else
        printf "  %-38s %7s %7s  %-14s  " "${fn}" "${ref}" "${ist}" "${md}"
        echo -e "${GREEN}✅ OK${RESET}"
        _log "  ${fn}: OK (${ist} Zeilen, MD5=${md})"
        ((PASSED++))
    fi
    rm -f /tmp/gp_syn_$$.txt
done

[[ ${FILE_ERRORS} -eq 0 ]] && echo -e "\n  ${GREEN}Alle ${#REF_LINES[@]} Python-Dateien vorhanden und syntaktisch korrekt.${RESET}"

# ══════════════════════════════════════════════════════════════════════════════
HEAD "3  KRITISCHE KLASSEN & METHODEN"
# ══════════════════════════════════════════════════════════════════════════════

${PY} - << 'PYCHECK' 2>&1 | tee -a "${LOG_FILE}"
import sys, os, ast
INSTALL_DIR = "/opt/grub-pilot"

REQUIRED = {
    "grub_pilot_service.py": {
        "GrubPilotBackend": [
            "get_system_info","list_boot_entries","set_default_entry",
            "set_timeout","modify_kernel_params","list_themes","set_theme",
            "list_backups","restore_backup",
            "_check_secure_boot","_get_grub_version","_ok","_err",
        ]
    },
    "grub_pilot_gui.py": {
        "GrubPilotApp": [
            "__init__","_setup_window","_build_layout",
            "_navigate","_make_page","_rebuild_ui",
        ]
    },
    "grub_pilot_sidebar.py": {
        "Sidebar": [
            "__init__","_build","_btn","_click",
            "set_active","_set_visual","rebuild",
        ]
    },
    "grub_pilot_grub_utils.py": {
        # Modulebene – Funktionen direkt prüfen
        "__module__": [
            "detect_grub_update_cmd","run_grub_update",
            "detect_grub_set_default_cmd","read_grub_defaults","safe_write_grub",
        ]
    },
    "grub_pilot_backup.py": {
        "__module__": ["create_backup","list_backups","restore_backup"]
    },
    "grub_pilot_dbus_client.py": {
        "DBusClient": ["__init__","_connect","call"]
    },
    "grub_pilot_toast.py": {
        "ToastManager": ["show","success","error","info","warning"]
    },
}

errors = 0; passed = 0

def check_file(fn, classes):
    global errors, passed
    fp = os.path.join(INSTALL_DIR, fn)
    if not os.path.isfile(fp):
        print(f"  ❌  {fn}: FEHLT"); errors += 1; return
    try:
        tree = ast.parse(open(fp).read())
    except SyntaxError as e:
        print(f"  ❌  {fn}: Syntaxfehler: {e}"); errors += 1; return

    module_funcs = {n.name for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef)}
    class_map = {n.name: {m.name for m in ast.walk(n)
                           if isinstance(m, ast.FunctionDef)}
                 for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

    for cls, methods in classes.items():
        if cls == "__module__":
            for m in methods:
                if m in module_funcs:
                    passed += 1
                else:
                    print(f"  ❌  {fn}: Funktion '{m}()' FEHLT"); errors += 1
        else:
            if cls not in class_map:
                print(f"  ❌  {fn}: Klasse '{cls}' FEHLT"); errors += 1
                continue
            for m in methods:
                if m in class_map[cls]:
                    passed += 1
                else:
                    print(f"  ❌  {fn}: {cls}.{m}() FEHLT"); errors += 1

for fn, cls in REQUIRED.items():
    check_file(fn, cls)

# Rekursions-Sicherheit: set_active darf on_navigate NICHT aufrufen
fp = os.path.join(INSTALL_DIR, "grub_pilot_sidebar.py")
if os.path.isfile(fp):
    src = open(fp).read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "set_active":
            calls = [n.func.attr for n in ast.walk(node)
                     if isinstance(n, ast.Call) and hasattr(n.func,'attr')]
            if "on_navigate" in calls:
                print("  ❌  grub_pilot_sidebar: set_active() ruft on_navigate auf → ENDLOSREKURSION!")
                errors += 1
            else:
                print("  ✅  sidebar.set_active(): kein on_navigate-Aufruf (Rekursionsschutz OK)")
                passed += 1

if errors == 0:
    print(f"  ✅  Alle kritischen Methoden vorhanden ({passed} geprüft)")
else:
    print(f"\n  Ergebnis: {passed} OK, {errors} FEHLER")
sys.exit(errors)
PYCHECK
[[ $? -eq 0 ]] && OK "Methoden-Check bestanden" || FAIL "Methoden-Check: Fehler gefunden"

# ══════════════════════════════════════════════════════════════════════════════
HEAD "4  PYTHON IMPORTS & LAUFZEIT-PLAUSIBILITÄT"
# ══════════════════════════════════════════════════════════════════════════════

${PY} - << 'PYIMPORT' 2>&1 | tee -a "${LOG_FILE}"
import sys, os
sys.path.insert(0, "/opt/grub-pilot")
errors = 0

# Kern-Module
for mod in [
    "grub_pilot_colors","grub_pilot_lang","grub_pilot_config_manager",
    "grub_pilot_grub_utils","grub_pilot_backup","grub_pilot_dbus_client",
    "grub_pilot_toast","grub_pilot_sidebar",
    "grub_pilot_page_home","grub_pilot_page_entries","grub_pilot_page_timeout",
    "grub_pilot_page_themes","grub_pilot_page_backups","grub_pilot_page_settings",
    "grub_pilot_page_help","grub_pilot_page_about",
]:
    try:
        __import__(mod)
        print(f"  ✅  {mod}.py")
    except Exception as e:
        print(f"  ❌  {mod}.py: {e}"); errors += 1

# Backend-Module (dbus – nur bei Root/systemd importierbar)
for mod in ["grub_pilot_backend","grub_pilot_service"]:
    try:
        __import__(mod)
        print(f"  ✅  {mod}.py")
    except ImportError as e:
        if "dbus" in str(e) or "gi" in str(e):
            print(f"  ⚠️   {mod}.py: dbus/gi nicht im Import-Pfad (normal ohne Root/systemd)")
        else:
            print(f"  ❌  {mod}.py: {e}"); errors += 1
    except Exception as e:
        print(f"  ⚠️   {mod}.py: {e}")

print()

# Kritische Einzelprüfungen
import ast

# DBusGMainLoop muss auf Modulebene in backend.py stehen (VOR jeder Klasse)
fp = "/opt/grub-pilot/grub_pilot_backend.py"
if os.path.isfile(fp):
    src = open(fp).read()
    if "DBusGMainLoop(set_as_default=True)" in src:
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if "DBusGMainLoop" in line and "set_as_default" in line:
                # Muss vor der ersten Klassendefinition stehen
                class_lines = [j for j,l in enumerate(lines) if l.strip().startswith("class ")]
                if not class_lines or i < class_lines[0]:
                    print("  ✅  DBusGMainLoop auf Modulebene (vor Klassen) ← kritischer Fix")
                else:
                    print("  ❌  DBusGMainLoop NACH Klassendefinition → D-Bus-Fehler!"); errors += 1
                break
    else:
        print("  ❌  DBusGMainLoop(set_as_default=True) fehlt in backend.py!"); errors += 1

# safe_write_grub: tmp.close() muss vor shutil.move aufgerufen werden
fp = "/opt/grub-pilot/grub_pilot_grub_utils.py"
if os.path.isfile(fp):
    src = open(fp).read()
    # Prüfe ob grub-script-check als subprocess-Aufruf (List-Literal) vorkommt
    # Ein Vorkommen nur in Kommentaren/Docstrings ist kein Fehler
    gsc_in_call = False
    try:
        tree_g = ast.parse(src)
        for node in ast.walk(tree_g):
            if isinstance(node, ast.List):
                for elt in node.elts:
                    if isinstance(elt, ast.Constant) and "grub-script-check" in str(elt.value):
                        gsc_in_call = True
    except Exception:
        pass
    if gsc_in_call:
        print("  ❌  grub_pilot_grub_utils: grub-script-check als Befehlsaufruf vorhanden (falsches Tool!)"); errors += 1
    else:
        print("  ✅  grub_pilot_grub_utils: grub-script-check nicht als Aufruf vorhanden (nur in Kommentaren OK)")
    if "tmp.close()" in src:
        print("  ✅  grub_pilot_grub_utils: tmp.close() vor shutil.move vorhanden")
    else:
        print("  ❌  grub_pilot_grub_utils: tmp.close() fehlt → File-Descriptor-Leak!"); errors += 1

# safe_write_grub Rückgabe muss in set_timeout/set_default geprüft werden
if os.path.isfile("/opt/grub-pilot/grub_pilot_service.py"):
    src = open("/opt/grub-pilot/grub_pilot_service.py").read()
    if "if not safe_write_grub" in src:
        print("  ✅  grub_pilot_service: safe_write_grub Rückgabe wird geprüft")
    else:
        print("  ⚠️   grub_pilot_service: safe_write_grub Rückgabe möglicherweise ungeprüft")

# Keine bare except: in kritischen Dateien
for fn in ["grub_pilot_service.py","grub_pilot_grub_utils.py","grub_pilot_backup.py"]:
    fp = os.path.join("/opt/grub-pilot", fn)
    if not os.path.isfile(fp): continue
    tree = ast.parse(open(fp).read())
    bare = sum(1 for n in ast.walk(tree)
               if isinstance(n, ast.ExceptHandler) and n.type is None)
    if bare > 0:
        print(f"  ⚠️   {fn}: {bare}× bare 'except:' (sollte 'except Exception:' sein)")
    else:
        print(f"  ✅  {fn}: kein bare except:")

sys.exit(errors)
PYIMPORT
[[ $? -eq 0 ]] && OK "Import-Check bestanden" || FAIL "Import-Check: Fehler gefunden"

# ══════════════════════════════════════════════════════════════════════════════
HEAD "5  SYSTEM-ABHÄNGIGKEITEN"
# ══════════════════════════════════════════════════════════════════════════════

# format: "befehl:paket:beschreibung:pflicht|optional"
TOOLS=(
    "python3:python3:Python 3:pflicht"
    "python3-tk::Tkinter GUI-Grundlage:pflicht"
    "customtkinter::CustomTkinter (pip):pflicht"
    "dbus-daemon:dbus:D-Bus Daemon:pflicht"
    "pkexec:policykit-1:PolKit Root-Rechte:pflicht"
    "systemctl:systemd:Dienstverwaltung:pflicht"
    "update-grub:grub2-common:GRUB Update (Debian):optional"
    "grub2-mkconfig:grub2-tools:GRUB Update (Fedora):optional"
    "grub-mkconfig:grub:GRUB Update (Arch):optional"
    "grub-set-default:grub2-common:Boot-Standard setzen:optional"
    "grub2-set-default:grub2-tools:Boot-Standard (Fedora):optional"
    "efibootmgr:efibootmgr:UEFI Boot Manager:optional"
    "mokutil:mokutil:Secure Boot Status:optional"
    "os-prober:os-prober:Dual-Boot-Erkennung:optional"
    "md5sum:coreutils:Datei-Prüfsummen:pflicht"
    "git:git:Versionsverwaltung:optional"
)

for entry in "${TOOLS[@]}"; do
    IFS=':' read -r cmd pkg desc prio <<< "${entry}"
    found=false
    if [[ "${cmd}" == "python3-tk" ]]; then
        ${PY} -c "import tkinter" 2>/dev/null && found=true
    elif [[ "${cmd}" == "customtkinter" ]]; then
        ${PY} -c "import customtkinter" 2>/dev/null && found=true
    else
        command -v "${cmd}" &>/dev/null && found=true
    fi

    if ${found}; then
        VER=""
        case "${cmd}" in
            python3)       VER=$(python3 --version 2>&1 | head -1) ;;
            customtkinter) VER=$(${PY} -c "import customtkinter; print(customtkinter.__version__)" 2>/dev/null) ;;
        esac
        OK "${cmd}  ${desc}${VER:+  (${VER})}"
    else
        [[ "${prio}" == "pflicht" ]] \
            && FAIL "${cmd} FEHLT → ${pkg:+apt/pip install ${pkg}}" \
            || WARN "${cmd} fehlt (optional) – ${desc}"
    fi
done

# Mindestens ein grub-update-Befehl muss vorhanden sein
GRUB_UPDATE_FOUND=false
for gc in update-grub grub2-mkconfig grub-mkconfig; do
    command -v "${gc}" &>/dev/null && GRUB_UPDATE_FOUND=true && break
done
${GRUB_UPDATE_FOUND} \
    && OK "GRUB-Update-Befehl vorhanden" \
    || FAIL "Kein GRUB-Update-Befehl gefunden (update-grub / grub2-mkconfig / grub-mkconfig)"

# ══════════════════════════════════════════════════════════════════════════════
HEAD "6  PYTHON-MODULE"
# ══════════════════════════════════════════════════════════════════════════════

${PY} - << 'PYMOD' 2>&1 | tee -a "${LOG_FILE}"
import sys
for mod, pkg, req in [
    ("tkinter",       "python3-tk",                True),
    ("customtkinter", "pip: customtkinter",         True),
    ("dbus",          "python3-dbus / dbus-python", True),
    ("gi",            "python3-gi / PyGObject",     True),
    ("gi.repository.GLib", "python3-gi",            True),
    ("configparser",  "eingebaut",                  True),
    ("subprocess",    "eingebaut",                  True),
    ("json",          "eingebaut",                  True),
    ("shutil",        "eingebaut",                  True),
    ("tempfile",      "eingebaut",                  True),
    ("re",            "eingebaut",                  True),
    ("ast",           "eingebaut",                  True),
    ("PIL",           "pip: pillow",                False),
]:
    try:
        m = __import__(mod)
        v = getattr(m, '__version__', '')
        print(f"  ✅  {mod}  {v and f'({v})' or ''}")
    except ImportError:
        sym = "❌" if req else "⚠️ "
        sev = "FEHLT → install" if req else "fehlt (optional)"
        print(f"  {sym}  {mod}: {sev} {pkg}")
PYMOD

# ══════════════════════════════════════════════════════════════════════════════
HEAD "7  SYSTEMD-DIENST & D-BUS"
# ══════════════════════════════════════════════════════════════════════════════

# systemd-Unit prüfen
if [[ -f "${SERVICE_FILE}" ]]; then
    OK "Service-Datei: ${SERVICE_FILE}"
    grep -q "BusName=org.grubpilot.backend" "${SERVICE_FILE}" \
        && OK "BusName korrekt (org.grubpilot.backend)" \
        || FAIL "BusName fehlt oder falsch in ${SERVICE_FILE}"
    grep -q "User=root" "${SERVICE_FILE}" \
        && OK "User=root konfiguriert" \
        || WARN "User=root fehlt – Backend benötigt Root-Rechte"
    grep -q "Restart=on-failure" "${SERVICE_FILE}" \
        && OK "Restart-Policy: on-failure" \
        || WARN "Restart-Policy fehlt"
    EXEC_PATH=$(grep "ExecStart=" "${SERVICE_FILE}" | cut -d= -f2 | awk '{print $1}' | head -1)
    [[ -n "${EXEC_PATH}" && -f "${EXEC_PATH}" ]] \
        && OK "ExecStart-Pfad existiert: ${EXEC_PATH}" \
        || FAIL "ExecStart-Pfad nicht gefunden: ${EXEC_PATH:-unbekannt}"
else
    FAIL "Service-Datei fehlt: ${SERVICE_FILE}"
fi

# Service-Status
if command -v systemctl &>/dev/null; then
    SVC_STATUS=$(systemctl is-active grub-pilot-backend.service 2>/dev/null | head -1 | tr -d '[:space:]' || echo "unbekannt")
    case "${SVC_STATUS}" in
        active)     OK   "Service-Status: active (läuft)" ;;
        activating) WARN "Service-Status: activating (startet noch – Import-Fehler prüfen)" ;;
        inactive)   WARN "Service-Status: inactive (gestoppt)  →  sudo systemctl start grub-pilot-backend" ;;
        failed)     FAIL "Service-Status: failed  →  sudo journalctl -u grub-pilot-backend -n 20" ;;
        *)          WARN "Service-Status: ${SVC_STATUS}" ;;
    esac

    SVC_ENABLED=$(systemctl is-enabled grub-pilot-backend.service 2>/dev/null || echo "unbekannt")
    [[ "${SVC_ENABLED}" == "enabled" ]] \
        && OK  "Service aktiviert (autostart beim Boot)" \
        || WARN "Service nicht aktiviert: ${SVC_ENABLED}"
fi

# D-Bus Policy
if [[ -f "${DBUS_CONF}" ]]; then
    OK "D-Bus Policy vorhanden"
    grep -q "org.grubpilot.backend" "${DBUS_CONF}" \
        && OK "Interface in Policy korrekt" \
        || FAIL "Interface fehlt in D-Bus Policy"
else
    FAIL "D-Bus Policy fehlt: ${DBUS_CONF}"
fi

# D-Bus erreichbar?
${PY} - << 'PYDBUS' 2>&1 | tee -a "${LOG_FILE}"
import sys
try:
    import dbus
    import dbus.mainloop.glib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus   = dbus.SystemBus()
    names = [str(n) for n in bus.list_names() if "grubpilot" in str(n).lower()]
    if names:
        print(f"  ✅  Backend auf D-Bus erreichbar: {names}")
    else:
        print(f"  ⚠️   Backend NICHT auf D-Bus registriert")
        print(f"       → sudo systemctl start grub-pilot-backend")
except Exception as e:
    print(f"  ⚠️   D-Bus-Test: {e}")
PYDBUS

# ══════════════════════════════════════════════════════════════════════════════
HEAD "8  GRUB-KONFIGURATION"
# ══════════════════════════════════════════════════════════════════════════════

# /etc/default/grub
if [[ -f "${GRUB_DEFAULTS}" ]]; then
    OK "/etc/default/grub vorhanden"
    grep -q "GRUB_DEFAULT"  "${GRUB_DEFAULTS}" && OK "GRUB_DEFAULT definiert"  || WARN "GRUB_DEFAULT fehlt"
    grep -q "GRUB_TIMEOUT"  "${GRUB_DEFAULTS}" && OK "GRUB_TIMEOUT definiert"  || WARN "GRUB_TIMEOUT fehlt"
    grep -q "GRUB_CMDLINE"  "${GRUB_DEFAULTS}" && OK "GRUB_CMDLINE definiert"  || WARN "GRUB_CMDLINE fehlt"
    DEF_VAL=$(grep "^GRUB_DEFAULT=" "${GRUB_DEFAULTS}" | cut -d= -f2 | tr -d '"')
    TMO_VAL=$(grep "^GRUB_TIMEOUT=" "${GRUB_DEFAULTS}" | cut -d= -f2)
    INFO "  GRUB_DEFAULT=${DEF_VAL:-?}  |  GRUB_TIMEOUT=${TMO_VAL:-?}"

    # Backup der Originaldatei sollte existieren
    [[ -f "${GRUB_DEFAULTS}.grub-pilot-bak" ]] \
        && OK "Backup von /etc/default/grub vorhanden (.grub-pilot-bak)" \
        || INFO "Kein Grub-Pilot-Backup der GRUB-Defaults (noch keine Änderungen vorgenommen)"
else
    WARN "/etc/default/grub nicht gefunden – BLS-System oder ungewöhnliches Setup"
fi

# /boot/grub/grub.cfg oder grub2
GRUB_CFG_FOUND=""
for p in "${GRUB_CFG}" "${GRUB_CFG2}" \
    "/boot/efi/EFI/fedora/grub.cfg" "/boot/efi/EFI/debian/grub.cfg" \
    "/boot/efi/EFI/linuxmint/grub.cfg"; do
    [[ -f "${p}" ]] && GRUB_CFG_FOUND="${p}" && break
done

if [[ -n "${GRUB_CFG_FOUND}" ]]; then
    ENTRY_COUNT=$(grep -c "^menuentry" "${GRUB_CFG_FOUND}" 2>/dev/null || echo 0)
    OK "grub.cfg: ${GRUB_CFG_FOUND}  (${ENTRY_COUNT} Boot-Einträge)"
else
    WARN "Kein grub.cfg gefunden (EFI-Pfad evtl. abweichend)"
fi

# BLS-Einträge
if [[ -d "/boot/loader/entries" ]]; then
    BLS_COUNT=$(find /boot/loader/entries -name "*.conf" 2>/dev/null | wc -l)
    OK "BLS-Boot erkannt: ${BLS_COUNT} Einträge in /boot/loader/entries"
else
    INFO "BLS-Boot nicht aktiv (klassisches GRUB-Setup)"
fi

# UEFI
if [[ -d /sys/firmware/efi ]]; then
    OK "Boot-Modus: UEFI"
    command -v efibootmgr &>/dev/null \
        && INFO "  EFI-Einträge: $(efibootmgr 2>/dev/null | grep -c "Boot[0-9]" || echo '?')" \
        || INFO "  efibootmgr nicht verfügbar"
else
    INFO "Boot-Modus: Legacy BIOS"
fi

# Secure Boot
if command -v mokutil &>/dev/null; then
    SB=$(mokutil --sb-state 2>/dev/null | grep -o "enabled\|disabled" || echo "unbekannt")
    INFO "  Secure Boot: ${SB}"
fi

# ══════════════════════════════════════════════════════════════════════════════
HEAD "9  BACKUPS & NOTFALL-BACKUP"
# ══════════════════════════════════════════════════════════════════════════════

if [[ -d "${BACKUP_DIR}" ]]; then
    BACKUP_COUNT=$(find "${BACKUP_DIR}" -maxdepth 1 -type d -name "backup_*" 2>/dev/null | wc -l)
    [[ "${BACKUP_COUNT}" -gt 0 ]] \
        && OK "${BACKUP_COUNT} Grub-Pilot-Backup(s) in ${BACKUP_DIR}" \
        || INFO "Noch keine Grub-Pilot-Backups vorhanden (werden beim ersten Schreiben erstellt)"

    # Jüngstes Backup zeigen
    LATEST=$(find "${BACKUP_DIR}" -maxdepth 1 -type d -name "backup_*" 2>/dev/null | sort | tail -1)
    if [[ -n "${LATEST}" ]]; then
        INFO "  Jüngstes Backup: $(basename "${LATEST}")"
        [[ -f "${LATEST}/manifest.json" ]] \
            && OK  "  manifest.json vorhanden" \
            || WARN "  manifest.json fehlt in ${LATEST}"
        BFILE_COUNT=$(find "${LATEST}" -type f ! -name "manifest.json" 2>/dev/null | wc -l)
        INFO "  ${BFILE_COUNT} gesicherte Datei(en) in diesem Backup"
    fi
else
    WARN "Backup-Verzeichnis nicht vorhanden: ${BACKUP_DIR}"
fi

# Notfall-Backup (angelegt durch install.sh)
EMERGENCY=$(find /root -maxdepth 1 -type d -name "grub-pilot-emergency-backup-*" 2>/dev/null | sort | tail -1)
if [[ -n "${EMERGENCY}" ]]; then
    OK "Notfall-Backup: ${EMERGENCY}"
    [[ -f "${EMERGENCY}/restore-emergency.sh" ]] \
        && OK "  restore-emergency.sh vorhanden" \
        || WARN "  restore-emergency.sh fehlt"
else
    WARN "Kein Notfall-Backup in /root gefunden (install.sh legt es automatisch an)"
fi

# ══════════════════════════════════════════════════════════════════════════════
HEAD "10  BERECHTIGUNGEN & SICHERHEIT"
# ══════════════════════════════════════════════════════════════════════════════

# Dateiberechtigungen kritischer Systemdateien
for path_perm in \
    "${SERVICE_FILE}:644" \
    "${DBUS_CONF}:644" \
    "${POLKIT_POLICY}:644" \
    "${INSTALL_DIR}/grub_pilot_backend.py:755" \
    "${INSTALL_DIR}/grub_pilot_service.py:644"; do
    IFS=':' read -r path exp_perm <<< "${path_perm}"
    [[ -f "${path}" ]] || continue
    ist_perm=$(stat -c '%a' "${path}" 2>/dev/null || echo "???")
    [[ "${ist_perm}" == "${exp_perm}" ]] \
        && OK  "$(basename "${path}"): Berechtigung ${ist_perm} ✓" \
        || WARN "$(basename "${path}"): Berechtigung ${ist_perm} (erwartet ${exp_perm})"
done

# Ausführbarkeit der Starter
[[ -x "${BIN_GUI}" ]] && OK  "${BIN_GUI}: ausführbar" || FAIL "${BIN_GUI}: NICHT ausführbar"
[[ -x "${BIN_CLI}" ]] && OK  "${BIN_CLI}: ausführbar" || FAIL "${BIN_CLI}: NICHT ausführbar"

# /etc/default/grub schreibbar für Root?
if [[ -f "${GRUB_DEFAULTS}" ]]; then
    [[ -w "${GRUB_DEFAULTS}" ]] \
        && OK  "/etc/default/grub: für Root schreibbar" \
        || FAIL "/etc/default/grub: NICHT schreibbar – GRUB-Änderungen unmöglich"
fi

# Sudoers/PolKit – Root-Zugriff für Backend
[[ $EUID -eq 0 ]] \
    && OK  "Analyse läuft als Root – Berechtigungs-Test vollständig" \
    || WARN "Analyse läuft NICHT als Root – einige Prüfungen eingeschränkt"

# ══════════════════════════════════════════════════════════════════════════════
HEAD "11  KONFIGURATION & LOGS"
# ══════════════════════════════════════════════════════════════════════════════

# System-Config
if [[ -f "${SYSTEM_CONFIG}" ]]; then
    OK "System-Konfiguration: ${SYSTEM_CONFIG}"
    ${PY} - << PYCFG 2>/dev/null | tee -a "${LOG_FILE}"
import configparser, os
cfg = configparser.ConfigParser()
cfg.read("${SYSTEM_CONFIG}")
for sec in cfg.sections():
    for k,v in cfg.items(sec):
        print(f"  ℹ️   [{sec}] {k} = {v}")
PYCFG
else
    INFO "Systemweite Konfiguration noch nicht vorhanden (wird beim ersten Start erstellt)"
fi

# User-Config
USER_CONFIG="${LOG_HOME}/.config/grub-pilot/config.ini"
if [[ -f "${USER_CONFIG}" ]]; then
    OK "Benutzer-Konfiguration: ${USER_CONFIG}"
else
    INFO "Benutzer-Konfiguration noch nicht vorhanden (normal)"
fi

# Backend-Log
BACKEND_LOG="${LOG_DIR}/fehler.log"
if [[ -f "${BACKEND_LOG}" ]]; then
    ERR_LINES=$(wc -l < "${BACKEND_LOG}")
    ERROR_ENTRIES=$(grep -c "\[ERROR\]\|\[CRITICAL\]" "${BACKEND_LOG}" 2>/dev/null || echo 0)
    [[ "${ERROR_ENTRIES}" -gt 0 ]] \
        && WARN "Backend-Log: ${ERROR_ENTRIES} Fehlereinträge in ${BACKEND_LOG}" \
        || OK  "Backend-Log: ${ERR_LINES} Einträge, keine Fehler"
    INFO "  Letzte 5 Log-Einträge:"
    tail -5 "${BACKEND_LOG}" | while IFS= read -r line; do INFO "    ${line}"; done
else
    INFO "Backend-Log noch nicht vorhanden (Backend wurde noch nicht gestartet)"
fi

# GUI-Log (Benutzer)
GUI_LOG="${LOG_HOME}/.local/share/grub-pilot/gui.log"
if [[ -f "${GUI_LOG}" ]]; then
    GUI_ERR=$(grep -c "\[ERROR\]" "${GUI_LOG}" 2>/dev/null || echo 0)
    if [[ "${GUI_ERR}" -gt 0 ]]; then
        WARN "GUI-Log: ${GUI_ERR} Fehlereinträge in ${GUI_LOG}"
        INFO "  Letzte Fehler-Einträge:"
        grep "\[ERROR\]" "${GUI_LOG}" | tail -3 | while IFS= read -r line; do
            INFO "    ${line}"
        done
    else
        OK "GUI-Log vorhanden, keine Fehler (${GUI_LOG})"
    fi
else
    INFO "GUI-Log nicht vorhanden (GUI wurde noch nicht gestartet)"
fi

# ══════════════════════════════════════════════════════════════════════════════
HEAD "12  SHELL-SCRIPTS SYNTAX"
# ══════════════════════════════════════════════════════════════════════════════

for script in install.sh restore-emergency.sh grub-pilot-gui; do
    # Suche im aktuellen Ordner und im Installationsordner
    for sp in "./${script}" "${INSTALL_DIR}/${script}" "/usr/local/bin/${script}"; do
        [[ -f "${sp}" ]] || continue
        bash -n "${sp}" 2>/dev/null \
            && OK  "${script}: Bash-Syntax OK  (${sp})" \
            || FAIL "${script}: Bash-Syntaxfehler in ${sp}"
        break
    done
done

# Launcher: korrekter Aufbau
for launcher in "/usr/local/bin/grub-pilot-gui" "./grub-pilot-gui"; do
    [[ -f "${launcher}" ]] || continue
    grep -q "find_python" "${launcher}" \
        && OK  "grub-pilot-gui: Python-Finder-Funktion vorhanden" \
        || WARN "grub-pilot-gui: find_python fehlt – veraltete Version"
    grep -q "apt-get install" "${launcher}" && grep -q "tkinter" "${launcher}" \
        && OK  "grub-pilot-gui: tkinter-Auto-Install vorhanden" \
        || WARN "grub-pilot-gui: tkinter-Auto-Install fehlt"
    grep -q "exec.*\${FOUND}" "${launcher}" \
        && OK  "grub-pilot-gui: exec-Aufruf vorhanden" \
        || WARN "grub-pilot-gui: exec-Aufruf fehlt"
    break
done

# Prüfen ob install.sh shopt -s nullglob enthält (kritischer Fix)
for isp in "./install.sh" "${INSTALL_DIR}/install.sh"; do
    [[ -f "${isp}" ]] || continue
    grep -q "nullglob" "${isp}" \
        && OK  "install.sh: shopt -s nullglob vorhanden (Glob-Fix)" \
        || WARN "install.sh: nullglob fehlt – Glob-Fehler möglich"
    grep -q "ID_LIKE\|linuxmint\|lmde" "${isp}" \
        && OK  "install.sh: LMDE/Mint-Erkennung vorhanden" \
        || WARN "install.sh: LMDE/Mint-Erkennung fehlt"
    break
done

# ══════════════════════════════════════════════════════════════════════════════
HEAD "ZUSAMMENFASSUNG"
# ══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "  ${BOLD}Ergebnis:  ${GREEN}${PASSED} OK${RESET}  ${RED}${ERRORS} Fehler${RESET}  ${YELLOW}${WARNINGS} Warnungen${RESET}"
_log ""
_log "ZUSAMMENFASSUNG: ${PASSED} OK / ${ERRORS} Fehler / ${WARNINGS} Warnungen"

if [[ ${ERRORS} -eq 0 ]]; then
    echo -e "\n  ${GREEN}${BOLD}✅ Grub Pilot ist vollständig und fehlerfrei installiert.${RESET}"
else
    echo -e "\n  ${RED}${BOLD}❌ ${ERRORS} kritische Fehler:${RESET}"
    for e in "${ERROR_LIST[@]}"; do echo -e "    ${RED}•  ${e}${RESET}"; done
fi

[[ ${WARNINGS} -gt 0 ]] && {
    echo -e "\n  ${YELLOW}${BOLD}⚠️  ${WARNINGS} Warnungen:${RESET}"
    for w in "${WARN_LIST[@]}"; do echo -e "    ${YELLOW}•  ${w}${RESET}"; done
}

echo -e "\n  ${BOLD}Reparatur:${RESET} sudo bash install.sh"
echo -e "  ${BOLD}Dienst:   ${RESET} sudo systemctl start grub-pilot-backend"
echo -e "  ${BOLD}Notfall:  ${RESET} sudo /root/grub-pilot-emergency-backup-*/restore-emergency.sh"

# ── Kurzfassung schreiben ─────────────────────────────────────────────────────
{
echo "Grub Pilot v2.0.1 – Analyse-Kurzfassung"
echo "$(date '+%d.%m.%Y %H:%M:%S')  |  $(hostname)  |  $(whoami)"
echo "================================================================"
echo "Distribution: ${OS_NAME}"
echo "ERGEBNIS: ${PASSED} OK / ${ERRORS} Fehler / ${WARNINGS} Warnungen"
echo ""
[[ ${ERRORS}   -gt 0 ]] && { echo "KRITISCHE FEHLER:"; for e in "${ERROR_LIST[@]}"; do echo "  • $e"; done; echo ""; }
[[ ${WARNINGS} -gt 0 ]] && { echo "WARNUNGEN:";        for w in "${WARN_LIST[@]}"; do echo "  • $w"; done; echo ""; }
echo "PYTHON-DATEIEN:"
for fn in grub_pilot_backend.py grub_pilot_service.py grub_pilot_gui.py \
          grub_pilot_grub_utils.py grub_pilot_backup.py grub_pilot_sidebar.py; do
    fp="${INSTALL_DIR}/${fn}"
    [[ -f "${fp}" ]] \
        && echo "  ${fn}: $(wc -l < "${fp}") Zeilen, MD5=$(md5sum "${fp}" | cut -c1-12)" \
        || echo "  ${fn}: FEHLT"
done
echo ""
echo "SYSTEMDIENST:"
echo "  Status:   $(systemctl is-active  grub-pilot-backend.service 2>/dev/null || echo 'unbekannt')"
echo "  Enabled:  $(systemctl is-enabled grub-pilot-backend.service 2>/dev/null || echo 'unbekannt')"
echo ""
echo "GRUB:"
echo "  /etc/default/grub: $([[ -f "${GRUB_DEFAULTS}" ]] && echo "vorhanden" || echo "FEHLT")"
FOUND_CFG=""
for p in "${GRUB_CFG}" "${GRUB_CFG2}"; do [[ -f "${p}" ]] && FOUND_CFG="${p}" && break; done
echo "  grub.cfg: ${FOUND_CFG:-nicht gefunden}"
echo "  UEFI: $([[ -d /sys/firmware/efi ]] && echo "ja" || echo "nein")"
echo ""
echo "LOGS:"
echo "  Analyse-Log: ${LOG_FILE}"
echo "  Kurzfassung: ${SHORT_FILE}"
echo ""
echo "SYSTEM: Python=$(python3 --version 2>&1) | OS=$(. /etc/os-release 2>/dev/null && echo "${PRETTY_NAME:-${NAME}}" || uname -r)"
} > "${SHORT_FILE}"

chown "${LOG_USER}:${LOG_USER}" "${LOG_FILE}" "${SHORT_FILE}" 2>/dev/null || true

echo ""
echo -e "  ${CYAN}📄 Vollständiges Log:  ${LOG_FILE}${RESET}"
echo -e "  ${CYAN}📄 Kurzfassung:        ${SHORT_FILE}${RESET}"
echo ""
