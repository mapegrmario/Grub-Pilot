#!/usr/bin/env python3
"""Grub Pilot - Kernel-Parameter-Editor"""
import customtkinter as ctk
import tkinter as tk
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t

# Häufige Parameter mit Beschreibung
COMMON_PARAMS = [
    ("quiet",                   "Stille Ausgabe beim Boot"),
    ("splash",                  "Splash-Screen anzeigen"),
    ("nomodeset",               "Grafiktreiber-Probleme beheben"),
    ("nvidia-drm.modeset=1",    "NVIDIA DRM Modus"),
    ("acpi=off",                "ACPI deaktivieren"),
    ("noapic",                  "APIC deaktivieren"),
    ("nolapic",                 "Local APIC deaktivieren"),
    ("pci=nomsi",               "MSI Interrupts deaktivieren"),
    ("iommu=soft",              "Software IOMMU"),
    ("amd_iommu=on",            "AMD IOMMU aktivieren"),
    ("intel_iommu=on",          "Intel IOMMU aktivieren"),
    ("mitigations=off",         "CPU-Mitigationen deaktivieren (schneller)"),
    ("threadirqs",              "Thread IRQs"),
    ("elevator=deadline",       "I/O Scheduler: deadline"),
    ("systemd.unified_cgroup_hierarchy=1", "cgroup v2"),
]


class KernelPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus      = dbus_client
        self.toast     = toast
        self._params   = tk.StringVar()
        self._toggles  = {}
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t('kernel_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', pady=(0,16))

        # Aktuelle Parameter laden
        self._load_current()

        # Aktueller Wert-Editor
        edit_card = self._card()
        ctk.CTkLabel(edit_card, text=t('kernel_current'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=18, pady=(14,6))
        self._entry = ctk.CTkEntry(edit_card, textvariable=self._params,
                                   height=38, font=ctk.CTkFont(size=12),
                                   fg_color=COLORS['bg'],
                                   border_color=COLORS['border'])
        self._entry.pack(fill='x', padx=18, pady=(0,14))

        # Schnell-Toggles
        toggle_card = self._card()
        ctk.CTkLabel(toggle_card, text=t('kernel_toggles'),
                     font=ctk.CTkFont(size=13, weight='bold'),
                     text_color=COLORS['text']).pack(anchor='w', padx=18, pady=(14,8))

        grid = ctk.CTkFrame(toggle_card, fg_color='transparent')
        grid.pack(fill='x', padx=12, pady=(0,14))

        for i, (param, desc) in enumerate(COMMON_PARAMS):
            var = ctk.BooleanVar(value=param in self._params.get())
            self._toggles[param] = var
            row = i // 2
            col = i %  2
            cb = ctk.CTkCheckBox(grid, text=f"{param}",
                                 variable=var,
                                 font=ctk.CTkFont(size=12),
                                 text_color=COLORS['text'],
                                 fg_color=COLORS['accent'],
                                 command=lambda p=param, v=var: self._toggle(p, v))
            cb.grid(row=row, column=col, sticky='w', padx=14, pady=3)
            # Tooltip-Label
            ctk.CTkLabel(grid, text=f"  {desc}",
                         font=ctk.CTkFont(size=10),
                         text_color=COLORS['text_dim']
                         ).grid(row=row, column=col, sticky='e', padx=4)

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # mem= Eingabe
        mem_row = ctk.CTkFrame(toggle_card, fg_color='transparent')
        mem_row.pack(fill='x', padx=18, pady=(0,14))
        ctk.CTkLabel(mem_row, text='mem=',
                     font=ctk.CTkFont(size=12, weight='bold'),
                     text_color=COLORS['text']).pack(side='left')
        self._mem_entry = ctk.CTkEntry(mem_row, width=100, height=32,
                                       placeholder_text='z.B. 4G',
                                       font=ctk.CTkFont(size=12),
                                       fg_color=COLORS['bg'],
                                       border_color=COLORS['border'])
        self._mem_entry.pack(side='left', padx=8)
        ctk.CTkButton(mem_row, text='+ Hinzufügen', width=110, height=32,
                      corner_radius=8,
                      fg_color=COLORS['accent_light'],
                      text_color=COLORS['accent'],
                      hover_color=COLORS['card_hover'],
                      command=self._add_mem).pack(side='left')

        # Speichern-Button
        ctk.CTkButton(self, text=t('kernel_save'), height=42,
                      corner_radius=10, width=200,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      text_color='#ffffff',
                      font=ctk.CTkFont(size=13, weight='bold'),
                      command=self._save).pack(anchor='w', pady=18)

    def _card(self):
        f = ctk.CTkFrame(self, fg_color=COLORS['card'], corner_radius=12,
                         border_width=1, border_color=COLORS['border'])
        f.pack(fill='x', pady=5)
        return f

    def _load_current(self):
        try:
            r = self.dbus.call('get_kernel_params')
            self._params.set(r.get('params', 'quiet splash'))
        except Exception:
            self._params.set('quiet splash')

    def _toggle(self, param: str, var: ctk.BooleanVar):
        params = self._params.get().split()
        if var.get():
            if param not in params:
                params.append(param)
        else:
            params = [p for p in params if p != param]
        self._params.set(' '.join(params))

    def _add_mem(self):
        val = self._mem_entry.get().strip()
        if val:
            cur = self._params.get()
            # Alten mem= entfernen
            parts = [p for p in cur.split() if not p.startswith('mem=')]
            parts.append(f'mem={val}')
            self._params.set(' '.join(parts))
            self._mem_entry.delete(0, 'end')

    def _save(self):
        params = self._params.get().strip()
        r = self.dbus.call('set_kernel_params', params)
        if r.get('success'):
            self.toast.success(t('kernel_saved'))
        else:
            self.toast.error(r.get('error', '?'))

    def refresh(self):
        for w in self.winfo_children(): w.destroy()
        self._build()
