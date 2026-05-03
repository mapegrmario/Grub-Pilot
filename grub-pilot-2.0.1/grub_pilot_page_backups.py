#!/usr/bin/env python3
"""Grub Pilot - Backups Page (in-app Bestätigung)"""
import customtkinter as ctk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class BackupsPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus  = dbus_client
        self.toast = toast
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('backups_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0, 14))

        backups = self.dbus.call('list_backups')
        if isinstance(backups, dict) or not backups:
            self._empty_state(); return

        sc = ctk.CTkScrollableFrame(self, fg_color='transparent')
        sc.pack(expand=True, fill='both')
        for b in backups:
            self._backup_card(sc, b)

    def _empty_state(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=16,
                         border_width=1, border_color=COLORS['border'])
        f.pack(expand=True, fill='both', padx=4)
        ctk.CTkLabel(f, text='💾', font=ctk.CTkFont(size=48)).pack(pady=(40,8))
        ctk.CTkLabel(f, text=t('backups_empty'), font=ctk.CTkFont(size=14),
                     text_color=COLORS['text_dim']).pack()

    def _backup_card(self, parent, b):
        card = ctk.CTkFrame(parent, fg_color=COLORS['card'], corner_radius=12,
                            border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=5, padx=2)
        card.bind('<Enter>', lambda _: card.configure(fg_color=COLORS['card_hover']))
        card.bind('<Leave>', lambda _: card.configure(fg_color=COLORS['card']))

        info = ctk.CTkFrame(card, fg_color='transparent')
        info.pack(side='left', padx=18, pady=12)
        ctk.CTkLabel(info, text=b.get('timestamp', b.get('id','')),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w')
        if b.get('description'):
            ctk.CTkLabel(info, text=b['description'],
                         font=ctk.CTkFont(size=11),
                         text_color=COLORS['text_dim']).pack(anchor='w')

        ctk.CTkButton(card, text=t('backups_restore'), width=150, height=34,
                      corner_radius=8, fg_color='#b45309', text_color='#ffffff',
                      hover_color='#92400e',
                      command=lambda bid=b['id']: self._confirm(bid)
                      ).pack(side='right', padx=14, pady=12)

    def _confirm(self, bid):
        overlay = ctk.CTkFrame(self, fg_color='#00000066', corner_radius=0)
        overlay.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        dialog = ctk.CTkFrame(overlay, fg_color=COLORS['card'], corner_radius=18,
                              border_width=1, border_color=COLORS['border'],
                              width=420, height=200)
        dialog.place(relx=0.5, rely=0.5, anchor='center')
        dialog.pack_propagate(False)

        ctk.CTkLabel(dialog, text=t('backups_confirm'),
                     font=ctk.CTkFont(size=14), justify='center',
                     wraplength=360, text_color=COLORS['text']
                     ).pack(pady=28, padx=20)

        btn_row = ctk.CTkFrame(dialog, fg_color='transparent')
        btn_row.pack()

        def do_restore():
            overlay.destroy()
            r = self.dbus.call('restore_backup', bid)
            if r.get('success'):
                self.toast.success(t('toast_restore_ok'))
            else:
                self.toast.error(t('toast_restore_err', error=r.get('error','?')))
            self.refresh()

        ctk.CTkButton(btn_row, text=t('yes'), width=120, height=36,
                      fg_color='#b45309', text_color='#ffffff',
                      hover_color='#92400e', command=do_restore).pack(side='left', padx=8)
        ctk.CTkButton(btn_row, text=t('no'), width=120, height=36,
                      fg_color=COLORS['border'], text_color=COLORS['text'],
                      hover_color=COLORS['card_hover'],
                      command=overlay.destroy).pack(side='left', padx=8)

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
