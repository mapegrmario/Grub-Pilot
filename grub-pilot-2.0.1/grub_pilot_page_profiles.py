#!/usr/bin/env python3
"""Grub Pilot - Config Export / Import (Profile)"""
import customtkinter as ctk
import tkinter.filedialog as fd
import json, os
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class ProfilesPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus  = dbus_client
        self.toast = toast
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('profiles_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0,16))

        # Export
        exp_card = self._card()
        hdr_exp = ctk.CTkFrame(exp_card, fg_color='transparent')
        hdr_exp.pack(fill='x', padx=18, pady=(16,8))
        badge = ctk.CTkFrame(hdr_exp, fg_color='#dcfce7', corner_radius=8,
                             width=40, height=40)
        badge.pack(side='left'); badge.pack_propagate(False)
        ctk.CTkLabel(badge, text='📤',
                     font=ctk.CTkFont(size=20)).place(relx=0.5, rely=0.5,
                                                      anchor='center')
        lbl = ctk.CTkFrame(hdr_exp, fg_color='transparent')
        lbl.pack(side='left', padx=10)
        ctk.CTkLabel(lbl, text=t('profiles_export_title'),
                     font=ctk.CTkFont(size=14, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w')
        ctk.CTkLabel(lbl, text=t('profiles_export_hint'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(anchor='w')

        ctk.CTkButton(exp_card, text='📤  ' + t('profiles_export_btn'),
                      height=40, width=200, corner_radius=10,
                      fg_color='#16a34a', hover_color='#15803d',
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._export).pack(anchor='w', padx=18, pady=(4,16))

        # Import
        imp_card = self._card()
        hdr_imp = ctk.CTkFrame(imp_card, fg_color='transparent')
        hdr_imp.pack(fill='x', padx=18, pady=(16,8))
        badge2 = ctk.CTkFrame(hdr_imp, fg_color='#dbeafe', corner_radius=8,
                              width=40, height=40)
        badge2.pack(side='left'); badge2.pack_propagate(False)
        ctk.CTkLabel(badge2, text='📥',
                     font=ctk.CTkFont(size=20)).place(relx=0.5, rely=0.5,
                                                       anchor='center')
        lbl2 = ctk.CTkFrame(hdr_imp, fg_color='transparent')
        lbl2.pack(side='left', padx=10)
        ctk.CTkLabel(lbl2, text=t('profiles_import_title'),
                     font=ctk.CTkFont(size=14, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w')
        ctk.CTkLabel(lbl2, text=t('profiles_import_hint'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(anchor='w')

        ctk.CTkButton(imp_card, text='📥  ' + t('profiles_import_btn'),
                      height=40, width=200, corner_radius=10,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._import).pack(anchor='w', padx=18, pady=(4,16))

        # Profil-Vorschau
        ctk.CTkLabel(self, text=t('profiles_current'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(16,6))

        self._preview = ctk.CTkTextbox(
            self, height=200,
            font=ctk.CTkFont(family='monospace', size=11),
            fg_color=COLORS['card'], text_color=COLORS['text'],
            corner_radius=12, border_width=1,
            border_color=COLORS['border'],
        )
        self._preview.pack(fill='x')
        self._load_preview()

    def _card(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                         border_width=1, border_color=COLORS['border'])
        f.pack(fill='x', pady=6)
        return f

    def _get_profile_data(self) -> dict:
        try:
            r = self.dbus.call('export_config')
            return r if isinstance(r, dict) else {}
        except Exception:
            return {}

    def _load_preview(self):
        data = self._get_profile_data()
        self._preview.configure(state='normal')
        self._preview.delete('1.0', 'end')
        self._preview.insert('1.0', json.dumps(data, indent=2, ensure_ascii=False))
        self._preview.configure(state='disabled')

    def _export(self):
        from datetime import datetime
        data = self._get_profile_data()
        if not data:
            self.toast.error(t('profiles_export_empty'))
            return
        path = fd.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('Grub Pilot Profil', '*.json'), ('Alle', '*.*')],
            initialfile=f'grub-pilot-profil-{datetime.now().strftime("%Y%m%d")}.json',
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.toast.success(t('profiles_export_ok').format(path=os.path.basename(path)))

    def _import(self):
        path = fd.askopenfilename(
            title=t('profiles_import_title'),
            filetypes=[('Grub Pilot Profil', '*.json'), ('Alle', '*.*')],
        )
        if not path:
            return
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.toast.error(f'Lesefehler: {e}')
            return

        r = self.dbus.call('import_config', json.dumps(data))
        if r.get('success'):
            self.toast.success(t('profiles_import_ok'))
            self._load_preview()
        else:
            self.toast.error(r.get('error', '?'))

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
