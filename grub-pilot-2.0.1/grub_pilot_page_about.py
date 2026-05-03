#!/usr/bin/env python3
"""Grub Pilot - About Page (Win11 Stil)"""
import customtkinter as ctk
from grub_pilot_colors import COLORS, APP_VERSION
from grub_pilot_lang   import t


class AboutPage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('about_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0, 20))

        sc = ctk.CTkScrollableFrame(self, fg_color='transparent',
                                    border_width=0)
        sc.pack(expand=True, fill='both')

        # ── App-Info ──────────────────────────────────────────────────────
        top = ctk.CTkFrame(sc, fg_color=COLORS['card'], corner_radius=12,
                           border_width=1, border_color=COLORS['border'])
        top.pack(fill='x', pady=(0, 10))

        left = ctk.CTkFrame(top, fg_color='transparent')
        left.pack(side='left', padx=22, pady=18)
        ctk.CTkLabel(left, text='🛡️', font=ctk.CTkFont(size=52)).pack()

        right = ctk.CTkFrame(top, fg_color='transparent')
        right.pack(side='left', padx=10, pady=18, fill='x', expand=True)
        ctk.CTkLabel(right, text='Grub Pilot',
                     font=ctk.CTkFont(size=20, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w')
        ctk.CTkLabel(right, text=f'Version {APP_VERSION}',
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS['text_dim']).pack(anchor='w')
        ctk.CTkLabel(right, text=t('home_subtitle'),
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS['text_dim']).pack(anchor='w', pady=(4,0))

        # ── Info-Zeilen ───────────────────────────────────────────────────
        info = ctk.CTkFrame(sc, fg_color=COLORS['card'], corner_radius=12,
                            border_width=1, border_color=COLORS['border'])
        info.pack(fill='x', pady=(0, 10))

        for i, (label, value) in enumerate([
            (t('about_author'),  'Mario Peeß'),
            (t('about_location'),'Großenhain, Deutschland'),
            (t('about_email'),   'mapegr@mailbox.org'),
            (t('about_license'), 'GPLv3'),
        ]):
            row = ctk.CTkFrame(info, fg_color='transparent')
            row.pack(fill='x', padx=20, pady=0)
            if i > 0:
                ctk.CTkFrame(info, fg_color=COLORS['border_light'],
                             height=1).pack(fill='x', padx=20)
            ctk.CTkLabel(row, text=label,
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS['text_dim'],
                         width=120, anchor='w').pack(side='left', pady=11)
            ctk.CTkLabel(row, text=value,
                         font=ctk.CTkFont(size=13, weight='bold'),
                         text_color=COLORS['text']).pack(side='left')

        # ── Haftungsausschluss ────────────────────────────────────────────
        disc = ctk.CTkFrame(sc, fg_color='#fff8f0', corner_radius=12,
                            border_width=1, border_color='#fcd9b6')
        disc.pack(fill='x', pady=(0, 10))
        ctk.CTkLabel(disc, text=t('about_disclaimer'),
                     font=ctk.CTkFont(size=12), text_color='#7c3a00',
                     wraplength=540, justify='left').pack(padx=20, pady=16)

        # ── Drittanbieter ─────────────────────────────────────────────────
        tp = ctk.CTkFrame(sc, fg_color=COLORS['card'], corner_radius=12,
                          border_width=1, border_color=COLORS['border'])
        tp.pack(fill='x', pady=(0, 16))
        ctk.CTkLabel(tp, text='📦  ' + ('Drittanbieter-Software'
                                         if t('about_license') == 'GPLv3'
                                         else 'Third-party software'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=20, pady=(16,4))
        ctk.CTkLabel(tp, text=t('about_thirdparty'),
                     font=ctk.CTkFont(family='monospace', size=11),
                     text_color=COLORS['text_dim'],
                     justify='left', wraplength=560,
                     ).pack(anchor='w', padx=20, pady=(0, 16))

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
