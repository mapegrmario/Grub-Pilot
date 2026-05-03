#!/usr/bin/env python3
"""Grub Pilot - Boot-Timeout Page"""
import customtkinter as ctk
import tkinter as tk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t


class TimeoutPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus       = dbus_client
        self.toast      = toast
        self._timeout_v = tk.StringVar(value='5')
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('timeout_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0, 24))

        card = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=18,
                            border_width=1, border_color=COLORS['border'])
        card.pack(fill='x', padx=4, pady=8, ipady=10)

        self._display = ctk.CTkLabel(card,
            text=t('timeout_sec', n=5),
            font=ctk.CTkFont(size=54, weight='bold'),
            text_color=COLORS['accent'])
        self._display.pack(pady=(28, 10))

        self._slider = ctk.CTkSlider(card, from_=-1, to=30, number_of_steps=31,
            command=self._on_slide, height=22,
            button_color=COLORS['accent'], progress_color=COLORS['accent'])
        self._slider.set(5)
        self._slider.pack(fill='x', padx=50, pady=(0, 8))

        ctk.CTkLabel(card, text=t('timeout_hint'),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS['text_dim']).pack(pady=(0, 20))

        ctk.CTkButton(card, text=t('timeout_save'), height=44, corner_radius=10,
                      fg_color=COLORS['success'], hover_color=COLORS['success_hover'],
                      text_color='#ffffff', font=ctk.CTkFont(size=14, weight='bold'),
                      command=self._save).pack(pady=(0,28), padx=50, fill='x')

    def _on_slide(self, val):
        v = int(float(val))
        self._timeout_v.set(str(v))
        if v == -1:   self._display.configure(text=t('timeout_disabled'))
        elif v == 0:  self._display.configure(text=t('timeout_instant'))
        else:         self._display.configure(text=t('timeout_sec', n=v))

    def _save(self):
        r = self.dbus.call('set_timeout', self._timeout_v.get())
        if r.get('success'):
            self.toast.success(t('toast_timeout_ok', t=self._timeout_v.get()))
        else:
            self.toast.error(t('toast_timeout_err', error=r.get('error','?')))

    def refresh(self): pass
