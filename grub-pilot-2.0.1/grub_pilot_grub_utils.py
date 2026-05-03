#!/usr/bin/env python3
"""Grub Pilot - Distro-agnostic GRUB Utilities
Fixes:
  - update-grub replaced by auto-detected distro command
  - grub-script-check removed (wrong tool for /etc/default/grub)
  - tmp.close() always called before os.unlink()
  - Return value properly propagated
"""
import subprocess, os, shutil, tempfile, logging

LOG = logging.getLogger(__name__)

# Candidate output paths for grub-mkconfig, in order of preference
_GRUB_CFG_CANDIDATES = [
    '/boot/grub/grub.cfg',
    '/boot/grub2/grub.cfg',
    '/boot/efi/EFI/fedora/grub.cfg',
    '/boot/efi/EFI/opensuse/grub.cfg',
]


def detect_grub_update_cmd() -> list[str] | None:
    """Return the correct grub-update command for the running distro."""
    # Ubuntu / Mint / Debian — wrapper script
    if shutil.which('update-grub'):
        return ['update-grub']
    # Determine output path for mkconfig variants
    out = '/boot/grub/grub.cfg'
    for p in _GRUB_CFG_CANDIDATES:
        if os.path.exists(os.path.dirname(p)):
            out = p
            break
    # Fedora / RHEL / openSUSE
    if shutil.which('grub2-mkconfig'):
        return ['grub2-mkconfig', '-o', out]
    # Arch / Gentoo / generic
    if shutil.which('grub-mkconfig'):
        return ['grub-mkconfig', '-o', out]
    LOG.warning("Kein GRUB-Update-Befehl gefunden")
    return None


def run_grub_update() -> bool:
    """Run the appropriate grub update command. Raises RuntimeError on failure."""
    cmd = detect_grub_update_cmd()
    if not cmd:
        raise RuntimeError("Kein GRUB-Update-Befehl verfügbar")
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        msg = res.stderr.strip()[:300]
        LOG.error(f"GRUB-Update fehlgeschlagen [{' '.join(cmd)}]: {msg}")
        raise RuntimeError(f"GRUB-Update fehlgeschlagen: {msg}")
    LOG.info(f"GRUB-Update erfolgreich: {' '.join(cmd)}")
    return True


def detect_grub_set_default_cmd(entry_id: str) -> list[str] | None:
    for cmd in ['grub2-set-default', 'grub-set-default']:
        if shutil.which(cmd):
            return [cmd, entry_id]
    return None


def read_grub_defaults(path: str = '/etc/default/grub') -> tuple[dict, list]:
    """Parse /etc/default/grub → (key_value_dict, comment_lines)."""
    config, header = {}, []
    if not os.path.exists(path):
        return config, header
    with open(path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                header.append(line)
            elif '=' in stripped:
                k, v = stripped.split('=', 1)
                config[k.strip()] = v.strip()
    return config, header


def safe_write_grub(config: dict, target: str = '/etc/default/grub') -> bool:
    """
    Write a GRUB config dict safely:
      1. Create temp file in same directory
      2. Validate basic sanity (must contain GRUB_ keys)
      3. Atomic move to target
    Does NOT call grub-script-check (wrong tool for /etc/default/grub).
    Returns True on success, False on any error.
    """
    if not config:
        LOG.error("safe_write_grub: leere Konfiguration")
        return False

    # Backup the original
    if os.path.exists(target):
        try:
            shutil.copy2(target, target + '.grub-pilot-bak')
        except Exception as e:
            LOG.warning(f"Konnte kein Backup anlegen: {e}")

    tmp_path = None
    try:
        tmp_dir = os.path.dirname(target)
        tmp = tempfile.NamedTemporaryFile(
            mode='w', delete=False, dir=tmp_dir, suffix='.grub-pilot-tmp'
        )
        tmp_path = tmp.name
        tmp.write('# /etc/default/grub – verwaltet von Grub Pilot\n')
        for key, val in sorted(config.items()):
            tmp.write(f'{key}={val}\n')
        tmp.close()   # ← CRITICAL: close before any further ops

        # Basic sanity: at least one GRUB_ key must exist
        with open(tmp_path) as f:
            content = f.read()
        if 'GRUB_' not in content:
            raise ValueError("Ungültige GRUB-Konfiguration generiert (keine GRUB_-Schlüssel)")

        shutil.move(tmp_path, target)
        LOG.info(f"GRUB-Konfiguration geschrieben: {target}")
        return True

    except Exception as e:
        LOG.error(f"safe_write_grub Fehler: {e}")
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        return False
