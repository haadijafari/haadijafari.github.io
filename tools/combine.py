#!/usr/bin/env python3
"""Paste screenshots side by side for review: tools/combine.py OUT.png IN.png [IN.png ...]"""
import sys
from PIL import Image

ims = [Image.open(p).convert("RGB") for p in sys.argv[2:]]
out = Image.new("RGB", (sum(i.width for i in ims) + 20 * (len(ims) - 1), max(i.height for i in ims)), "#444")
x = 0
for im in ims:
    out.paste(im, (x, 0))
    x += im.width + 20
out.save(sys.argv[1])
