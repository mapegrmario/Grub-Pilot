#!/usr/bin/env python3
"""Grub Pilot – Icon Generator (wird vom install.sh aufgerufen)"""
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("PIL nicht verfügbar – Icon übersprungen", file=sys.stderr)
    sys.exit(0)

import os
os.makedirs('/usr/share/icons/grub-pilot', exist_ok=True)

img  = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Hintergrund
draw.rounded_rectangle([8, 8, 248, 248], radius=42, fill=(13, 13, 32))
draw.rounded_rectangle([16, 16, 240, 240], radius=36, fill=(20, 20, 50))

# Schild (äußere Fläche)
shield = [(128, 56), (196, 96), (196, 172), (128, 216), (60, 172), (60, 96)]
draw.polygon(shield, fill=(74, 158, 255))

# Schild (innere Aussparung)
inner = [(128, 76), (178, 108), (178, 168), (128, 196), (78, 168), (78, 108)]
draw.polygon(inner, fill=(20, 20, 50))

# Text "GP"
try:
    from PIL import ImageFont
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 48)
    draw.text((128, 148), 'GP', fill=(74, 158, 255), anchor='ms', font=font)
except Exception:
    draw.text((128, 148), 'GP', fill=(74, 158, 255), anchor='ms')

img.save('/usr/share/icons/grub-pilot/icon.png')
print("Icon erstellt: /usr/share/icons/grub-pilot/icon.png")
