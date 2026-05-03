#!/usr/bin/env python3
"""Grub Pilot - Home Page (Win11 Stil)"""
import customtkinter as ctk
from grub_pilot_colors import COLORS, APP_VERSION
from grub_pilot_lang   import t


class HomePage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus = dbus_client
        self._build()

    def _build(self):
        # ── Seitentitel ───────────────────────────────────────────────────
        title_row = ctk.CTkFrame(self, fg_color='transparent')
        title_row.pack(anchor='w', pady=(0, 24))
        ctk.CTkLabel(title_row, text='🛡️',
                     font=ctk.CTkFont(size=28)).pack(side='left')
        ctk.CTkLabel(title_row, text='  Grub Pilot',
                     font=ctk.CTkFont(size=26, weight='bold'),
                     text_color=COLORS['text']).pack(side='left')
        ctk.CTkLabel(title_row, text=f'  v{APP_VERSION}',
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS['text_dim']).pack(side='left',
                                                         pady=(6, 0))

        ctk.CTkLabel(self, text=t('home_subtitle'),
                     font=ctk.CTkFont(size=14),
                     text_color=COLORS['text_dim']).pack(anchor='w',
                                                          pady=(0, 24))

        # ── System-Info-Kacheln ───────────────────────────────────────────
        try:
            info = self.dbus.call('get_system_info')
            tiles = [
                ('UEFI', '🔒', info.get('is_uefi', False)),
                ('Secure Boot', '🛡', info.get('is_secure_boot', False)),
                ('BLS Boot', '📂', info.get('uses_bls', False)),
            ]
            grub_ver = str(info.get('grub_version', '?'))
            connected = True
        except Exception:
            tiles, grub_ver, connected = [], '?', False

        tile_row = ctk.CTkFrame(self, fg_color='transparent')
        tile_row.pack(anchor='w', pady=(0, 16))

        for label, icon, state in tiles:
            self._tile(tile_row, icon, label,
                       '✅ Aktiv' if state else '❌ Inaktiv',
                       COLORS['success'] if state else COLORS['text_dim'])

        # GRUB-Version Kachel
        self._tile(tile_row, '⚙️', 'GRUB', grub_ver, COLORS['accent'])

        # ── Status-Banner ─────────────────────────────────────────────────
        if not connected:
            banner = ctk.CTkFrame(self, fg_color='#fff3cd', corner_radius=10,
                                  border_width=1, border_color='#ffc107')
            banner.pack(fill='x', pady=8)
            ctk.CTkLabel(banner,
                         text=f'⚠️  {t("backend_offline")}   –   {t("restart_hint")}',
                         font=ctk.CTkFont(size=12),
                         text_color='#856404').pack(padx=16, pady=10)

    def _tile(self, parent, icon, title, value, value_color):
        card = ctk.CTkFrame(parent, fg_color=COLORS['card'],
                            corner_radius=12,
                            border_width=1, border_color=COLORS['border'],
                            width=155, height=100)
        card.pack(side='left', padx=6)
        card.pack_propagate(False)
        card.bind('<Enter>',
                  lambda _: card.configure(fg_color=COLORS['card_hover']))
        card.bind('<Leave>',
                  lambda _: card.configure(fg_color=COLORS['card']))

        ctk.CTkLabel(card, text=icon,
                     font=ctk.CTkFont(size=22)).pack(pady=(14, 2))
        ctk.CTkLabel(card, text=title,
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack()
        ctk.CTkLabel(card, text=value,
                     font=ctk.CTkFont(size=12, weight='bold'),
                     text_color=value_color).pack(pady=(2, 0))

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
