#!/usr/bin/env python3
"""Grub Pilot - Theme Installer
Extrahiert .tar.xz Archive und installiert GRUB-Themes nach /boot/grub/themes/.
Unterstützt:
  - theme.tar.xz (enthält theme.txt direkt)
  - theme.tar.xz (enthält Ordner mit theme.txt)
  - theme.tar.xz (enthält mehrere Themes)
"""
import tarfile, os, shutil, tempfile, logging

LOG = logging.getLogger(__name__)

THEME_DIRS = [
    '/boot/grub/themes',
    '/boot/grub2/themes',
    '/usr/share/grub/themes',
]


def get_install_dir() -> str:
    """Gibt das erste vorhandene Theme-Verzeichnis zurück."""
    for d in THEME_DIRS:
        parent = os.path.dirname(d)
        if os.path.isdir(parent):
            os.makedirs(d, exist_ok=True)
            return d
    # Fallback
    os.makedirs(THEME_DIRS[0], exist_ok=True)
    return THEME_DIRS[0]


def find_theme_roots(extract_dir: str) -> list[str]:
    """
    Sucht alle Verzeichnisse die eine theme.txt enthalten.
    Gibt Liste absoluter Pfade zurück.
    """
    roots = []
    for root, _dirs, files in os.walk(extract_dir):
        if 'theme.txt' in files:
            roots.append(root)
    return roots


def install_theme_archive(archive_path: str) -> dict:
    """
    Installiert ein GRUB-Theme aus einem .tar.xz-Archiv.

    Rückgabe:
        {'success': True,  'installed': ['name1', ...], 'target': '/boot/grub/themes'}
        {'success': False, 'error': 'Fehlermeldung'}
    """
    if not os.path.isfile(archive_path):
        return {'success': False, 'error': f'Datei nicht gefunden: {archive_path}'}

    if not tarfile.is_tarfile(archive_path):
        return {'success': False, 'error': 'Keine gültige tar-Datei'}

    target_base = get_install_dir()
    installed   = []
    tmpdir      = None

    try:
        tmpdir = tempfile.mkdtemp(prefix='grub-pilot-theme-')
        LOG.info(f"Extrahiere {archive_path} → {tmpdir}")

        # Sicherheits-Check: keine absoluten Pfade / Path-Traversal
        with tarfile.open(archive_path, 'r:xz') as tf:
            for member in tf.getmembers():
                if member.name.startswith('/') or '..' in member.name:
                    return {'success': False,
                            'error': f'Unsicherer Pfad im Archiv: {member.name}'}
            tf.extractall(tmpdir)

        theme_roots = find_theme_roots(tmpdir)

        if not theme_roots:
            return {'success': False,
                    'error': 'Kein GRUB-Theme gefunden (keine theme.txt im Archiv)'}

        for theme_path in theme_roots:
            theme_name = os.path.basename(theme_path)
            if not theme_name:
                theme_name = os.path.basename(os.path.dirname(theme_path))
            if not theme_name or theme_name == '.':
                theme_name = os.path.splitext(
                    os.path.splitext(os.path.basename(archive_path))[0])[0]

            dest = os.path.join(target_base, theme_name)

            # Altes Theme sichern falls vorhanden
            if os.path.exists(dest):
                bak = dest + '.grub-pilot-bak'
                if os.path.exists(bak):
                    shutil.rmtree(bak, ignore_errors=True)
                shutil.copytree(dest, bak)
                shutil.rmtree(dest)
                LOG.info(f"Backup des alten Themes: {bak}")

            shutil.copytree(theme_path, dest)
            # Berechtigungen setzen
            for r, dirs, files in os.walk(dest):
                os.chmod(r, 0o755)
                for f in files:
                    os.chmod(os.path.join(r, f), 0o644)

            installed.append(theme_name)
            LOG.info(f"Theme installiert: {dest}")

        return {
            'success':   True,
            'installed': installed,
            'target':    target_base,
        }

    except tarfile.TarError as e:
        LOG.error(f"tar-Fehler: {e}")
        return {'success': False, 'error': f'Archiv-Fehler: {e}'}
    except Exception as e:
        LOG.error(f"install_theme_archive: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}
    finally:
        if tmpdir and os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)


def list_installed_themes() -> list[dict]:
    """Listet alle installierten GRUB-Themes (haben theme.txt)."""
    themes = []
    for base in THEME_DIRS:
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            tp = os.path.join(base, name)
            if os.path.isdir(tp) and os.path.isfile(os.path.join(tp, 'theme.txt')):
                themes.append({'name': name, 'path': tp})
    return themes
