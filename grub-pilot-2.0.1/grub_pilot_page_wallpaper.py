#!/usr/bin/env python3
"""Grub Pilot - Hintergrundbild setzen"""
import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter as tk
import os
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class WallpaperPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus      = dbus_client
        self.toast     = toast
        self._path_var = tk.StringVar()
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('wallpaper_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0,16))

        # Aktuelles Bild
        self._load_current()

        # Auswahl-Karte
        card = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                            border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', pady=5)

        ctk.CTkLabel(card, text=t('wallpaper_select'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=18, pady=(14,8))

        row = ctk.CTkFrame(card, fg_color='transparent')
        row.pack(fill='x', padx=18, pady=(0,6))
        row.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(row, textvariable=self._path_var,
                     placeholder_text=t('wallpaper_path_hint'),
                     height=38, font=ctk.CTkFont(size=12),
                     fg_color=COLORS['bg'],
                     border_color=COLORS['border'],
                     ).grid(row=0, column=0, sticky='ew', padx=(0,8))

        ctk.CTkButton(row, text=t('wallpaper_browse'),
                      width=140, height=38, corner_radius=8,
                      fg_color=COLORS['border'], text_color=COLORS['text'],
                      hover_color=COLORS['card_hover'],
                      command=self._pick).grid(row=0, column=1)

        ctk.CTkLabel(card, text=t('wallpaper_formats'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(anchor='w', padx=18, pady=(0,4))

        # Vorschau-Bereich
        self._preview = ctk.CTkLabel(card, text='🖼️',
                                     font=ctk.CTkFont(size=48),
                                     text_color=COLORS['text_dim'],
                                     height=140)
        self._preview.pack(pady=(6,4))
        self._preview_lbl = ctk.CTkLabel(card, text=t('wallpaper_no_preview'),
                                         font=ctk.CTkFont(size=11),
                                         text_color=COLORS['text_dim'])
        self._preview_lbl.pack(pady=(0,14))

        if self._path_var.get():
            self._update_preview(self._path_var.get())

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color='transparent')
        btn_row.pack(anchor='w', pady=14)

        ctk.CTkButton(btn_row, text=t('wallpaper_set'), height=42,
                      width=180, corner_radius=10,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._set).pack(side='left', padx=(0,10))

        ctk.CTkButton(btn_row, text=t('wallpaper_remove'), height=42,
                      width=180, corner_radius=10,
                      fg_color='#b45309', hover_color='#92400e',
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13),
                      command=self._remove).pack(side='left')

    def _load_current(self):
        try:
            r = self.dbus.call('get_wallpaper')
            if r.get('path'):
                self._path_var.set(r['path'])
        except Exception:
            pass

    def _pick(self):
        path = fd.askopenfilename(
            title=t('wallpaper_title'),
            filetypes=[
                ('Bilder', '*.png *.jpg *.jpeg *.tga *.bmp'),
                ('PNG', '*.png'), ('JPEG', '*.jpg *.jpeg'),
                ('Alle', '*.*'),
            ],
        )
        if path:
            self._path_var.set(path)
            self._update_preview(path)

    def _update_preview(self, path: str):
        """Vorschau-Bild laden (PIL)."""
        if not os.path.isfile(path):
            return
        try:
            from PIL import Image as PImage, ImageTk
            img = PImage.open(path)
            img.thumbnail((320, 130))
            photo = ImageTk.PhotoImage(img)
            self._preview.configure(image=photo, text='')
            self._preview.image = photo
            w, h = img.size
            self._preview_lbl.configure(
                text=f'{os.path.basename(path)}  ({w}×{h}px)')
        except Exception:
            self._preview_lbl.configure(text=os.path.basename(path))

    def _set(self):
        path = self._path_var.get().strip()
        if not path:
            self.toast.warning(t('wallpaper_no_file'))
            return
        if not os.path.isfile(path):
            self.toast.error(f'Datei nicht gefunden: {path}')
            return
        r = self.dbus.call('set_wallpaper', path)
        if r.get('success'):
            self.toast.success(t('wallpaper_set_ok'))
        else:
            self.toast.error(r.get('error', '?'))

    def _remove(self):
        r = self.dbus.call('set_wallpaper', '')
        if r.get('success'):
            self._path_var.set('')
            self._preview.configure(image='', text='🖼️')
            self._preview_lbl.configure(text=t('wallpaper_no_preview'))
            self.toast.success(t('wallpaper_removed'))
        else:
            self.toast.error(r.get('error', '?'))

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
