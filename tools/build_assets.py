#!/usr/bin/env python3
"""Generate every optimized asset the page serves from its originals.

Usage: python3 tools/build_assets.py [hero|avatar|hobbies|certs|edu|footer|fonts|sprite ...]

Idempotent: re-run whenever an original changes or a certificate is added
(add it to CERTS). Originals are never served; only these outputs are.
"""
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from fontTools import subset
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Source-pixel box (left, top, right, bottom) on the EXIF-transposed
# 3549x5323 photo: 2:3 portrait from just above the hair to the waist.
HERO_SRC = "images/hero/IMG_0154.jpg"
HERO_CROP = (250, 400, 3183, 4800)
# 1200x630 social preview, face in the middle.
OG_CROP = (215, 500, 3215, 2075)

HOBBIES = {
    "chess": "images/hobbies/chess2.jpg",
    "martial-arts": "images/hobbies/jiu-jitsu.jpg",
    "guitar": "images/hobbies/music1.webp",
    "learning": "images/hobbies/brain.jpeg",
    "friends": "images/hobbies/friends2.jpg",
}

# slug: (thumbnail source, full-size source)
CERTS = {
    "ml-foundations-duke": ("resume/Docs/Machine Learning Foundations for Product Managers.pdf",) * 2,
    "basic-python": ("images/certifications/Basic-Python.jpg",) * 2,
    "advanced-python": ("images/certifications/Advanced-Python.jpg",) * 2,
    "python-oop": ("images/certifications/Python-OOP.jpg",) * 2,
    "django-basic": ("images/certifications/Django-Basic.png",) * 2,
    "git": ("images/certifications/Git.png",) * 2,
    "frontend": ("images/certifications/Frontend.png",) * 2,
    "c": ("images/certifications/C.jpg",) * 2,
    "ef-set": ("images/certifications/EF-SET-Certificate.png", "images/certifications/EF-SET-Certificate-min.jpg"),
    "odoo": ("images/certifications/BTCO-Certificate.jpg",) * 2,
}

ATU_VIEWBOX = "50 20 1600 1935"
EDU = {"sku": "images/edu/sku.png", "sampad": "images/edu/Sampad.png"}
FONTS = {
    "pinyon-script": "fonts/PinyonScript-Regular.ttf",
    "satisfy": "fonts/Satisfy-Regular.ttf",
    "herr-von-muellerhoff": "fonts/HerrVonMuellerhoff-Regular.ttf",
}
AVATAR_SRC = "images/avatar/me.jpg"


def p(path):
    return os.path.join(ROOT, path)


def load(path):
    if path.endswith(".pdf"):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "page")
            subprocess.run(["pdftoppm", "-r", "110", "-png", "-singlefile", p(path), out], check=True)
            return Image.open(out + ".png").convert("RGB")
    return ImageOps.exif_transpose(Image.open(p(path))).convert("RGB")


def save_webp(img, path, long_edge, quality=78):
    img = img.copy()
    img.thumbnail((long_edge, long_edge), Image.LANCZOS)
    img.save(p(path), "WEBP", quality=quality, method=6)
    print("wrote", path, img.size, os.path.getsize(p(path)))


