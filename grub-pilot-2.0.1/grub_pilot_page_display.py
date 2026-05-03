#!/usr/bin/env python3
"""Grub Pilot - Auflösung / Video-Modus"""
import customtkinter as ctk
import tkinter as tk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t

RESOLUTIONS = [
    'auto', '1920x1080', '1920x1080x32', '1920x1200',
    '2560x1440', '3840x2160',
    '1280x1024', '1280x1024x32',
    '1280x720',  '1024x768',  '1024x768x32',
    '800x600',   '640x480',
]
PAYLOAD_MODES = ['text', 'keep', 'auto']


class DisplayPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus         = dbus_client
        self.toast        = toast
        self._gfxmode_var = tk.StringVar(value='auto')
        self._payload_var = tk.StringVar(value='keep')
        self._osprober    = tk.BooleanVar(value=True)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('display_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0,16))

        self._load_current()

        # GRUB_GFXMODE
        card1 = self._card()
        ctk.CTkLabel(card1, text='GRUB_GFXMODE  —  ' + t('display_gfxmode'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=18, pady=(14,8))

        row1 = ctk.CTkFrame(card1, fg_color='transparent')
        row1.pack(fill='x', padx=18, pady=(0,14))
        ctk.CTkOptionMenu(row1, values=RESOLUTIONS,
                          variable=self._gfxmode_var,
                          font=ctk.CTkFont(size=13), height=38, width=220,
                          fg_color=COLORS['card'],
                          button_color=COLORS['accent'],
                          button_hover_color=COLORS['accent_hover'],
                          text_color=COLORS['text'],
                          ).pack(side='left')
        ctk.CTkLabel(row1, text=t('display_gfxmode_hint'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(side='left', padx=12)

        # GRUB_GFXPAYLOAD_LINUX
        card2 = self._card()
        ctk.CTkLabel(card2, text='GRUB_GFXPAYLOAD_LINUX  —  ' + t('display_payload'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=18, pady=(14,8))

        row2 = ctk.CTkFrame(card2, fg_color='transparent')
        row2.pack(fill='x', padx=18, pady=(0,4))
        for val, lbl in [('text', t('display_payload_text')),
                         ('keep', t('display_payload_keep')),
                         ('auto', t('display_payload_auto'))]:
            ctk.CTkRadioButton(row2, text=f'{val} — {lbl}',
                               variable=self._payload_var, value=val,
                               font=ctk.CTkFont(size=12),
                               text_color=COLORS['text'],
                               fg_color=COLORS['accent'],
                               ).pack(anchor='w', padx=6, pady=3)

        ctk.CTkLabel(card2, text=t('display_payload_hint'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(anchor='w', padx=18, pady=(4,14))

        # os-prober Toggle
        card3 = self._card()
        os_row = ctk.CTkFrame(card3, fg_color='transparent')
        os_row.pack(fill='x', padx=18, pady=14)
        info = ctk.CTkFrame(os_row, fg_color='transparent')
        info.pack(side='left', expand=True, fill='x')
        ctk.CTkLabel(info, text='GRUB_DISABLE_OS_PROBER  —  ' + t('display_osprober'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w')
        ctk.CTkLabel(info, text=t('display_osprober_hint'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(anchor='w', pady=(2,0))
        ctk.CTkSwitch(os_row, text=t('display_osprober_on'),
                      variable=self._osprober,
                      font=ctk.CTkFont(size=12),
                      progress_color=COLORS['accent'],
                      ).pack(side='right')

        # Speichern
        ctk.CTkButton(self, text=t('display_save'), height=42, width=200,
                      corner_radius=10,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._save).pack(anchor='w', pady=18)

    def _card(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                         border_width=1, border_color=COLORS['border'])
        f.pack(fill='x', pady=5)
        return f

    def _load_current(self):
        try:
            r = self.dbus.call('get_display_settings')
            self._gfxmode_var.set(r.get('gfxmode', 'auto'))
            self._payload_var.set(r.get('gfxpayload', 'keep'))
            self._osprober.set(r.get('osprober', True))
        except Exception:
            pass

    def _save(self):
        r = self.dbus.call('set_display_settings',
                           self._gfxmode_var.get(),
                           self._payload_var.get(),
                           '1' if self._osprober.get() else '0')
        if r.get('success'):
            self.toast.success(t('display_saved'))
        else:
            self.toast.error(r.get('error', '?'))

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
