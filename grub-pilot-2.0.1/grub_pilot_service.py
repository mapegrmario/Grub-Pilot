#!/usr/bin/env python3
"""Grub Pilot - D-Bus Service Object"""
import dbus, dbus.service
import subprocess, json, os, shutil, tempfile, logging, re

from grub_pilot_backup          import create_backup, list_backups, restore_backup
from grub_pilot_grub_utils      import (read_grub_defaults, safe_write_grub,
                                        run_grub_update, detect_grub_set_default_cmd)
from grub_pilot_theme_installer import install_theme_archive, list_installed_themes

LOG   = logging.getLogger(__name__)
IFACE = 'org.grubpilot.backend'


class GrubPilotBackend(dbus.service.Object):
    def __init__(self, bus):
        bus_name = dbus.service.BusName(IFACE, bus=bus)
        super().__init__(bus_name, '/org/grubpilot/backend')
        self.system_info = {
            'is_uefi':        os.path.exists('/sys/firmware/efi'),
            'is_secure_boot': self._check_secure_boot(),
            'uses_bls':       os.path.isdir('/boot/loader/entries'),
            'grub_version':   self._get_grub_version(),
        }
        LOG.info("GrubPilotBackend bereit")

    # ── private helpers ────────────────────────────────────────────────────

    def _check_secure_boot(self) -> bool:
        try:
            r = subprocess.run(['mokutil', '--sb-state'],
                               capture_output=True, text=True, timeout=5)
            return 'SecureBoot enabled' in r.stdout
        except Exception:
            return False

    def _get_grub_version(self) -> str:
        for cmd in [['grub-install', '--version'], ['grub2-install', '--version']]:
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                m = re.search(r'(\d+\.\d+)', r.stdout)
                if m:
                    return m.group(1)
            except Exception:
                continue
        return 'unknown'

    def _ok(self, msg='OK') -> str:
        return json.dumps({'success': True,  'message': msg})

    def _err(self, msg: str) -> str:
        return json.dumps({'success': False, 'error':   str(msg)})

    # ── D-Bus methods ──────────────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def get_system_info(self) -> str:
        return json.dumps(self.system_info)

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def list_boot_entries(self) -> str:
        entries = []
        try:
            if self.system_info['uses_bls']:
                edir = '/boot/loader/entries'
                for ef in sorted(os.listdir(edir)):
                    if not ef.endswith('.conf'):
                        continue
                    ei = {'file': ef}
                    with open(os.path.join(edir, ef)) as f:
                        for line in f:
                            if line.startswith('title '):
                                ei['title'] = line.split('title ', 1)[1].strip()
                            elif line.startswith('options '):
                                ei['options'] = line.split('options ', 1)[1].strip()
                    if 'title' in ei:
                        entries.append(ei)
            else:
                gcfg = '/boot/grub/grub.cfg'
                if os.path.exists(gcfg):
                    with open(gcfg) as f:
                        for line in f:
                            m = re.search(r"menuentry\s+'([^']*)'", line)
                            if m:
                                entries.append({'title': m.group(1), 'type': 'classic'})
        except Exception as e:
            LOG.error(f"list_boot_entries: {e}")
        return json.dumps(entries)

    @dbus.service.method(IFACE, in_signature='ss', out_signature='s')
    def set_default_entry(self, entry_id: str, method: str = 'id') -> str:
        try:
            create_backup(f'Standard → {entry_id}', self.system_info)
            if self.system_info['uses_bls']:
                cmd = detect_grub_set_default_cmd(entry_id)
                if cmd:
                    subprocess.run(cmd, capture_output=True, text=True, check=True)
            else:
                config, _ = read_grub_defaults()
                config['GRUB_DEFAULT'] = f'"{entry_id}"'
                if not safe_write_grub(config):
                    return self._err('Schreibfehler in /etc/default/grub')
                run_grub_update()
            return self._ok(f'Standard-Eintrag gesetzt: {entry_id}')
        except Exception as e:
            LOG.error(f"set_default_entry: {e}")
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def set_timeout(self, timeout: str) -> str:
        try:
            t = int(timeout)
            if t < -1:
                return self._err('Timeout muss >= -1 sein')
            create_backup(f'Timeout → {t}s', self.system_info)
            config, _ = read_grub_defaults()
            config['GRUB_TIMEOUT'] = str(t)
            if not safe_write_grub(config):
                return self._err('Schreibfehler in /etc/default/grub')
            if not self.system_info['uses_bls']:
                run_grub_update()
            return self._ok(f'Timeout auf {t}s gesetzt')
        except Exception as e:
            LOG.error(f"set_timeout: {e}")
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='ss', out_signature='s')
    def modify_kernel_params(self, entry_id: str, params: str) -> str:
        try:
            create_backup(f'Kernel-Parameter {entry_id}', self.system_info)
            if self.system_info['uses_bls']:
                edir = '/boot/loader/entries'
                for ef in os.listdir(edir):
                    if entry_id not in ef:
                        continue
                    ep  = os.path.join(edir, ef)
                    tmp = tempfile.NamedTemporaryFile(
                        mode='w', delete=False, dir=edir, suffix='.grub-pilot-tmp')
                    try:
                        with open(ep) as f:
                            for line in f:
                                tmp.write(f'options {params}\n'
                                          if line.startswith('options') else line)
                        tmp.close()
                        shutil.move(tmp.name, ep)
                    except Exception:
                        tmp.close()
                        if os.path.exists(tmp.name):
                            os.unlink(tmp.name)
                        raise
                    break
            else:
                config, _ = read_grub_defaults()
                config['GRUB_CMDLINE_LINUX_DEFAULT'] = f'"{params}"'
                if not safe_write_grub(config):
                    return self._err('Schreibfehler in /etc/default/grub')
                run_grub_update()
            return self._ok('Kernel-Parameter aktualisiert')
        except Exception as e:
            LOG.error(f"modify_kernel_params: {e}")
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def list_themes(self) -> str:
        try:
            return json.dumps(list_installed_themes())
        except Exception as e:
            LOG.error(f"list_themes: {e}")
            return json.dumps([])

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def set_theme(self, theme_name: str) -> str:
        try:
            # Theme-Pfad in allen bekannten Verzeichnissen suchen
            theme_path = None
            for base in ['/boot/grub/themes', '/boot/grub2/themes',
                         '/usr/share/grub/themes']:
                tp = os.path.join(base, theme_name, 'theme.txt')
                if os.path.isfile(tp):
                    theme_path = tp
                    break
            if not theme_path:
                return self._err(f'Theme nicht gefunden: {theme_name}')

            create_backup(f'Theme → {theme_name}', self.system_info)
            config, _ = read_grub_defaults()
            config['GRUB_THEME'] = f'"{theme_path}"'
            if not safe_write_grub(config):
                return self._err('Schreibfehler in /etc/default/grub')
            if not self.system_info['uses_bls']:
                run_grub_update()
            return self._ok(f'Theme aktiviert: {theme_name}')
        except Exception as e:
            LOG.error(f"set_theme: {e}")
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def install_theme_archive(self, archive_path: str) -> str:
        """Installiert ein GRUB-Theme aus einem .tar.xz-Archiv."""
        try:
            if not os.path.isfile(archive_path):
                return self._err(f'Datei nicht gefunden: {archive_path}')
            create_backup(f'Vor Theme-Installation: {os.path.basename(archive_path)}',
                          self.system_info)
            result = install_theme_archive(archive_path)
            if result['success']:
                names = ', '.join(result['installed'])
                LOG.info(f"Theme(s) installiert: {names} → {result['target']}")
                return json.dumps({
                    'success':   True,
                    'message':   f'Theme installiert: {names}',
                    'installed': result['installed'],
                    'target':    result['target'],
                })
            else:
                return self._err(result['error'])
        except Exception as e:
            LOG.error(f"install_theme_archive: {e}", exc_info=True)
            return self._err(str(e))

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def list_backups(self) -> str:
        try:
            return json.dumps(list_backups())
        except Exception as e:
            LOG.error(f"list_backups: {e}")
            return json.dumps([])

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def restore_backup(self, backup_id: str) -> str:
        try:
            count = restore_backup(backup_id)
            if not self.system_info['uses_bls']:
                run_grub_update()
            return self._ok(f'{count} Dateien wiederhergestellt')
        except Exception as e:
            LOG.error(f"restore_backup: {e}")
            return self._err(e)


    # ── Kernel-Parameter ───────────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def get_kernel_params(self) -> str:
        try:
            config, _ = read_grub_defaults()
            params = config.get('GRUB_CMDLINE_LINUX_DEFAULT', '"quiet splash"')
            return json.dumps({'success': True, 'params': params.strip('"')})
        except Exception as e:
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def set_kernel_params(self, params: str) -> str:
        try:
            create_backup(f'Kernel-Parameter: {params[:40]}', self.system_info)
            config, _ = read_grub_defaults()
            config['GRUB_CMDLINE_LINUX_DEFAULT'] = f'"{params}"'
            if not safe_write_grub(config):
                return self._err('Schreibfehler /etc/default/grub')
            run_grub_update()
            return self._ok(f'Kernel-Parameter gesetzt: {params}')
        except Exception as e:
            LOG.error(f"set_kernel_params: {e}")
            return self._err(e)

    # ── GRUB Reparatur ─────────────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def list_disks(self) -> str:
        import glob
        disks = sorted(
            glob.glob('/dev/sd[a-z]') +
            glob.glob('/dev/nvme[0-9]n[0-9]') +
            glob.glob('/dev/vd[a-z]')
        )
        return json.dumps(disks if disks else ['/dev/sda'])

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def grub_install(self, disk: str) -> str:
        import shutil as sh
        try:
            if not disk.startswith('/dev/'):
                return self._err('Ungültiges Laufwerk')
            create_backup(f'vor grub-install {disk}', self.system_info)
            cmd = 'grub-install' if sh.which('grub-install') else 'grub2-install'
            args = [cmd, '--recheck', disk]
            if self.system_info['is_uefi']:
                args += ['--target=x86_64-efi', '--efi-directory=/boot/efi',
                         '--bootloader-id=grub']
            r = subprocess.run(args, capture_output=True, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            if r.returncode != 0:
                return json.dumps({'success': False, 'error': out})
            return json.dumps({'success': True, 'output': out})
        except Exception as e:
            LOG.error(f"grub_install: {e}")
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def grub_update(self) -> str:
        try:
            from grub_pilot_grub_utils import detect_grub_update_cmd
            cmd = detect_grub_update_cmd()
            if not cmd:
                return self._err('Kein GRUB-Update-Befehl gefunden')
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            if r.returncode != 0:
                return json.dumps({'success': False, 'error': out})
            return json.dumps({'success': True, 'output': out})
        except Exception as e:
            LOG.error(f"grub_update: {e}")
            return self._err(e)

    # ── Hintergrundbild ────────────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def get_wallpaper(self) -> str:
        try:
            config, _ = read_grub_defaults()
            path = config.get('GRUB_BACKGROUND', '').strip('"')
            return json.dumps({'success': True, 'path': path})
        except Exception as e:
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def set_wallpaper(self, path: str) -> str:
        try:
            create_backup('Hintergrundbild', self.system_info)
            config, _ = read_grub_defaults()
            if path:
                if not os.path.isfile(path):
                    return self._err(f'Datei nicht gefunden: {path}')
                config['GRUB_BACKGROUND'] = f'"{path}"'
            else:
                config.pop('GRUB_BACKGROUND', None)
            if not safe_write_grub(config):
                return self._err('Schreibfehler')
            run_grub_update()
            return self._ok(f'Hintergrundbild: {path or "entfernt"}')
        except Exception as e:
            LOG.error(f"set_wallpaper: {e}")
            return self._err(e)

    # ── Anzeige-Einstellungen ──────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def get_display_settings(self) -> str:
        try:
            config, _ = read_grub_defaults()
            return json.dumps({
                'success':    True,
                'gfxmode':    config.get('GRUB_GFXMODE', 'auto').strip('"'),
                'gfxpayload': config.get('GRUB_GFXPAYLOAD_LINUX', 'keep').strip('"'),
                'osprober':   config.get('GRUB_DISABLE_OS_PROBER', 'false').strip('"') != 'true',
            })
        except Exception as e:
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='sss', out_signature='s')
    def set_display_settings(self, gfxmode: str, gfxpayload: str,
                             osprober: str) -> str:
        try:
            create_backup('Anzeige-Einstellungen', self.system_info)
            config, _ = read_grub_defaults()
            config['GRUB_GFXMODE']            = f'"{gfxmode}"'
            config['GRUB_GFXPAYLOAD_LINUX']   = f'"{gfxpayload}"'
            config['GRUB_DISABLE_OS_PROBER']  = '"true"' if osprober == '0' else '"false"'
            if not safe_write_grub(config):
                return self._err('Schreibfehler')
            run_grub_update()
            return self._ok('Anzeige-Einstellungen gespeichert')
        except Exception as e:
            LOG.error(f"set_display_settings: {e}")
            return self._err(e)

    # ── EFI Boot-Reihenfolge ───────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def list_efi_entries(self) -> str:
        try:
            r = subprocess.run(['efibootmgr'], capture_output=True,
                               text=True, timeout=10)
            entries = []
            boot_order = []
            for line in r.stdout.splitlines():
                if line.startswith('BootOrder:'):
                    boot_order = line.split(':')[1].strip().split(',')
                m = re.match(r'Boot([0-9A-Fa-f]{4})([*\s])\s+(.*)', line)
                if m:
                    bid, active, name = m.groups()
                    entries.append({
                        'id':     bid,
                        'name':   name.strip(),
                        'active': active == '*',
                    })
            if boot_order:
                order_map = {e: i for i, e in enumerate(boot_order)}
                entries.sort(key=lambda x: order_map.get(x['id'], 999))
            return json.dumps(entries)
        except Exception as e:
            LOG.error(f"list_efi_entries: {e}")
            return json.dumps([])

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def set_efi_order(self, order_csv: str) -> str:
        try:
            order = order_csv.replace(',', '')
            r = subprocess.run(['efibootmgr', '--bootorder', order_csv],
                               capture_output=True, text=True, timeout=10)
            if r.returncode != 0:
                return self._err(r.stderr.strip())
            return self._ok('EFI-Reihenfolge gespeichert')
        except Exception as e:
            LOG.error(f"set_efi_order: {e}")
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def delete_efi_entry(self, entry_id: str) -> str:
        try:
            r = subprocess.run(['efibootmgr', '--delete-bootnum',
                                '--bootnum', entry_id],
                               capture_output=True, text=True, timeout=10)
            if r.returncode != 0:
                return self._err(r.stderr.strip())
            return self._ok(f'EFI-Eintrag {entry_id} gelöscht')
        except Exception as e:
            LOG.error(f"delete_efi_entry: {e}")
            return self._err(e)

    # ── Eigene Einträge ────────────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def get_custom_entries(self) -> str:
        try:
            path = '/etc/grub.d/40_custom'
            content = open(path).read() if os.path.isfile(path) else ''
            return json.dumps({'success': True, 'content': content})
        except Exception as e:
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def set_custom_entries(self, content: str) -> str:
        try:
            path = '/etc/grub.d/40_custom'
            create_backup('40_custom Einträge', self.system_info)
            with open(path, 'w') as f:
                f.write(content)
            os.chmod(path, 0o755)
            run_grub_update()
            return self._ok('Einträge gespeichert und GRUB aktualisiert')
        except Exception as e:
            LOG.error(f"set_custom_entries: {e}")
            return self._err(e)

    # ── Config Export / Import ─────────────────────────────────────────────

    @dbus.service.method(IFACE, in_signature='', out_signature='s')
    def export_config(self) -> str:
        try:
            config, _ = read_grub_defaults()
            return json.dumps({
                'success':    True,
                'grub_defaults': dict(config),
                'system_info':   self.system_info,
                'exported_at':   __import__('datetime').datetime.now().isoformat(),
                'version':       '2.0.1',
            })
        except Exception as e:
            return self._err(e)

    @dbus.service.method(IFACE, in_signature='s', out_signature='s')
    def import_config(self, json_str: str) -> str:
        try:
            data = json.loads(json_str)
            if 'grub_defaults' not in data:
                return self._err('Ungültiges Profil-Format')
            create_backup('vor Config-Import', self.system_info)
            new_config = data['grub_defaults']
            if not safe_write_grub(new_config):
                return self._err('Schreibfehler beim Importieren')
            run_grub_update()
            return self._ok('Konfiguration importiert und GRUB aktualisiert')
        except Exception as e:
            LOG.error(f"import_config: {e}")
            return self._err(e)
