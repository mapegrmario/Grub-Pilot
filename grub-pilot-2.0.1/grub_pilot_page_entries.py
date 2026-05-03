#!/usr/bin/env python3
"""Grub Pilot - Boot Entries Page"""
import customtkinter as ctk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class EntriesPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus  = dbus_client
        self.toast = toast
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('entries_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0, 14))

        entries = self.dbus.call('list_boot_entries')
        if isinstance(entries, dict) or not entries:
            self._empty_state(); return

        sc = ctk.CTkScrollableFrame(self, fg_color='transparent')
        sc.pack(expand=True, fill='both')
        for e in entries:
            self._entry_card(sc, e)

    def _empty_state(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=16,
                         border_width=1, border_color=COLORS['border'])
        f.pack(expand=True, fill='both', padx=4)
        ctk.CTkLabel(f, text='📋', font=ctk.CTkFont(size=48)).pack(pady=(40,8))
        ctk.CTkLabel(f, text=t('entries_empty'), font=ctk.CTkFont(size=14),
                     text_color=COLORS['text_dim']).pack()

    def _entry_card(self, parent, entry: dict):
        card = ctk.CTkFrame(parent, fg_color=COLORS['card'], corner_radius=12,
                            border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=5, padx=2)
        card.bind('<Enter>', lambda _: card.configure(fg_color=COLORS['card_hover']))
        card.bind('<Leave>', lambda _: card.configure(fg_color=COLORS['card']))

        ctk.CTkLabel(card, text=entry.get('title', 'Unbekannt'),
                     font=ctk.CTkFont(size=14, weight='bold'),
                     text_color=COLORS['text']).pack(side='left', padx=18, pady=14)

        ctk.CTkButton(card, text=t('entries_set_def'), width=130, height=34,
                      corner_radius=8, fg_color=COLORS['accent'],
                      hover_color=COLORS['accent_hover'], text_color='#ffffff',
                      command=lambda e=entry: self._set_default(e)
                      ).pack(side='right', padx=14, pady=10)

    def _set_default(self, entry):
        eid = entry.get('file', entry.get('title', ''))
        r = self.dbus.call('set_default_entry', eid, 'id')
        if r.get('success'):
            self.toast.success(t('toast_def_ok', title=entry.get('title', eid)))
        else:
            self.toast.error(t('toast_def_err', error=r.get('error','?')))
        self.refresh()

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
