#!/usr/bin/env python3
"""Grub Pilot - Eigene Boot-Einträge (/etc/grub.d/40_custom)"""
import customtkinter as ctk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t

TEMPLATE = """menuentry "Eigener Eintrag" {
    set root=(hd0,1)
    linux /vmlinuz root=/dev/sda1
    initrd /initrd.img
}"""


class CustomEntriesPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus  = dbus_client
        self.toast = toast
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('custom_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0,8))

        ctk.CTkLabel(self, text=t('custom_hint'),
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS['text_dim']).pack(anchor='w', pady=(0,14))

        # Toolbar
        tb = ctk.CTkFrame(self, fg_color='transparent')
        tb.pack(fill='x', pady=(0,8))

        ctk.CTkButton(tb, text='📄 ' + t('custom_template'),
                      width=130, height=34, corner_radius=8,
                      fg_color=COLORS['accent_light'], text_color=COLORS['accent'],
                      hover_color=COLORS['card_hover'],
                      command=self._insert_template).pack(side='left', padx=(0,6))

        ctk.CTkButton(tb, text='🔄 ' + t('custom_reload'),
                      width=100, height=34, corner_radius=8,
                      fg_color=COLORS['border'], text_color=COLORS['text'],
                      hover_color=COLORS['card_hover'],
                      command=self._reload).pack(side='left', padx=3)

        # Editor
        self._editor = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family='monospace', size=12),
            fg_color=COLORS['card'], text_color=COLORS['text'],
            corner_radius=12, border_width=1,
            border_color=COLORS['border'],
            wrap='none',
        )
        self._editor.pack(expand=True, fill='both', pady=4)
        self._load()

        # Status + Speichern
        bottom = ctk.CTkFrame(self, fg_color='transparent')
        bottom.pack(fill='x', pady=(8,0))
        ctk.CTkButton(bottom, text=t('custom_save'), height=42, width=200,
                      corner_radius=10,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._save).pack(side='left')
        self._status = ctk.CTkLabel(bottom, text='/etc/grub.d/40_custom',
                                    font=ctk.CTkFont(size=10),
                                    text_color=COLORS['text_dim'])
        self._status.pack(side='left', padx=12)

    def _load(self):
        r = self.dbus.call('get_custom_entries')
        content = r.get('content', '') if isinstance(r, dict) else ''
        self._editor.delete('1.0', 'end')
        self._editor.insert('1.0', content or t('custom_empty_placeholder'))

    def _reload(self):
        self._load()
        self._status.configure(text=t('custom_reloaded'),
                               text_color=COLORS['success'])
        self.after(3000, lambda: self._status.configure(
            text='/etc/grub.d/40_custom', text_color=COLORS['text_dim']))

    def _insert_template(self):
        self._editor.insert('end', '\n' + TEMPLATE + '\n')

    def _save(self):
        content = self._editor.get('1.0', 'end').strip()
        r = self.dbus.call('set_custom_entries', content)
        if r.get('success'):
            self.toast.success(t('custom_saved'))
        else:
            self.toast.error(r.get('error', '?'))

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
