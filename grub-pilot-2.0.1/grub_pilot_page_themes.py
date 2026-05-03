#!/usr/bin/env python3
"""Grub Pilot - Themes Page mit Theme-Installer (.tar.xz)"""
import customtkinter as ctk
import tkinter.filedialog as fd
import os
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class ThemesPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus       = dbus_client
        self.toast      = toast
        self._path_var  = ctk.StringVar()
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────

    def _build(self):
        # ── Seitentitel ───────────────────────────────────────────────────
        ctk.CTkLabel(self, text=t('themes_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0, 16))

        # ── Installer-Bereich ─────────────────────────────────────────────
        self._build_installer()

        # ── Trennlinie ────────────────────────────────────────────────────
        ctk.CTkFrame(self, fg_color=COLORS['border'],
                     height=1).pack(fill='x', pady=14)

        # ── Installierte Themes ───────────────────────────────────────────
        ctk.CTkLabel(self, text=t('themes_activate_hint'),
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS['text_dim']).pack(anchor='w', pady=(0, 8))

        themes = self.dbus.call('list_themes')
        if isinstance(themes, dict) or not themes:
            self._empty_state()
        else:
            sc = ctk.CTkScrollableFrame(self, fg_color='transparent',
                                        height=260)
            sc.pack(fill='x')
            for th in themes:
                self._theme_card(sc, th)

    def _build_installer(self):
        """Installer-Karte für .tar.xz-Dateien."""
        card = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=14,
                            border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=(0, 4))

        # Kopfzeile
        hdr = ctk.CTkFrame(card, fg_color='transparent')
        hdr.pack(fill='x', padx=18, pady=(16, 10))

        badge = ctk.CTkFrame(hdr, fg_color=COLORS['accent_light'],
                             corner_radius=8, width=40, height=40)
        badge.pack(side='left')
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text='📦',
                     font=ctk.CTkFont(size=20)).place(relx=0.5, rely=0.5,
                                                      anchor='center')

        txt = ctk.CTkFrame(hdr, fg_color='transparent')
        txt.pack(side='left', padx=10)
        ctk.CTkLabel(txt, text=t('themes_install_title'),
                     font=ctk.CTkFont(size=14, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w')
        ctk.CTkLabel(txt, text=t('themes_install_hint'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(anchor='w')

        # Dateiauswahl-Zeile
        row = ctk.CTkFrame(card, fg_color='transparent')
        row.pack(fill='x', padx=18, pady=(0, 4))
        row.grid_columnconfigure(0, weight=1)

        self._path_entry = ctk.CTkEntry(
            row,
            textvariable=self._path_var,
            placeholder_text=t('themes_install_path'),
            height=38, corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['bg'],
            border_color=COLORS['border'],
        )
        self._path_entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))

        ctk.CTkButton(
            row,
            text=t('themes_install_select'),
            width=140, height=38, corner_radius=8,
            fg_color=COLORS['border'], text_color=COLORS['text'],
            hover_color=COLORS['card_hover'],
            font=ctk.CTkFont(size=12),
            command=self._pick_file,
        ).grid(row=0, column=1)

        # Install-Button + Status-Label
        bottom = ctk.CTkFrame(card, fg_color='transparent')
        bottom.pack(fill='x', padx=18, pady=(8, 18))

        self._install_btn = ctk.CTkButton(
            bottom,
            text=t('themes_install_do'),
            height=40, corner_radius=10, width=180,
            fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
            text_color='#ffffff',
            font=ctk.CTkFont(size=13, weight='bold'),
            command=self._install,
        )
        self._install_btn.pack(side='left')

        self._status_lbl = ctk.CTkLabel(
            bottom, text='',
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_dim'],
        )
        self._status_lbl.pack(side='left', padx=14)

    def _empty_state(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                         border_width=1, border_color=COLORS['border'])
        f.pack(fill='x', pady=4)
        ctk.CTkLabel(f, text='🎨', font=ctk.CTkFont(size=36)).pack(pady=(20, 4))
        ctk.CTkLabel(f, text=t('themes_empty'), font=ctk.CTkFont(size=13),
                     text_color=COLORS['text_dim']).pack()
        ctk.CTkLabel(f, text=t('themes_hint'), font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(pady=(2, 16))

    def _theme_card(self, parent, theme: dict):
        card = ctk.CTkFrame(parent, fg_color=COLORS['card'], corner_radius=10,
                            border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=4, padx=2)
        card.bind('<Enter>',
                  lambda _: card.configure(fg_color=COLORS['card_hover']))
        card.bind('<Leave>',
                  lambda _: card.configure(fg_color=COLORS['card']))

        # Theme-Icon + Name
        left = ctk.CTkFrame(card, fg_color='transparent')
        left.pack(side='left', padx=16, pady=12)
        ctk.CTkLabel(left, text='🎨',
                     font=ctk.CTkFont(size=22)).pack(side='left')
        info = ctk.CTkFrame(left, fg_color='transparent')
        info.pack(side='left', padx=8)
        ctk.CTkLabel(info, text=theme['name'],
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w')
        ctk.CTkLabel(info, text=theme['path'],
                     font=ctk.CTkFont(size=10),
                     text_color=COLORS['text_dim']).pack(anchor='w')

        # Aktivieren-Button
        ctk.CTkButton(
            card,
            text=t('themes_activate'),
            width=120, height=34, corner_radius=8,
            fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
            text_color='#ffffff', font=ctk.CTkFont(size=12),
            command=lambda th=theme: self._activate(th),
        ).pack(side='right', padx=14, pady=10)

    # ── Aktionen ──────────────────────────────────────────────────────────

    def _pick_file(self):
        """Öffnet den System-Dateidialog für .tar.xz-Dateien."""
        path = fd.askopenfilename(
            title=t('themes_install_title'),
            filetypes=[
                ('GRUB Theme Archive', '*.tar.xz *.tar.gz *.tar.bz2 *.tar'),
                ('Alle Dateien', '*.*'),
            ],
        )
        if path:
            self._path_var.set(path)
            self._status_lbl.configure(text='')

    def _install(self):
        """Installiert das gewählte Theme-Archiv."""
        path = self._path_var.get().strip()
        if not path:
            self._status_lbl.configure(
                text=t('themes_no_file'), text_color=COLORS['warning'])
            return
        if not os.path.isfile(path):
            self._status_lbl.configure(
                text=f'⚠️  Datei nicht gefunden: {path}',
                text_color=COLORS['warning'])
            return

        # UI während der Installation sperren
        self._install_btn.configure(state='disabled',
                                    text=t('themes_installing'))
        self._status_lbl.configure(
            text=t('themes_installing'), text_color=COLORS['text_dim'])
        self.update()

        r = self.dbus.call('install_theme_archive', path)

        # UI entsperren
        self._install_btn.configure(state='normal',
                                    text=t('themes_install_do'))

        if r.get('success'):
            names = ', '.join(r.get('installed', []))
            target = r.get('target', '')
            self._status_lbl.configure(
                text=t('themes_installed_in', path=target),
                text_color=COLORS['success'])
            self._path_var.set('')
            self.toast.success(t('themes_install_ok', names=names))
            self.refresh()
        else:
            err = r.get('error', '?')
            self._status_lbl.configure(
                text=t('themes_install_err', error=err),
                text_color=COLORS['error'])
            self.toast.error(t('themes_install_err', error=err))

    def _activate(self, theme: dict):
        r = self.dbus.call('set_theme', theme['name'])
        if r.get('success'):
            self.toast.success(t('toast_theme_ok', name=theme['name']))
        else:
            self.toast.error(r.get('error', '?'))
        self.refresh()

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
