#!/usr/bin/env python3
"""Grub Pilot - Backend Entry Point
CRITICAL FIX: DBusGMainLoop(set_as_default=True) must be the very first
D-Bus call — before any dbus.service.Object instantiation.
"""
# ── Step 1: initialise the GLib main loop integration ─────────────────────
import dbus.mainloop.glib
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)   # ← MUST be first

# ── Step 2: everything else ────────────────────────────────────────────────
import dbus
from gi.repository import GLib
import logging, os, sys

os.makedirs('/var/log/grub-pilot', exist_ok=True)
logging.basicConfig(
    filename='/var/log/grub-pilot/fehler.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
LOG = logging.getLogger(__name__)

# Ensure the install directory is on sys.path so sibling modules resolve
_INSTALL_DIR = '/opt/grub-pilot'
if _INSTALL_DIR not in sys.path:
    sys.path.insert(0, _INSTALL_DIR)

from grub_pilot_service import GrubPilotBackend   # noqa: E402


def main() -> None:
    try:
        bus     = dbus.SystemBus()
        backend = GrubPilotBackend(bus)          # noqa: F841
        loop    = GLib.MainLoop()
        LOG.info("Grub Pilot Backend gestartet – warte auf D-Bus-Anfragen")
        loop.run()
    except KeyboardInterrupt:
        LOG.info("Backend durch Benutzer beendet")
    except Exception as e:
        LOG.critical(f"Backend-Start fehlgeschlagen: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
