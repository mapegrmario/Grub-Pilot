#!/usr/bin/env python3
"""Grub Pilot - Main GUI mit Startup-Error-Catcher"""
import customtkinter as ctk
import os, logging, traceback, sys

LOG_PATH = os.path.expanduser('~/.local/share/grub-pilot/gui.log')
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
)
LOG = logging.getLogger(__name__)

ctk.set_appearance_mode('light')
ctk.set_default_color_theme('blue')

from grub_pilot_config_manager import get as cfg_get
from grub_pilot_lang           import set_lang
set_lang(cfg_get('grub-pilot', 'language', 'de'))

from grub_pilot_colors             import COLORS
from grub_pilot_lang               import t
from grub_pilot_dbus_client        import DBusClient
from grub_pilot_toast              import ToastManager
from grub_pilot_sidebar            import Sidebar
from grub_pilot_page_home          import HomePage
from grub_pilot_page_entries       import EntriesPage
from grub_pilot_page_timeout       import TimeoutPage
from grub_pilot_page_kernel        import KernelPage
from grub_pilot_page_themes        import ThemesPage
from grub_pilot_page_wallpaper     import WallpaperPage
from grub_pilot_page_display       import DisplayPage
from grub_pilot_page_efi           import EfiPage
from grub_pilot_page_custom        import CustomEntriesPage
from grub_pilot_page_backups       import BackupsPage
from grub_pilot_page_profiles      import ProfilesPage
from grub_pilot_page_logs          import LogsPage
from grub_pilot_page_repair        import RepairPage
from grub_pilot_page_settings      import SettingsPage
from grub_pilot_page_help          import HelpPage
from grub_pilot_page_about         import AboutPage


class GrubPilotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.dbus  = DBusClient()
        self.toast = ToastManager(self)
        self._setup_window()
        self._build_layout()
        self._navigate('home')

    def _setup_window(self):
        self.title(t('app_title'))
        self.geometry('1200x780')
        self.minsize(980, 620)
        self.configure(fg_color=COLORS['bg'])
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'+{(sw-1200)//2}+{(sh-780)//2}')

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, on_navigate=self._navigate)
        self.sidebar.grid(row=0, column=0, sticky='nsew')

        ctk.CTkFrame(self, fg_color=COLORS['border'],
                     width=1, corner_radius=0).grid(row=0, column=0,
                     sticky='nse')

        self._host = ctk.CTkFrame(self, fg_color=COLORS['bg'],
                                  corner_radius=0)
        self._host.grid(row=0, column=1, sticky='nsew')
        self._host.grid_columnconfigure(0, weight=1)
        self._host.grid_rowconfigure(0, weight=1)
        self._page = None

    def _navigate(self, pid: str):
        if self._page:
            if hasattr(self._page, '_running'):
                self._page._running = False
            self._page.destroy()
        try:
            p = self._make_page(pid)
        except Exception as e:
            LOG.error(f"Fehler beim Laden der Seite '{pid}': {e}\n{traceback.format_exc()}")
            p = self._error_page(pid, str(e))
        p.grid(row=0, column=0, sticky='nsew', padx=28, pady=24)
        self._page = p
        self._pid  = pid
        self.sidebar.set_active(pid)

    def _make_page(self, pid: str):
        h = self._host
        match pid:
            case 'home':      return HomePage(h, self.dbus)
            case 'entries':   return EntriesPage(h, self.dbus, self.toast)
            case 'timeout':   return TimeoutPage(h, self.dbus, self.toast)
            case 'kernel':    return KernelPage(h, self.dbus, self.toast)
            case 'themes':    return ThemesPage(h, self.dbus, self.toast)
            case 'wallpaper': return WallpaperPage(h, self.dbus, self.toast)
            case 'display':   return DisplayPage(h, self.dbus, self.toast)
            case 'efi':       return EfiPage(h, self.dbus, self.toast)
            case 'custom':    return CustomEntriesPage(h, self.dbus, self.toast)
            case 'backups':   return BackupsPage(h, self.dbus, self.toast)
            case 'profiles':  return ProfilesPage(h, self.dbus, self.toast)
            case 'logs':      return LogsPage(h, self.dbus, self.toast)
            case 'repair':    return RepairPage(h, self.dbus, self.toast)
            case 'settings':  return SettingsPage(h, self.toast,
                                  on_lang_change=self._rebuild_ui)
            case 'help':      return HelpPage(h)
            case 'about':     return AboutPage(h)
            case _:           return HomePage(h, self.dbus)

    def _error_page(self, pid: str, error: str) -> ctk.CTkFrame:
        """Zeigt eine Fehlerseite statt zu crashen."""
        frame = ctk.CTkFrame(self._host, fg_color='transparent')
        ctk.CTkLabel(frame, text='⚠️',
                     font=ctk.CTkFont(size=52)).pack(pady=(40, 8))
        ctk.CTkLabel(frame,
                     text=f'Fehler beim Laden: {pid}',
                     font=ctk.CTkFont(size=16, weight='bold'),
                     text_color=COLORS['error']).pack()
        box = ctk.CTkTextbox(frame, height=160,
                             font=ctk.CTkFont(family='monospace', size=11),
                             fg_color=COLORS['card'],
                             text_color=COLORS['error'])
        box.pack(fill='x', padx=20, pady=12)
        box.insert('1.0', error)
        box.configure(state='disabled')
        ctk.CTkLabel(frame,
                     text=f'Details: {LOG_PATH}',
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack()
        return frame

    def _rebuild_ui(self):
        self.title(t('app_title'))
        self.sidebar.rebuild()
        self._navigate(getattr(self, '_pid', 'settings'))


def main():
    try:
        app = GrubPilotApp()
        app.mainloop()
    except Exception as e:
        LOG.critical(f"Kritischer Startfehler: {e}\n{traceback.format_exc()}")
        # Fallback: Fehler in Terminal ausgeben
        print(f"\n❌ Grub Pilot Startfehler:\n{e}", file=sys.stderr)
        print(f"Details: {LOG_PATH}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
