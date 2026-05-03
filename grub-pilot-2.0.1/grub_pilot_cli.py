#!/usr/bin/env python3
"""Grub Pilot - Command Line Interface"""
import argparse, dbus, json, sys, os, logging

os.makedirs('/var/log/grub-pilot', exist_ok=True)
logging.basicConfig(
    filename='/var/log/grub-pilot/fehler.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
LOG = logging.getLogger(__name__)

IFACE = 'org.grubpilot.backend'


class CLI:
    def __init__(self):
        try:
            self.bus   = dbus.SystemBus()
            proxy      = self.bus.get_object(IFACE, '/org/grubpilot/backend')
            self.iface = dbus.Interface(proxy, IFACE)
        except Exception as e:
            print(f'❌ Backend nicht erreichbar: {e}', file=sys.stderr)
            print('   Starten mit: sudo systemctl start grub-pilot-backend',
                  file=sys.stderr)
            sys.exit(1)

    def call(self, method: str, *args):
        try:
            return json.loads(str(getattr(self.iface, method)(*args)))
        except Exception as e:
            return {'success': False, 'error': str(e)}


def build_parser() -> argparse.ArgumentParser:
    p   = argparse.ArgumentParser(
        prog='grub-pilot',
        description='Grub Pilot – Sicheres GRUB-Konfigurationswerkzeug',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Autor: Mario Peeß / Großenhain  |  mapegr@mailbox.org',
    )
    sub = p.add_subparsers(dest='cmd', required=True)

    sub.add_parser('status',  help='Systeminformationen anzeigen')
    sub.add_parser('list',    help='Boot-Einträge auflisten')
    sub.add_parser('backups', help='Backup-Liste anzeigen')
    sub.add_parser('rescue',  help='Notfall-Info anzeigen')

    sp = sub.add_parser('set-default', help='Standard-Boot-Eintrag setzen')
    sp.add_argument('entry', help='Eintrags-ID oder Titel')

    sp = sub.add_parser('set-timeout', help='Boot-Timeout setzen (-1 / 0–30)')
    sp.add_argument('timeout', type=int, help='Sekunden')

    sp = sub.add_parser('restore', help='Backup wiederherstellen')
    sp.add_argument('id', help='Backup-ID (backup_YYYYMMDD_HHMMSS)')

    return p


def main() -> None:
    args = build_parser().parse_args()
    cli  = CLI()

    if args.cmd == 'status':
        r = cli.call('get_system_info')
        if isinstance(r, dict):
            print(json.dumps(r, indent=2, ensure_ascii=False))
        else:
            print(r)

    elif args.cmd == 'list':
        entries = cli.call('list_boot_entries')
        if not isinstance(entries, list):
            print('Keine Einträge gefunden')
            return
        for i, e in enumerate(entries):
            print(f'  [{i}] {e.get("title", "?")}')

    elif args.cmd == 'backups':
        backups = cli.call('list_backups')
        if not isinstance(backups, list) or not backups:
            print('Keine Backups vorhanden')
            return
        for b in backups:
            print(f"  {b['id']}  {b.get('description', '')}")

    elif args.cmd == 'set-default':
        r = cli.call('set_default_entry', args.entry, 'id')
        _print_result(r)

    elif args.cmd == 'set-timeout':
        r = cli.call('set_timeout', str(args.timeout))
        _print_result(r)

    elif args.cmd == 'restore':
        r = cli.call('restore_backup', args.id)
        _print_result(r)

    elif args.cmd == 'rescue':
        print('🚑 Notfall-Wiederherstellung:')
        print('   sudo /root/grub-pilot-emergency-backup-*/restore-emergency.sh')
        print('   Backups: /var/backups/grub-pilot/')
        print('   Logs:    /var/log/grub-pilot/fehler.log')


def _print_result(r):
    if isinstance(r, dict):
        if r.get('success'):
            print(f"✅ {r.get('message', 'OK')}")
        else:
            print(f"❌ Fehler: {r.get('error', '?')}", file=sys.stderr)
            sys.exit(1)
    else:
        print(r)


if __name__ == '__main__':
    main()
