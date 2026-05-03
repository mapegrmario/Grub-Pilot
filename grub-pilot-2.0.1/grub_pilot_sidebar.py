#!/usr/bin/env python3
"""Grub Pilot - Sidebar Navigation"""
import customtkinter as ctk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t

NAV_MAIN = [
    ('home',     '🏠', 'nav_home'),
    ('entries',  '📋', 'nav_entries'),
    ('timeout',  '⏱️',  'nav_timeout'),
    ('kernel',   '⚙️',  'nav_kernel'),
    ('themes',   '🎨', 'nav_themes'),
    ('wallpaper','🖼️', 'nav_wallpaper'),
    ('display',  '🖥️',  'nav_display'),
    ('efi',      '🔒', 'nav_efi'),
    ('custom',   '📝', 'nav_custom'),
    ('backups',  '💾', 'nav_backups'),
    ('profiles', '📤', 'nav_profiles'),
]
NAV_BOTTOM = [
    ('logs',     '📄', 'nav_logs'),
    ('repair',   '🔧', 'nav_repair'),
    ('settings', '⚙️',  'nav_settings'),
    ('help',     '❓', 'nav_help'),
    ('about',    'ℹ️',  'nav_about'),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navigate, **kwargs):
        super().__init__(parent, width=230,
                         fg_color=COLORS['sidebar'],
                         corner_radius=0, **kwargs)
        self.grid_propagate(False)
        self.on_navigate = on_navigate
        self._active_btn = None
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._build()

    def _build(self):
        # Logo
        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=16, pady=(20, 6))
        ctk.CTkLabel(header, text='🛡️',
                     font=ctk.CTkFont(size=24)).pack(side='left')
        ctk.CTkLabel(header, text='  Grub Pilot',
                     font=ctk.CTkFont(size=16, weight='bold'),
                     text_color='#7eb3ff').pack(side='left')

        ctk.CTkFrame(self, fg_color='#2d3f55',
                     height=1).pack(fill='x', padx=12, pady=(4, 6))

        # Scrollbarer Bereich — OHNE scrollbar_button_color (nicht in ctk 5.2.2)
        sc = ctk.CTkScrollableFrame(self, fg_color='transparent')
        sc.pack(fill='both', expand=True, padx=0, pady=0)

        ctk.CTkLabel(sc, text=t('nav_section_main'),
                     font=ctk.CTkFont(size=10),
                     text_color='#607a99').pack(anchor='w', padx=14, pady=(6,2))

        for pid, icon, key in NAV_MAIN:
            self._btn(sc, pid, icon, key)

        ctk.CTkFrame(sc, fg_color='#2d3f55',
                     height=1).pack(fill='x', padx=12, pady=6)

        ctk.CTkLabel(sc, text=t('nav_section_tools'),
                     font=ctk.CTkFont(size=10),
                     text_color='#607a99').pack(anchor='w', padx=14, pady=(0,2))

        for pid, icon, key in NAV_BOTTOM:
            self._btn(sc, pid, icon, key)

        ctk.CTkFrame(sc, fg_color='transparent', height=10).pack()

    def _btn(self, parent, pid: str, icon: str, key: str):
        b = ctk.CTkButton(
            parent,
            text=f'{icon}  {t(key)}',
            anchor='w', height=38, corner_radius=8,
            fg_color='transparent',
            hover_color=COLORS['button_active'],
            text_color=COLORS['text_sidebar'],
            font=ctk.CTkFont(size=13),
            command=lambda p=pid: self._click(p),
        )
        b.pack(fill='x', padx=8, pady=1)
        self._buttons[pid] = b

    def _click(self, pid: str):
        self._set_visual(pid)
        self.on_navigate(pid)

    def set_active(self, pid: str):
        self._set_visual(pid)

    def _set_visual(self, pid: str):
        if self._active_btn:
            self._active_btn.configure(
                fg_color='transparent',
                text_color=COLORS['text_sidebar'],
                font=ctk.CTkFont(size=13),
            )
        b = self._buttons.get(pid)
        if b:
            b.configure(
                fg_color=COLORS['btn_active_bg'],
                text_color=COLORS['btn_active_fg'],
                font=ctk.CTkFont(size=13, weight='bold'),
            )
            self._active_btn = b

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        self._active_btn = None
        self._buttons.clear()
        self._build()