def hero():
    src = load(HERO_SRC)
    crop = src.crop(HERO_CROP)
    for w in (600, 1200):
        save_webp(crop, "images/hero/hadi-%d.webp" % w, w * 3 // 2, quality=74)
    og = src.crop(OG_CROP).resize((1200, 630), Image.LANCZOS)
    og.save(p("hadi-jafari.jpg"), "JPEG", quality=80, optimize=True, progressive=True)
    print("wrote hadi-jafari.jpg", os.path.getsize(p("hadi-jafari.jpg")))


def hobbies():
    for slug, src in HOBBIES.items():
        save_webp(load(src), "images/hobbies/%s.webp" % slug, 480)


def certs():
    for slug, (thumb_src, full_src) in CERTS.items():
        thumb = load(thumb_src)
        save_webp(thumb, "images/certifications/%s-thumb.webp" % slug, 480, quality=72)
        full = thumb if full_src == thumb_src else load(full_src)
        save_webp(full, "images/certifications/%s.webp" % slug, 1600)


def avatar():
    src = load(AVATAR_SRC)
    for w in (480, 800):
        save_webp(src, "images/avatar/me-%d.webp" % w, w * src.height // src.width)


def footer_waves():
    """The footer divider without its solid black backdrop, so its top blends into the page."""
    svg = open(p("images/svg/footer-top.svg"), encoding="utf-8").read()
    svg = re.sub(r'<rect[^>]*></rect>|<rect[^>]*/>', "", svg, count=1)
    open(p("images/svg/footer-waves.svg"), "w", encoding="utf-8").write(svg)
    print("wrote images/svg/footer-waves.svg", os.path.getsize(p("images/svg/footer-waves.svg")))


def edu():
    # The SKU and Sampad originals are white artwork on transparency (made for dark
    # pages); recolor them black so they read on the white logo tiles like the ATU logo.
    for slug, src in EDU.items():
        img = Image.open(p(src)).convert("RGBA")
        black = Image.new("RGBA", img.size, (0, 0, 0, 255))
        black.putalpha(img.getchannel("A"))
        save_webp(black, "images/edu/%s.webp" % slug, 200, quality=85)
    atu_clean()


def atu_clean():
    """Strip the off-canvas embedded PNG and Inkscape/Sodipodi metadata."""
    ns_drop = ("http://www.inkscape.org/namespaces/inkscape",
               "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
               "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
               "http://purl.org/dc/elements/1.1/",
               "http://creativecommons.org/ns#")
    svg_ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", svg_ns)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    tree = ET.parse(p("images/edu/ATU.svg"))
    root = tree.getroot()

    def dropped(el):
        tag = el.tag
        if tag in ("{%s}image" % svg_ns, "{%s}metadata" % svg_ns):
            return True
        return any(tag.startswith("{%s}" % ns) for ns in ns_drop)

    def clean(el):
        for child in list(el):
            if dropped(child):
                el.remove(child)
            else:
                clean(child)
        for key in list(el.attrib):
            if any(key.startswith("{%s}" % ns) for ns in ns_drop):
                del el.attrib[key]

    clean(root)
    # Path data carries ~6 decimals; one is plenty on a 1700px canvas.
    rounder = lambda m: ("%.1f" % float(m.group(0))).rstrip("0").rstrip(".")
    for el in root.iter():
        for key in ("d", "points"):
            if key in el.attrib:
                el.set(key, re.sub(r"-?\d*\.\d+(?:e-?\d+)?", rounder, el.attrib[key]))
    # Drop style declarations that only restate SVG defaults, and ids nothing references.
    defaults = {"fill-opacity:1", "stroke-opacity:1", "stroke-dasharray:none",
                "stroke-miterlimit:4", "stroke-linecap:butt", "stroke-linejoin:miter"}
    referenced = set(re.findall(r"#([\w-]+)", ET.tostring(root, encoding="unicode")))
    for el in root.iter():
        if "style" in el.attrib:
            decls = [d.strip() for d in el.attrib["style"].split(";") if d.strip()]
            el.set("style", ";".join(d for d in decls if d not in defaults))
        if "id" in el.attrib and el.attrib["id"] not in referenced and el is not root:
            del el.attrib["id"]
    # Artwork bounds measured from a 1:1 render, (58, 29)-(1642, 1947), plus a little padding.
    root.set("viewBox", ATU_VIEWBOX)
    root.set("width", ATU_VIEWBOX.split()[2])
    root.set("height", ATU_VIEWBOX.split()[3])
    tree.write(p("images/edu/atu.min.svg"), encoding="utf-8", xml_declaration=False)
    print("wrote images/edu/atu.min.svg", os.path.getsize(p("images/edu/atu.min.svg")))


ICON_DIR = "vendors/bootstrap-icons-1.11.3"
SPRITE_START, SPRITE_END = "<!-- icons:start -->", "<!-- icons:end -->"


def sprite():
    """Rewrite index.html's inline icon sprite to hold exactly the icons the page and main.js use."""
    page = open(p("index.html"), encoding="utf-8").read()
    script = open(p("js/main.js"), encoding="utf-8").read()  # e.g. the menu's close icon
    names = sorted(set(re.findall(r'<use href="#i-([\w-]+)"', page)) | set(re.findall(r"#i-([\w-]+)", script)))
    symbols = []
    for name in names:
        svg = open(p("%s/%s.svg" % (ICON_DIR, name)), encoding="utf-8").read()
        inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
        inner = re.sub(r"\s*\n\s*", "", inner)
        symbols.append('<symbol id="i-%s" viewBox="0 0 16 16">%s</symbol>' % (name, inner))
    block = '%s\n  <svg xmlns="http://www.w3.org/2000/svg" hidden>\n    %s\n  </svg>\n  %s' % (
        SPRITE_START, "\n    ".join(symbols), SPRITE_END)
    start, end = page.index(SPRITE_START), page.index(SPRITE_END) + len(SPRITE_END)
    page = page[:start] + block + page[end:]
    open(p("index.html"), "w", encoding="utf-8").write(page)
    print("wrote sprite:", len(names), "icons")


def fonts():
    for slug, src in FONTS.items():
        out = "fonts/%s.woff2" % slug
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga", "calt"]
        font = subset.load_font(p(src), opts)
        sub = subset.Subsetter(opts)
        # Basic Latin + Latin-1 (ä in the footer quote) + curly quotes („ “ ’)
        sub.populate(unicodes=list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + list(range(0x2018, 0x201F)))
        sub.subset(font)
        subset.save_font(font, p(out), opts)
        print("wrote", out, os.path.getsize(p(out)))


STEPS = {"hero": hero, "avatar": avatar, "hobbies": hobbies, "certs": certs, "edu": edu,
         "footer": footer_waves, "fonts": fonts, "sprite": sprite}

if __name__ == "__main__":
    # Usage: build_assets.py [step ...]  (default: all steps)
    import sys
    for name in sys.argv[1:] or list(STEPS):
        STEPS[name]()
