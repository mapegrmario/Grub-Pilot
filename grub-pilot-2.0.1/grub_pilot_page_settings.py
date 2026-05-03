#!/usr/bin/env python3
"""Grub Pilot - Settings Page (nur Sprache, kein Theme-Toggle)"""
import customtkinter as ctk
from grub_pilot_colors         import COLORS
from grub_pilot_lang           import t, set_lang, get_lang
from grub_pilot_config_manager import save_user_config


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, toast, on_lang_change, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.toast          = toast
        self.on_lang_change = on_lang_change
        self._lang_var      = ctk.StringVar(value=get_lang())
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('settings_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0, 20))

        # ── Sprache ───────────────────────────────────────────────────────
        card = self._card()

        # Überschrift-Zeile mit kleinem Icon-Badge
        hdr = ctk.CTkFrame(card, fg_color='transparent')
        hdr.pack(fill='x', padx=20, pady=(18, 12))
        badge = ctk.CTkFrame(hdr, fg_color=COLORS['accent_light'],
                             corner_radius=8, width=36, height=36)
        badge.pack(side='left')
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text='🌍',
                     font=ctk.CTkFont(size=18)).place(relx=0.5, rely=0.5,
                                                      anchor='center')
        ctk.CTkLabel(hdr, text=f'  {t("settings_lang")}',
                     font=ctk.CTkFont(size=15, weight='bold'),
                     text_color=COLORS['text']).pack(side='left', padx=8)

        row = ctk.CTkFrame(card, fg_color='transparent')
        row.pack(anchor='w', padx=20, pady=(0, 20))

        for code, flag, label in [('de', '🇩🇪', 'Deutsch'),
                                   ('en', '🇬🇧', 'English')]:
            rb_frame = ctk.CTkFrame(row, fg_color='transparent')
            rb_frame.pack(side='left', padx=6)
            ctk.CTkRadioButton(
                rb_frame, text=f'{flag}  {label}',
                variable=self._lang_var, value=code,
                font=ctk.CTkFont(size=13), text_color=COLORS['text'],
                fg_color=COLORS['accent'],
                radiobutton_width=18, radiobutton_height=18,
            ).pack()

        # ── Speichern ─────────────────────────────────────────────────────
        ctk.CTkButton(
            self, text=t('settings_save'),
            height=44, corner_radius=10, width=200,
            fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
            text_color='#ffffff', font=ctk.CTkFont(size=14, weight='bold'),
            command=self._save,
        ).pack(anchor='w', pady=24, padx=0)

    def _card(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                         border_width=1, border_color=COLORS['border'])
        f.pack(fill='x', pady=6)
        return f

    def _save(self):
        lang = self._lang_var.get()
        set_lang(lang)
        save_user_config('grub-pilot', 'language', lang)
        self.toast.success(t('toast_saved'))
        self.on_lang_change()

    def refresh(self):
        self._lang_var.set(get_lang())
        for w in self.winfo_children():
            w.destroy()
        self._build()
