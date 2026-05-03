#!/usr/bin/env python3
"""Grub Pilot - GRUB installieren / reparieren"""
import customtkinter as ctk
import tkinter as tk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class RepairPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus       = dbus_client
        self.toast      = toast
        self._disk_var  = tk.StringVar()
        self._output    = None
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('repair_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0,16))

        # Laufwerks-Auswahl
        disk_card = self._card()
        ctk.CTkLabel(disk_card, text=t('repair_select_disk'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=18, pady=(14,8))

        # Laufwerke laden
        disks = self._get_disks()
        if disks:
            self._disk_var.set(disks[0])

        disk_row = ctk.CTkFrame(disk_card, fg_color='transparent')
        disk_row.pack(fill='x', padx=18, pady=(0,14))

        self._disk_menu = ctk.CTkOptionMenu(
            disk_row, values=disks if disks else ['/dev/sda'],
            variable=self._disk_var,
            font=ctk.CTkFont(size=13),
            height=38, width=220,
            fg_color=COLORS['card'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover'],
            text_color=COLORS['text'],
        )
        self._disk_menu.pack(side='left')

        ctk.CTkButton(disk_row, text='🔄 ' + t('repair_refresh'),
                      width=100, height=38, corner_radius=8,
                      fg_color=COLORS['border'], text_color=COLORS['text'],
                      hover_color=COLORS['card_hover'],
                      command=self._refresh_disks).pack(side='left', padx=8)

        # Aktionen
        act_card = self._card()
        ctk.CTkLabel(act_card, text=t('repair_actions'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=18, pady=(14,10))

        btn_row = ctk.CTkFrame(act_card, fg_color='transparent')
        btn_row.pack(fill='x', padx=18, pady=(0,14))

        ctk.CTkButton(btn_row, text='🔧 ' + t('repair_install'),
                      height=42, width=200, corner_radius=10,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._install_grub).pack(side='left', padx=(0,10))

        ctk.CTkButton(btn_row, text='🔄 ' + t('repair_update'),
                      height=42, width=180, corner_radius=10,
                      fg_color=COLORS['success'], hover_color=COLORS['success_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._update_grub).pack(side='left')

        # Warnung
        warn = ctk.CTkFrame(self, fg_color='#fff8f0', corner_radius=10,
                            border_width=1, border_color='#fcd9b6')
        warn.pack(fill='x', pady=6)
        ctk.CTkLabel(warn, text=t('repair_warning'),
                     font=ctk.CTkFont(size=12),
                     text_color='#7c3a00',
                     wraplength=600, justify='left').pack(padx=16, pady=10)

        # Ausgabe-Terminal
        ctk.CTkLabel(self, text=t('repair_output'),
                     font=ctk.CTkFont(size=12, weight='bold'),
                     text_color=COLORS['text_dim']).pack(anchor='w', pady=(10,4))

        self._output = ctk.CTkTextbox(
            self, height=180,
            font=ctk.CTkFont(family='monospace', size=11),
            fg_color='#1e1e2e', text_color='#cdd6f4',
            corner_radius=10, border_width=1,
            border_color=COLORS['border'],
        )
        self._output.pack(fill='x')
        self._output.configure(state='disabled')

    def _card(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                         border_width=1, border_color=COLORS['border'])
        f.pack(fill='x', pady=5)
        return f

    def _get_disks(self) -> list[str]:
        try:
            r = self.dbus.call('list_disks')
            return r if isinstance(r, list) else []
        except Exception:
            return ['/dev/sda', '/dev/nvme0n1']

    def _refresh_disks(self):
        disks = self._get_disks()
        if disks:
            self._disk_menu.configure(values=disks)
            self._disk_var.set(disks[0])

    def _log(self, text: str):
        if self._output:
            self._output.configure(state='normal')
            self._output.insert('end', text + '\n')
            self._output.see('end')
            self._output.configure(state='disabled')
            self.update()

    def _install_grub(self):
        disk = self._disk_var.get().strip()
        if not disk:
            self.toast.warning(t('repair_no_disk'))
            return
        self._log(f'→ grub-install {disk} ...')
        r = self.dbus.call('grub_install', disk)
        if r.get('success'):
            self._log(r.get('output', 'OK'))
            self.toast.success(t('repair_install_ok'))
        else:
            self._log('❌ ' + r.get('error', '?'))
            self.toast.error(r.get('error', '?'))

    def _update_grub(self):
        self._log('→ update-grub ...')
        r = self.dbus.call('grub_update')
        if r.get('success'):
            self._log(r.get('output', 'OK'))
            self.toast.success(t('repair_update_ok'))
        else:
            self._log('❌ ' + r.get('error', '?'))
            self.toast.error(r.get('error', '?'))

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
