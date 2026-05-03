#!/usr/bin/env python3
"""Grub Pilot - Backup / Restore Logic"""
import os, shutil, json, logging
from datetime import datetime

LOG = logging.getLogger(__name__)

BACKUP_DIR   = '/var/backups/grub-pilot'
GRUB_FILES   = ['/etc/default/grub', '/boot/grub/grub.cfg', '/boot/grub2/grub.cfg']
GRUB_DIRS    = ['/etc/grub.d', '/boot/loader/entries']


def create_backup(description: str = '', system_info: dict = None) -> str:
    ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
    bdir = os.path.join(BACKUP_DIR, f'backup_{ts}')
    os.makedirs(bdir, exist_ok=True)
    backed = []

    for fp in GRUB_FILES:
        if os.path.isfile(fp):
            dest = os.path.join(bdir, fp.lstrip('/'))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(fp, dest)
            backed.append(fp)

    for dp in GRUB_DIRS:
        if os.path.isdir(dp):
            dest = os.path.join(bdir, dp.lstrip('/'))
            shutil.copytree(dp, dest, dirs_exist_ok=True)
            backed.append(dp)

    manifest = {
        'timestamp':   ts,
        'description': description,
        'files':       backed,
        'system_info': system_info or {},
    }
    with open(os.path.join(bdir, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    LOG.info(f"Backup erstellt: {bdir} ({len(backed)} Pfade)")
    return bdir


def list_backups() -> list[dict]:
    if not os.path.isdir(BACKUP_DIR):
        return []
    result = []
    for entry in sorted(os.listdir(BACKUP_DIR), reverse=True):
        ep = os.path.join(BACKUP_DIR, entry)
        if not (os.path.isdir(ep) and entry.startswith('backup_')):
            continue
        m = {}
        mpath = os.path.join(ep, 'manifest.json')
        if os.path.exists(mpath):
            try:
                with open(mpath) as f:
                    m = json.load(f)
            except Exception:
                pass
        result.append({
            'id':          entry,
            'path':        ep,
            'timestamp':   m.get('timestamp', ''),
            'description': m.get('description', ''),
        })
    return result


def restore_backup(backup_id: str) -> int:
    bp = os.path.join(BACKUP_DIR, backup_id)
    if not os.path.isdir(bp):
        raise FileNotFoundError(f"Backup nicht gefunden: {backup_id}")
    count = 0
    for root, _dirs, files in os.walk(bp):
        for file in files:
            if file == 'manifest.json':
                continue
            src = os.path.join(root, file)
            rel = os.path.relpath(src, bp)
            dst = os.path.join('/', rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            count += 1
    LOG.info(f"Backup wiederhergestellt: {backup_id} ({count} Dateien)")
    return count
