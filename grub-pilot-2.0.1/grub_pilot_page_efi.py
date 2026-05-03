#!/usr/bin/env python3
"""Grub Pilot - EFI Boot-Reihenfolge"""
import customtkinter as ctk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class EfiPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus    = dbus_client
        self.toast   = toast
        self._entries = []
        self._sel_idx = None
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('efi_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0,16))

        if not self._check_uefi():
            self._no_uefi()
            return

        self._load_entries()

        # Toolbar
        tb = ctk.CTkFrame(self, fg_color='transparent')
        tb.pack(fill='x', pady=(0,8))
        ctk.CTkButton(tb, text='🔄 ' + t('efi_refresh'),
                      width=100, height=34, corner_radius=8,
                      fg_color=COLORS['border'], text_color=COLORS['text'],
                      hover_color=COLORS['card_hover'],
                      command=self._reload).pack(side='left', padx=(0,6))
        self._up_btn = ctk.CTkButton(tb, text='⬆  ' + t('efi_up'),
                      width=90, height=34, corner_radius=8,
                      fg_color=COLORS['accent_light'], text_color=COLORS['accent'],
                      hover_color=COLORS['card_hover'],
                      state='disabled', command=self._move_up)
        self._up_btn.pack(side='left', padx=3)
        self._dn_btn = ctk.CTkButton(tb, text='⬇  ' + t('efi_down'),
                      width=90, height=34, corner_radius=8,
                      fg_color=COLORS['accent_light'], text_color=COLORS['accent'],
                      hover_color=COLORS['card_hover'],
                      state='disabled', command=self._move_down)
        self._dn_btn.pack(side='left', padx=3)
        self._del_btn = ctk.CTkButton(tb, text='🗑  ' + t('efi_delete'),
                      width=90, height=34, corner_radius=8,
                      fg_color='#fde8e8', text_color='#c42b1c',
                      hover_color='#fbd5d5',
                      state='disabled', command=self._delete)
        self._del_btn.pack(side='left', padx=3)

        # Eintrags-Liste
        self._list_frame = ctk.CTkScrollableFrame(
            self, fg_color='transparent', height=360)
        self._list_frame.pack(fill='x', pady=4)
        self._render_list()

        # Speichern
        ctk.CTkButton(self, text=t('efi_save_order'), height=42, width=220,
                      corner_radius=10,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._save_order).pack(anchor='w', pady=14)

    def _check_uefi(self) -> bool:
        try:
            r = self.dbus.call('get_system_info')
            return bool(r.get('is_uefi', False))
        except Exception:
            return False

    def _no_uefi(self):
        card = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                            border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=8)
        ctk.CTkLabel(card, text='🖥️',
                     font=ctk.CTkFont(size=48)).pack(pady=(30,8))
        ctk.CTkLabel(card, text=t('efi_no_uefi'),
                     font=ctk.CTkFont(size=14),
                     text_color=COLORS['text_dim']).pack(pady=(0,30))

    def _load_entries(self):
        try:
            r = self.dbus.call('list_efi_entries')
            self._entries = r if isinstance(r, list) else []
        except Exception:
            self._entries = []

    def _reload(self):
        self._load_entries()
        self._sel_idx = None
        self._render_list()
        self._update_btns()

    def _render_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not self._entries:
            ctk.CTkLabel(self._list_frame, text=t('efi_empty'),
                         text_color=COLORS['text_dim'],
                         font=ctk.CTkFont(size=13)).pack(pady=20)
            return

        for i, entry in enumerate(self._entries):
            selected = (i == self._sel_idx)
            bg = COLORS['accent_light'] if selected else COLORS['card']
            card = ctk.CTkFrame(self._list_frame, fg_color=bg,
                                corner_radius=10,
                                border_width=1, border_color=COLORS['border'])
            card.pack(fill='x', pady=3)

            num = ctk.CTkLabel(card, text=f'{i+1:02d}',
                               font=ctk.CTkFont(size=12, weight='bold'),
                               text_color=COLORS['accent'] if selected else COLORS['text_dim'],
                               width=32)
            num.pack(side='left', padx=12, pady=12)

            mid = ctk.CTkFrame(card, fg_color='transparent')
            mid.pack(side='left', expand=True, fill='x', pady=8)
            ctk.CTkLabel(mid, text=entry.get('name', '?'),
                         font=ctk.CTkFont(size=13, weight='bold'),
                         text_color=COLORS['text']).pack(anchor='w')
            ctk.CTkLabel(mid, text=entry.get('id', ''),
                         font=ctk.CTkFont(size=10),
                         text_color=COLORS['text_dim']).pack(anchor='w')

            active_lbl = '✅ Aktiv' if entry.get('active') else ''
            if active_lbl:
                ctk.CTkLabel(card, text=active_lbl,
                             font=ctk.CTkFont(size=11),
                             text_color=COLORS['success']).pack(side='right', padx=14)

            for w in [card, num, mid]:
                w.bind('<Button-1>', lambda e, idx=i: self._select(idx))

    def _select(self, idx: int):
        self._sel_idx = idx
        self._render_list()
        self._update_btns()

    def _update_btns(self):
        has = self._sel_idx is not None
        n   = len(self._entries)
        self._up_btn.configure(state='normal' if has and self._sel_idx > 0 else 'disabled')
        self._dn_btn.configure(state='normal' if has and self._sel_idx < n-1 else 'disabled')
        self._del_btn.configure(state='normal' if has else 'disabled')

    def _move_up(self):
        i = self._sel_idx
        if i and i > 0:
            self._entries[i], self._entries[i-1] = self._entries[i-1], self._entries[i]
            self._sel_idx = i - 1
            self._render_list(); self._update_btns()

    def _move_down(self):
        i = self._sel_idx
        if i is not None and i < len(self._entries) - 1:
            self._entries[i], self._entries[i+1] = self._entries[i+1], self._entries[i]
            self._sel_idx = i + 1
            self._render_list(); self._update_btns()

    def _delete(self):
        if self._sel_idx is None:
            return
        entry = self._entries[self._sel_idx]
        r = self.dbus.call('delete_efi_entry', entry.get('id', ''))
        if r.get('success'):
            self.toast.success(t('efi_deleted'))
            self._reload()
        else:
            self.toast.error(r.get('error', '?'))

    def _save_order(self):
        order = [e.get('id', '') for e in self._entries]
        r = self.dbus.call('set_efi_order', ','.join(order))
        if r.get('success'):
            self.toast.success(t('efi_order_saved'))
        else:
            self.toast.error(r.get('error', '?'))

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
