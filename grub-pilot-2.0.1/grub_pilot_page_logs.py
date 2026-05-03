#!/usr/bin/env python3
"""Grub Pilot - Live Log Viewer"""
import customtkinter as ctk
import os, threading, time
from grub_pilot_colors import COLORS
from grub_pilot_lang   import t

LOG_FILE = '/var/log/grub-pilot/fehler.log'


class LogsPage(ctk.CTkFrame):
    def __init__(self, parent, dbus_client, toast, **kwargs):
        super().__init__(parent, fg_color='transparent', **kwargs)
        self.dbus      = dbus_client
        self.toast     = toast
        self._running  = False
        self._thread   = None
        self._build()

    def _build(self):
        # Kopfzeile mit Toolbar
        hdr = ctk.CTkFrame(self, fg_color='transparent')
        hdr.pack(fill='x', pady=(0,12))

        ctk.CTkLabel(hdr, text=t('logs_title'),
                     font=ctk.CTkFont(size=24, weight='bold'),
                     text_color=COLORS['text']).pack(side='left')

        right = ctk.CTkFrame(hdr, fg_color='transparent')
        right.pack(side='right')

        self._live_btn = ctk.CTkButton(right, text='▶  ' + t('logs_live_on'),
                       width=120, height=34, corner_radius=8,
                       fg_color=COLORS['success'], hover_color=COLORS['success_hover'],
                       text_color='#ffffff', font=ctk.CTkFont(size=12),
                       command=self._toggle_live)
        self._live_btn.pack(side='left', padx=4)

        ctk.CTkButton(right, text='🗑  ' + t('logs_clear'),
                      width=90, height=34, corner_radius=8,
                      fg_color=COLORS['border'], text_color=COLORS['text'],
                      hover_color=COLORS['card_hover'],
                      command=self._clear).pack(side='left', padx=4)

        ctk.CTkButton(right, text='💾  ' + t('logs_export'),
                      width=90, height=34, corner_radius=8,
                      fg_color=COLORS['accent_light'], text_color=COLORS['accent'],
                      hover_color=COLORS['card_hover'],
                      command=self._export).pack(side='left')

        # Log-Filter
        filter_row = ctk.CTkFrame(self, fg_color='transparent')
        filter_row.pack(fill='x', pady=(0,8))
        ctk.CTkLabel(filter_row, text=t('logs_filter'),
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS['text_dim']).pack(side='left', padx=(0,8))

        self._filter_btns = {}
        for level, color in [('ALL', COLORS['accent']),
                              ('INFO', '#16a34a'),
                              ('WARN', '#d97706'),
                              ('ERROR', '#dc2626')]:
            btn = ctk.CTkButton(filter_row, text=level, width=70, height=28,
                                corner_radius=6,
                                fg_color=color if level == 'ALL' else COLORS['border'],
                                text_color='#ffffff' if level == 'ALL' else COLORS['text'],
                                hover_color=COLORS['card_hover'],
                                font=ctk.CTkFont(size=11),
                                command=lambda l=level: self._set_filter(l))
            btn.pack(side='left', padx=3)
            self._filter_btns[level] = btn
        self._active_filter = 'ALL'

        # Terminal-Ausgabe
        self._textbox = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family='monospace', size=11),
            fg_color='#1a1a2e', text_color='#e2e8f0',
            corner_radius=12, border_width=1,
            border_color=COLORS['border'],
            wrap='none',
        )
        self._textbox.pack(expand=True, fill='both')
        self._textbox.tag_config('INFO',     foreground='#86efac')
        self._textbox.tag_config('WARNING',  foreground='#fde68a')
        self._textbox.tag_config('ERROR',    foreground='#fca5a5')
        self._textbox.tag_config('CRITICAL', foreground='#f87171')

        # Status-Zeile
        self._status = ctk.CTkLabel(self, text=LOG_FILE,
                                    font=ctk.CTkFont(size=10),
                                    text_color=COLORS['text_dim'])
        self._status.pack(anchor='w', pady=(4,0))

        # Initiales Laden
        self._load_log()

    def _load_log(self):
        self._textbox.configure(state='normal')
        self._textbox.delete('1.0', 'end')
        if not os.path.isfile(LOG_FILE):
            self._textbox.insert('end', f'Log-Datei nicht gefunden: {LOG_FILE}\n')
            self._textbox.configure(state='disabled')
            return
        with open(LOG_FILE) as f:
            lines = f.readlines()
        for line in lines:
            self._insert_line(line.rstrip())
        self._textbox.configure(state='disabled')
        self._textbox.see('end')

    def _insert_line(self, line: str):
        if self._active_filter != 'ALL':
            if self._active_filter not in line:
                return
        tag = ''
        if '[ERROR]' in line or '[CRITICAL]' in line:
            tag = 'ERROR'
        elif '[WARNING]' in line or '[WARN]' in line:
            tag = 'WARNING'
        elif '[INFO]' in line:
            tag = 'INFO'
        self._textbox.configure(state='normal')
        self._textbox.insert('end', line + '\n', tag)
        self._textbox.configure(state='disabled')

    def _toggle_live(self):
        if self._running:
            self._running = False
            self._live_btn.configure(text='▶  ' + t('logs_live_on'),
                                     fg_color=COLORS['success'])
        else:
            self._running = True
            self._live_btn.configure(text='⏹  ' + t('logs_live_off'),
                                     fg_color='#dc2626')
            self._thread = threading.Thread(target=self._tail_log, daemon=True)
            self._thread.start()

    def _tail_log(self):
        if not os.path.isfile(LOG_FILE):
            return
        with open(LOG_FILE) as f:
            f.seek(0, 2)   # ans Ende springen
            while self._running:
                line = f.readline()
                if line:
                    try:
                        self.after(0, self._insert_line, line.rstrip())
                        self.after(0, self._textbox.see, 'end')
                    except Exception:
                        break
                else:
                    time.sleep(0.5)

    def _set_filter(self, level: str):
        self._active_filter = level
        for lv, btn in self._filter_btns.items():
            if lv == level:
                btn.configure(fg_color=COLORS['accent'], text_color='#ffffff')
            else:
                btn.configure(fg_color=COLORS['border'], text_color=COLORS['text'])
        self._load_log()

    def _clear(self):
        self._textbox.configure(state='normal')
        self._textbox.delete('1.0', 'end')
        self._textbox.configure(state='disabled')

    def _export(self):
        import tkinter.filedialog as fd
        from datetime import datetime
        path = fd.asksaveasfilename(
            defaultextension='.log',
            filetypes=[('Log-Datei', '*.log'), ('Text', '*.txt')],
            initialfile=f'grub-pilot-{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        )
        if path:
            content = self._textbox.get('1.0', 'end')
            with open(path, 'w') as f:
                f.write(content)
            self.toast.success(f'✅ Exportiert: {path}')

    def refresh(self):
        self._running = False
        for w in self.winfo_children(): w.destroy()
        self._build()
