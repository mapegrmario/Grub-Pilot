#!/usr/bin/env python3
"""Grub Pilot - In-App Toast Notifications"""
import customtkinter as ctk

_KIND = {
    'success': ('#16a34a', '#ffffff'),
    'error':   ('#dc2626', '#ffffff'),
    'info':    ('#2563eb', '#ffffff'),
    'warning': ('#d97706', '#ffffff'),
}


class ToastManager:
    def __init__(self, root: ctk.CTk):
        self.root = root

    def show(self, message: str, kind: str = 'info', duration: int = 3500):
        fg, fg_txt = _KIND.get(kind, _KIND['info'])
        frame = ctk.CTkFrame(self.root, fg_color=fg, corner_radius=12)
        ctk.CTkLabel(frame, text=message, text_color=fg_txt,
                     font=ctk.CTkFont(size=13, weight='bold'),
                     wraplength=340, justify='left').pack(padx=18, pady=12)
        frame.place(relx=1.0, rely=1.0, anchor='se', x=-20, y=-20)
        frame.lift()
        self.root.after(duration, lambda: self._dismiss(frame))

    def _dismiss(self, frame):
        try: frame.place_forget(); frame.destroy()
        except Exception: pass

    def success(self, msg, duration=3200):  self.show(msg, 'success', duration)
    def error  (self, msg, duration=4500):  self.show(msg, 'error',   duration)
    def info   (self, msg, duration=3000):  self.show(msg, 'info',    duration)
    def warning(self, msg, duration=3500):  self.show(msg, 'warning', duration)
