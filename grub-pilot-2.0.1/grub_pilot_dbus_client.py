#!/usr/bin/env python3
"""Grub Pilot - D-Bus Client"""
import dbus, json, logging

LOG = logging.getLogger(__name__)
IFACE = 'org.grubpilot.backend'


class DBusClient:
    def __init__(self):
        self._connected = False
        self.interface  = None
        self._connect()

    def _connect(self):
        try:
            bus          = dbus.SystemBus()
            proxy        = bus.get_object(IFACE, '/org/grubpilot/backend')
            self.interface = dbus.Interface(proxy, IFACE)
            self._connected = True
        except Exception as e:
            LOG.error(f"D-Bus-Verbindungsfehler: {e}")
            self._connected = False

    @property
    def connected(self) -> bool:
        return self._connected

    def call(self, method: str, *args):
        """Call a backend method. Returns parsed dict/list or error dict."""
        if not self._connected:
            return {'success': False, 'error': 'Backend nicht verbunden'}
        try:
            raw    = getattr(self.interface, method)(*args)
            result = json.loads(str(raw))
            return result
        except Exception as e:
            LOG.error(f"D-Bus call '{method}': {e}")
            return {'success': False, 'error': str(e)}
