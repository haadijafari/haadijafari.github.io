#!/usr/bin/env python3
"""Static checks for hadij.ir.

Usage: python3 tools/check_site.py [-k SUBSTRING]

Each check is a function decorated with @check. It raises AssertionError
with a reason to fail. Prints PASS/FAIL per check; exits 1 on any failure.
"""
import json
import os
import re
import sys
from html import unescape
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKS = []


def check(fn):
    CHECKS.append(fn)
    return fn


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def html():
    return read("index.html")


def css():
    return read("css/base.css") + "\n" + read("css/style.css")


def mainjs():
    return read("js/main.js")


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def _collect(src=None):
    c = _Collector()
    c.feed(src if src is not None else html())
    return c


def tags(name, src=None):
    return [a for t, a in _collect(src).tags if t == name]


def text(src=None):
    src = src if src is not None else html()
    src = re.sub(r"<script\b.*?</script>", " ", src, flags=re.S)
    src = re.sub(r"<style\b.*?</style>", " ", src, flags=re.S)
    return re.sub(r"\s+", " ", " ".join(_collect(src).text))


def section(sid):
    """Raw HTML of <section id="sid"> ... </section> (sections are not nested)."""
    m = re.search(r'<section\b[^>]*\bid="%s"[^>]*>(.*?)</section>' % re.escape(sid), html(), re.S)
    if not m:
        raise AssertionError("no <section id=%r>" % sid)
    return m.group(0)


def classes(attrs):
    return (attrs.get("class") or "").split()


def is_local(url):
    if not url or url.startswith(("#", "data:", "mailto:", "tel:", "javascript:")):
        return False
    return not urlparse(url).scheme and not url.startswith("//")


def local_path(url):
    return os.path.normpath(os.path.join(ROOT, unquote(urlparse(url).path).lstrip("/")))


def size(url):
    return os.path.getsize(local_path(url))


def css_urls(src):
    return [u.strip("'\" ") for u in re.findall(r"url\(([^)]+)\)", src)]


def html_refs():
    refs = []
    for tag, attrs in _collect().tags:
        for key in ("src", "href"):
            if key in attrs:
                refs.append(attrs[key])
        for key in ("srcset",):
            if key in attrs:
                refs += [p.strip().split()[0] for p in attrs[key].split(",") if p.strip()]
        if "style" in attrs:
            refs += css_urls(attrs["style"])
    return refs


def clamp_px(expr, vw):
    """Pixel value of 'clamp(Arem, Brem + Cvw, Drem)' or 'Nrem' at viewport width vw (1rem = 16px)."""
    expr = expr.strip()
    m = re.fullmatch(r"clamp\(\s*(-?[\d.]+)rem,\s*(-?[\d.]+)rem\s*\+\s*([\d.]+)vw,\s*([\d.]+)rem\s*\)", expr)
    if m:
        lo, base, v, hi = (float(g) for g in m.groups())
        return min(max(lo * 16, base * 16 + v * vw / 100), hi * 16)
    m = re.fullmatch(r"([\d.]+)rem", expr)
    assert m, "can't evaluate %r" % expr
    return float(m.group(1)) * 16


def font_faces(src):
    """[(family, [urls])] for each @font-face in src."""
    out = []
    for block in re.findall(r"@font-face\s*{(.*?)}", src, re.S):
        fam = re.search(r"font-family:\s*['\"]?([^;'\"]+)", block)
        out.append((fam.group(1).strip() if fam else "", css_urls(block)))
    return out


def initial_weight():
    total = os.path.getsize(os.path.join(ROOT, "index.html"))
    for a in tags("link"):
        if a.get("rel") == "stylesheet" and is_local(a.get("href")):
            total += size(a["href"])
    for a in tags("script"):
        if is_local(a.get("src")):
            total += size(a["src"])
    for a in tags("img"):
        if a.get("loading") != "lazy" and is_local(a.get("src")):
            total += size(a["src"])
    src = css()
    without_faces = re.sub(r"@font-face\s*{.*?}", "", src, flags=re.S)
    for fam, urls in font_faces(src):
        if fam and re.search(r"font-family:[^;]*%s" % re.escape(fam), without_faces):
            for u in urls:
                total += os.path.getsize(os.path.join(ROOT, "css", u))
    for m in re.finditer(r"#hero[^{]*{([^}]*)}", src):
        for u in css_urls(m.group(1)):
            total += os.path.getsize(os.path.join(ROOT, "css", u))
    return total


# --------------------------------------------------------------- Task 1

@check
def refs_exist():
    missing = [u for u in html_refs() if is_local(u) and not os.path.exists(local_path(u))]
    for name in ("css/base.css", "css/style.css"):
        for u in css_urls(read(name)):
            if is_local(u) and not os.path.exists(os.path.normpath(os.path.join(ROOT, "css", u))):
                missing.append(name + ": " + u)
    assert not missing, "missing: %s" % missing


@check
def weight_budget():
    w = initial_weight()
    assert w <= 250_000, "initial weight %d > 250000" % w


@check
def no_template_leftovers():
    found = [s for s in ("{{", "{%") if s in html()]
    assert not found, "found %s" % found


# --------------------------------------------------------------- Task 2

CERT_SLUGS = ["ml-foundations-duke", "basic-python", "advanced-python", "python-oop",
              "django-basic", "git", "frontend", "c", "ef-set", "odoo"]
HOBBY_SLUGS = ["chess", "martial-arts", "guitar", "learning", "friends"]
KB = 1024
ASSET_CAPS = {
    "images/hero/hadi-600.webp": 70 * KB,
    "images/hero/hadi-1200.webp": 200 * KB,
    "images/og-image.jpg": 200 * KB,
    "images/edu/atu.min.svg": 30 * KB,
    "images/edu/sku.webp": 15 * KB,
    "images/edu/sampad.webp": 15 * KB,
    "fonts/pinyon-script.woff2": 40 * KB,
    "fonts/satisfy.woff2": 40 * KB,
    "fonts/herr-von-muellerhoff.woff2": 40 * KB,
    "images/avatar/me-480.webp": 50 * KB,
    "images/avatar/me-800.webp": 110 * KB,
    "images/svg/footer-waves.svg": 6 * KB,
}
ASSET_CAPS.update({"images/hobbies/%s.webp" % s: 60 * KB for s in HOBBY_SLUGS})
ASSET_CAPS.update({"images/certifications/%s-thumb.webp" % s: 40 * KB for s in CERT_SLUGS})
ASSET_CAPS.update({"images/certifications/%s.webp" % s: 250 * KB for s in CERT_SLUGS})


@check
def assets_generated():
    bad = []
    for path, cap in ASSET_CAPS.items():
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            bad.append(path + " missing")
        elif os.path.getsize(full) > cap:
            bad.append("%s %d > %d" % (path, os.path.getsize(full), cap))
    assert not bad, "; ".join(bad)


# --------------------------------------------------------------- Task 3

@check
def no_dead_libs():
    found = [s for s in ("isotope", "waypoints", "purecounter", "bootstrap.bundle",
                         "bootstrap-icons", "preloader") if s in html().lower()]
    assert not found, "found %s" % found


@check
def icons_defined():
    symbols = {a.get("id") for a in tags("symbol")}
    used = {a.get("href", "").lstrip("#") for a in tags("use")}
    used |= set(re.findall(r"#(i-[\w-]+)", mainjs()))
    missing = sorted(used - symbols)
    assert used, "no <use> icons found"
    assert not missing, "undefined icons: %s" % missing
    assert "bi bi-" not in html(), "font icons (<i class=\"bi bi-...\">) remain"


@check
def fonts_used_only():
    fams = {f for f, _ in font_faces(css())}
    assert fams == {"Pinyon Script", "Satisfy", "Herr Von Muellerhoff"}, "font faces: %s" % sorted(fams)


@check
def no_undefined_fonts():
    found = [f for f in ("Raleway", "Poppins") if f in css()]
    assert not found, "found %s" % found


# --------------------------------------------------------------- Task 4

NAV = ["#hero", "#about", "#projects", "#certifications", "#resume", "#services", "#hobbies"]


@check
def nav_matches_sections():
    m = re.search(r'<nav\b.*?</nav>', html(), re.S)
    assert m, "no <nav>"
    hrefs = [a.get("href") for a in tags("a", m.group(0))]
    assert hrefs == NAV, "nav hrefs %s" % hrefs
    ids = {a.get("id") for a in tags("section")}
    missing = [h for h in NAV if h[1:] not in ids]
    assert not missing, "no <section> for %s" % missing


@check
def no_typos():
    assert "Hobbbies" not in html(), "Hobbbies"


@check
def toggle_is_button():
    t = [(tag, a) for tag, a in _collect().tags if "mobile-nav-toggle" in classes(a)]
    assert t, "no .mobile-nav-toggle"
    tag, a = t[0]
    assert tag == "button" and a.get("aria-label"), "toggle is <%s> %s" % (tag, a)


# --------------------------------------------------------------- Task 5

# Each role carries its own article, so the static prefix is just "I'm".
ROLES = ["a Django Developer", "a Machine Learning Practitioner", "an AI & Soft Computing MSc Student"]
TAGLINE = ("I build clean, well-structured Django back-ends, and I'm bringing the same "
           "discipline to AI and machine learning.")
SOCIAL = ["https://github.com/haadijafari", "https://www.linkedin.com/in/haadijafari/",
          "mailto:haadijafari2003@gmail.com", "https://t.me/haadijafari",
          "https://instagram.com/hadijafari.exe"]


@check
def hero_image():
    imgs = tags("img", section("hero"))
    assert imgs, "no <img> in #hero"
    a = imgs[0]
    srcset = a.get("srcset", "")
    for f in ("images/hero/hadi-600.webp", "images/hero/hadi-1200.webp"):
        assert f in srcset, "srcset lacks %s" % f
    for key in ("sizes", "width", "height", "alt"):
        assert a.get(key), "missing %s" % key
    assert a.get("fetchpriority") == "high", "fetchpriority"
    assert a.get("loading") != "lazy", "hero image is lazy"


@check
def hero_copy():
    typed = [a for a in tags("span", section("hero")) if "typed" in classes(a)]
    assert typed, "no .typed"
    items = [s.strip() for s in typed[0].get("data-typed-items", "").split(",")]
    assert items == ROLES, "typed items %s" % items
    role = re.search(r'<p class="hero-role">\s*(.*?)<span', section("hero"), re.S)
    assert role and role.group(1).strip() == "I'm", "static role prefix %r" % (role and role.group(1))
    t = text(section("hero"))
    assert "Hadi Jafari" in t, "name"
    assert TAGLINE in t, "tagline"


@check
def social_links_exact():
    hrefs = [a.get("href", "") for a in tags("a")]
    bad = [h for h in hrefs if re.search(r"x\.com|twitter|wa\.me|^tel:", h)]
    assert not bad, "forbidden links %s" % bad
    for h in hrefs:
        if "instagram.com" in h:
            assert h == SOCIAL[4], "instagram %s" % h
        if "linkedin.com" in h:
            assert h == SOCIAL[1], "linkedin %s" % h
        if "t.me/" in h:
            assert h == SOCIAL[3], "telegram %s" % h
    pills = re.findall(r'<ul class="social-pills".*?</ul>', html(), re.S)
    assert pills, "no .social-pills"
    for block in pills:
        got = [a.get("href") for a in tags("a", block)]
        assert got == SOCIAL, "pills %s" % got


@check
def reduced_motion_typed():
    js = mainjs()
    i, j = js.find("prefers-reduced-motion"), js.find("new Typed(")
    assert i != -1 and j != -1 and i < j, "Typed not gated on prefers-reduced-motion"


# --------------------------------------------------------------- Task 6

ABOUT_HEADING = "Django Developer → AI & Machine Learning"
ABOUT_P1 = ("I'm a back-end developer who cares a lot about structure: clear architecture, "
            "readable code, and systems that are easy to grow. I've spent the last few years "
            "building web applications with Django, and I'm still building with it today.")
ABOUT_P2 = ("After finishing my BSc in Computer Science at Shahrekord University, I started a "
            "master's in AI & Soft Computing at Allameh Tabataba'i University. I'm now applying "
            "the same engineering habits to machine learning, from leak-free pipelines to models "
            "that hold up outside a notebook.")
SKILLS = {
    "Back-end": ["Python", "Django", "Django REST Framework", "SQL"],
    "AI & ML": ["scikit-learn", "NumPy", "pandas", "Jupyter", "Streamlit"],
    "DevOps & Tools": ["Docker", "Git & GitHub", "Linux", "DVC", "uv"],
    "Front-end": ["HTML", "CSS", "Bootstrap", "JavaScript"],
}


@check
def about_copy():
    t = text(section("about"))
    assert ABOUT_HEADING not in t, "old subheading still shown"
    for s in (ABOUT_P1, ABOUT_P2):
        assert s in t, "missing: %s" % s[:50]


@check
def info_list():
    sec = section("about")
    t = text(sec)
    assert "Isfahan, Iran" in t, "location"
    assert "Available" in t, "freelance"
    assert 'href="mailto:haadijafari2003@gmail.com"' in sec, "mailto"
    for bad in ("Persia", "Unknown", "Phone"):
        assert bad not in t, "found %s" % bad


@check
def no_inflated_stats():
    sec = section("about")
    t = text(sec)
    for bad in ("100", "Awards", "Coffee", "∞", "Years of Experience"):
        assert bad not in t, "found %s" % bad
    for good in ("3+", "17.57", "MSc"):
        assert good in t, "missing %s" % good
    assert 'id="cert-count"' in sec, "no #cert-count"


@check
def no_percent_bars():
    sec = section("about")
    assert "progress-bar" not in sec, "progress bars"
    assert "%" not in text(sec), "percentages"


@check
def skills_groups():
    t = text(section("about"))
    for group, tools in SKILLS.items():
        assert group in t, "group %s" % group
        for tool in tools:
            assert tool in t, "tool %s" % tool


@check
def no_nowrap_overflow():
    assert "text-nowrap" not in section("about"), "text-nowrap in #about"


# --------------------------------------------------------------- Task 7

PROJECTS = [
    ("Tehran House Price Prediction", "https://github.com/haadijafari/House-Price-Prediction"),
    ("Tetris AI", "https://github.com/haadijafari/Tetris_AI"),
    ("Persian Character Recognizer", "https://github.com/haadijafari/Alphabet-Recognition"),
]


@check
def projects():
    sec = section("projects")
    cards = re.findall(r'<article class="project-card".*?</article>', sec, re.S)
    assert len(cards) == 3, "%d project cards" % len(cards)
    for (title, url), card in zip(PROJECTS, cards):
        assert title in text(card), "title %s" % title
        assert url in [a.get("href") for a in tags("a", card)], "link %s" % url
    assert "R² 0.822" in text(cards[0]), "R² 0.822 missing"


# --------------------------------------------------------------- Task 8

def cert_cards():
    return [a for a in tags("a", section("certifications")) if "cert-card" in classes(a)]


@check
def cert_desc_unique():
    sec = section("certifications")
    refs = re.findall(r"description:\s*\.(desc\d+)", sec)
    assert refs, "no lightbox descriptions"
    dup = sorted({r for r in refs if refs.count(r) > 1})
    assert not dup, "descN used by several cards: %s" % dup
    for r in refs:
        n = len(re.findall(r'class="glightbox-desc %s"' % r, sec))
        assert n == 1, "%s defined %d times" % (r, n)


@check
def cert_count_fallback_matches():
    m = re.search(r'id="cert-count">(\d+)<', html())
    assert m, "no #cert-count number"
    n = len([a for a in tags("a", section("certifications")) if "certifications-lightbox" in classes(a)])
    assert int(m.group(1)) == n, "fallback %s != %d certificates" % (m.group(1), n)


@check
def cert_new():
    cards = cert_cards()
    assert cards and "ml-foundations-duke" in cards[0].get("href", ""), "first card is not the Duke ML certificate"
    assert "https://coursera.org/verify/6DB82NPQSW6L" in section("certifications"), "verify link"


@check
def cert_efset_title():
    ef = [a for a in tags("a", section("certifications")) if a.get("href", "").endswith("/ef-set.webp")]
    assert ef and "title: English: EF SET C2 Proficient;" in ef[0].get("data-glightbox", ""), "EF SET title"


@check
def imgs_lazy_sized():
    bad = []
    hero = section("hero")
    for a in tags("img"):
        if a.get("src") and a["src"] in hero:
            continue
        missing = [k for k in ("width", "height") if not a.get(k)]
        if "alt" not in a:  # alt="" is fine for decorative images
            missing.append("alt")
        if a.get("loading") != "lazy":
            missing.append("loading=lazy")
        if missing:
            bad.append("%s: %s" % (a.get("src"), missing))
    assert not bad, "; ".join(bad)


# --------------------------------------------------------------- Task 9

JALALI = re.compile(r"\b1[34]\d\d – (?:1[34]\d\d|Now)\b")


@check
def jalali_only_in_resume():
    page = html()
    assert not re.search(r"[۰-۹]|اکنون", page), "Persian digits or اکنون on the page"
    dates = re.findall(r'<p class="resume-date">.*?</p>', section("resume"), re.S)
    assert len(dates) == 5 and all(JALALI.search(text(d)) for d in dates), "resume dates lack Jalali years"
    outside = re.sub(r'<p class="resume-date">.*?</p>', "", page, flags=re.S)
    found = JALALI.findall(text(outside))
    assert not found, "Jalali years outside resume dates: %s" % found


@check
def resume_content():
    t = text(section("resume"))
    for s in ("Co-founder & CTO", "Vira Kavane Zista", "17.57 / 20", "Allameh Tabataba'i",
              "Shahrekord University", "C2 Proficient", "EF SET 76/100", "Native"):
        assert s in t, "missing %s" % s
    for bad in ("German", "Shahr-e Kord", "two years"):
        assert bad not in html(), "found %s" % bad


@check
def newest_first():
    t = text(section("resume"))
    order = [t.find(s) for s in ("Co-founder & CTO", "Django Back-end Developer")]
    assert -1 not in order and order == sorted(order), "experience order %s" % order
    order = [t.find(s) for s in ("MSc", "BSc", "Diploma")]
    assert -1 not in order and order == sorted(order), "education order %s" % order


# --------------------------------------------------------------- Task 10

SERVICES = ["Web Applications", "API Development", "E-Commerce Solutions",
            "Data Analysis & Visualization", "AI & Machine Learning", "Architecture & Refactoring"]
REFACTOR_DESC = ("Restructuring messy or growing Django codebases into clean, maintainable "
                 "architecture, so new features stop breaking old ones.")


@check
def services():
    sec = section("services")
    cards = re.findall(r'<div class="card service-card">.*?</div>', sec, re.S)
    assert len(cards) == 6, "%d service cards" % len(cards)
    titles = [text(c).strip() for c in re.findall(r"<h3>.*?</h3>", sec, re.S)]
    assert titles == SERVICES, "titles %s" % titles
    assert REFACTOR_DESC in text(sec), "refactoring description"
    assert "Automation" not in sec, "Automation still listed"


# --------------------------------------------------------------- Task 11

HOBBIES = ["Chess", "Martial Arts & Workout", "Guitar", "Learning", "Friends"]


@check
def hobbies_content():
    sec = section("hobbies")
    caps = [text(c).strip() for c in re.findall(r"<figcaption>.*?</figcaption>", sec, re.S)]
    assert caps == HOBBIES, "captions %s" % caps
    n = len([a for a in tags("figure", sec) if "polaroid" in classes(a)])
    assert n == 5, "%d polaroids" % n
    for bad in ("belt", "accordion"):
        assert bad not in sec.lower(), "found %s" % bad


@check
def deck_a11y():
    sec = section("hobbies")
    btn = [a for a in tags("button", sec) if "deck-shuffle" in classes(a)]
    assert btn and btn[0].get("aria-label"), "no labelled .deck-shuffle button"
    live = [a for t, a in _collect(sec).tags if "deck-text" in classes(a)]
    assert live and live[0].get("aria-live"), "no aria-live .deck-text"


@check
def reduced_motion_deck():
    blocks = re.findall(r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*{(.*?)}\s*}", css(), re.S)
    assert any(".polaroid" in b and "transition: none" in b for b in blocks), \
        "no reduced-motion rule turning off .polaroid transitions"


# --------------------------------------------------------------- Task 12

QUOTE = "„Ich habe gelitten, gelernt und mich verändert“"


@check
def footer():
    m = re.search(r"<footer\b.*?</footer>", html(), re.S)
    assert m, "no <footer>"
    f = m.group(0)
    pills = re.findall(r'<ul class="social-pills".*?</ul>', f, re.S)
    assert pills and [a.get("href") for a in tags("a", pills[0])] == SOCIAL, "footer pills"
    assert '<span id="year">2026</span>' in f, "year span"
    assert QUOTE in text(f), "German quote"
    assert "translate.google" not in f, "Google Translate link"
    assert "© 2023–" in text(f), "copyright years"
    assert "footer-top.svg" not in html(), "footer-top.svg"


@check
def no_jokey_intros():
    for s in ("Don't you know who I am", "missing piece of puzzle", "People have hobbies",
              "Services I can provide you", "I've attended in some courses"):
        assert s not in html(), "found: %s" % s


# --------------------------------------------------------------- Task 13

def jsonld_graph_nodes():
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html(), re.S)
    assert m, "no JSON-LD"
    return json.loads(m.group(1))["@graph"]


def jsonld_data():
    people = [n for n in jsonld_graph_nodes() if n.get("@type") == "Person"]
    assert len(people) == 1, "%d Person nodes" % len(people)
    return people[0]


@check
def jsonld():
    d = jsonld_data()
    assert d.get("sameAs") == [SOCIAL[0], SOCIAL[1], SOCIAL[3], SOCIAL[4]], "sameAs %s" % d.get("sameAs")
    assert d.get("knowsLanguage") == ["English", "Persian"], "knowsLanguage"
    assert (d.get("worksFor") or {}).get("name") == "Vira Kavane Zista", "worksFor"
    alumni = [a.get("name") for a in d.get("alumniOf", [])]
    assert "Shahrekord University" in alumni, "alumniOf %s" % alumni
    aff = d.get("affiliation") or {}
    aff = aff if isinstance(aff, list) else [aff]
    assert any(a.get("name") == "Allameh Tabataba'i University" for a in aff), "affiliation"


@check
def og_meta():
    metas = {a.get("property") or a.get("name"): a.get("content", "") for a in tags("meta")}
    assert metas.get("og:image") == "https://hadij.ir/images/og-image.jpg", "og:image"
    for key in ("og:title", "og:description", "description"):
        assert "Django" in metas.get(key, "") and "AI" in metas.get(key, ""), "%s lacks Django/AI" % key
    title = re.search(r"<title>(.*?)</title>", html()).group(1)
    assert "Django" in title and "AI" in title, "title %s" % title


@check
def sitemap():
    s = read("sitemap.xml")
    assert re.findall(r"<loc>([^<]+)</loc>", s) == ["https://hadij.ir/"], "sitemap must list only https://hadij.ir/"
    assert re.search(r"<lastmod>\d{4}-\d\d-\d\d</lastmod>", s), "no lastmod"
    assert "<priority>" not in s, "priority is ignored; drop it"


# ------------------------------------------------------- Final review fixes

# sha256 of the lowercased name of Hadi's unlaunched product; the name itself must
# not appear anywhere in this public repo, including this file.
SECRET_HASHES = {"ade81d6368a5434490075a17dc384e213ff48aa931b194448105add6541de693"}
PUBLIC_TEXT = ["index.html", "sitemap.xml", "README.md", "CLAUDE.md", "css", "js", "tools", "docs"]


def secret_hits():
    import hashlib
    hits = []
    for top in PUBLIC_TEXT:
        full = os.path.join(ROOT, top)
        paths = [full] if os.path.isfile(full) else [
            os.path.join(dp, f) for dp, _, fs in os.walk(full) if "__pycache__" not in dp for f in fs]
        for path in paths:
            try:
                words = set(re.findall(r"\w+", open(path, encoding="utf-8").read().lower()))
            except (UnicodeDecodeError, FileNotFoundError):
                continue
            if any(hashlib.sha256(w.encode()).hexdigest() in SECRET_HASHES for w in words):
                hits.append(os.path.relpath(path, ROOT))
    return hits


@check
def no_secret_name():
    assert not secret_hits(), "secret product named in %s" % secret_hits()


@check
def drawer_hidden_when_closed():
    src = css()
    mobile = re.search(r"@media \(max-width: 991\.98px\) {(.*?)\n}", src, re.S)
    assert mobile, "no mobile nav media block"
    block = mobile.group(1)
    assert re.search(r"#header\s*{[^}]*visibility:\s*hidden", block), "closed drawer not visibility:hidden"
    assert re.search(r"\.mobile-nav-active #header\s*{[^}]*visibility:\s*visible", block), "open drawer not visible"
    assert '"Escape"' in mainjs(), "Escape does not close the menu"


@check
def hero_original_not_published():
    import subprocess
    r = subprocess.run(["git", "check-ignore", "-q", "images/hero/IMG_0154.jpg"], cwd=ROOT)
    assert r.returncode == 0, "images/hero/IMG_0154.jpg is not git-ignored"


@check
def font_glyphs_cover_text():
    from fontTools.ttLib import TTFont
    needs = {
        "fonts/satisfy.woff2": text(re.search(r'<p class="footer-quote".*?</p>', html(), re.S).group(0))
        + "".join(text(c) for c in re.findall(r"<figcaption>.*?</figcaption>", html(), re.S)),
        "fonts/pinyon-script.woff2": text(re.search(r"<h1>.*?</h1>", section("hero"), re.S).group(0)),
    }
    for font, txt in needs.items():
        cmap = TTFont(os.path.join(ROOT, font)).getBestCmap()
        missing = sorted({ch for ch in txt if not ch.isspace() and ord(ch) not in cmap})
        assert not missing, "%s lacks %s" % (font, missing)


# ------------------------------------------------- Hadi's feedback, round 1

@check
def footer_waves():
    i, j = html().find("footer-waves.svg"), html().find('<footer id="footer"')
    assert 0 < i < j, "no footer-waves.svg divider right before the footer"
    divider = [a for a in tags("img") if "footer-waves.svg" in a.get("src", "")]
    assert divider[0].get("alt") == "", "divider should be decorative (alt=\"\")"


@check
def title_watermarks():
    titles = re.findall(r'<div class="section-title">.*?</div>', html(), re.S)
    assert len(titles) == 6, "%d section titles" % len(titles)
    for t in titles:
        marks = [a for a in tags("span", t) if "title-watermark" in classes(a)]
        assert marks and marks[0].get("aria-hidden") == "true", "title without aria-hidden watermark: %s" % text(t)[:30]
    rule = re.search(r"\.title-watermark\s*{([^}]*)}", css())
    assert rule, "no .title-watermark rule"
    font = re.search(r"font-family:\s*([^;]+);", rule.group(1)).group(1)
    var = re.match(r"var\((--[\w-]+)\)", font)
    if var:
        font = re.search(r"%s:\s*([^;]+);" % var.group(1), css()).group(1)
    assert "Herr Von Muellerhoff" in font, "watermark font is %s" % font


@check
def services_hover():
    rule = re.search(r"\.service-card:hover\s*{([^}]*)}", css())
    assert rule and "background" in rule.group(1), "no background change on service hover"


@check
def about_photo():
    imgs = tags("img", section("about"))
    assert imgs and "images/avatar/me-" in imgs[0].get("src", "") and imgs[0]["src"].endswith(".webp"), \
        "no WebP portrait in #about"


@check
def hero_calm():
    assert "social-pills" not in section("hero"), "social pills in the hero"
    hero_css = "".join(re.findall(r"#hero[^{]*{[^}]*}", css()))
    assert "radial-gradient" not in hero_css, "purple glow on the hero photo"


@check
def section_titles_classic():
    # Hadi's original look: centered, big heavy purple heading, no underline bar
    rule = re.search(r"\.section-title\s*{([^}]*)}", css())
    assert rule and "text-align: center" in rule.group(1), "section titles not centered"
    h2 = re.search(r"\.section-title h2\s*{([^}]*)}", css())
    assert h2, "no .section-title h2 rule"
    assert "font-weight: 900" in h2.group(1), "title not weight 900"
    assert re.search(r"color:\s*var\(--c-primary\)", h2.group(1)), "title not purple"
    assert ".section-title h2::after" not in css(), "underline bar under the title"


# ------------------------------------------------- About redesign

@check
def watermark_size_phone():
    wm = re.search(r"\.section-title \.title-watermark\s*{[^}]*font-size:\s*([^;]+);", css()).group(1)
    h2 = re.search(r"\.section-title h2\s*{[^}]*font-size:\s*([^;]+);", css()).group(1)
    ratio = clamp_px(wm, 360) / clamp_px(h2, 360)
    assert ratio >= 2.3, "watermark only %.2fx the title at 360px" % ratio
    assert clamp_px(wm, 1280) == 160, "desktop watermark %spx, want 10rem" % clamp_px(wm, 1280)


@check
def about_profile():
    sec = section("about")
    imgs = tags("img", sec)
    assert "profile-photo" in classes(imgs[0]), "first #about image is not .profile-photo"
    assert '<div class="profile-ring">' in sec, "no story ring"
    assert re.search(r'<h3 class="profile-name">Hadi Jafari</h3>', sec), "name"
    tag_block = re.search(r'<ul class="profile-tags".*?</ul>', sec, re.S)
    got = [unescape(s.strip()) for s in re.findall(r"</svg>([^<]+)</li>", tag_block.group(0))] if tag_block else []
    assert got == ["Co-founder & CTO, Vira Kavane Zista", "Isfahan, Iran"], "tags %s" % got
    assert "Soft Computing Student" not in text(sec), "student tag under the avatar"


@check
def about_details():
    sec = section("about")
    dl = re.search(r'<dl class="about-details">.*?</dl>', sec, re.S)
    assert dl, "no dl.about-details"
    dl = dl.group(0)
    labels = [s.strip() for s in re.findall(r"</svg>([^<]+)</dt>", dl)]
    assert labels == ["Birthday", "Degree", "Email", "Freelance"], "labels %s" % labels
    icons = re.findall(r'<dt><svg class="icon"[^>]*><use href="#i-([\w-]+)"', dl)
    assert icons == ["calendar3", "mortarboard", "envelope", "laptop"], "icons %s" % icons
    assert re.search(r'April 2003 (<span class="muted">)?\(<span id="age">23</span> years\)', dl), "birthday line with #age inside"
    assert "<dt>Age" not in dl and ">Age<" not in dl, "separate Age row"
    t = text(dl)
    assert "BSc Computer Science" in t and "MSc AI & Soft Computing" in t, "degree lines"
    assert re.search(r'<span class="[^"]*\bmuted\b[^"]*">\(in progress\)</span>', dl), "(in progress) not muted"
    assert re.search(r'<div class="desk-only"><dt><svg[^>]*><use href="#i-envelope"/></svg>Email</dt>', dl), "Email row not desk-only"
    assert 'class="hire-link" href="mailto:haadijafari2003@gmail.com?subject=Freelance%20project">Contact me</a>' in dl, "hire link"
    assert re.search(r"\.desk-only\s*{\s*display:\s*none;", css()), "desk-only not hidden on phones"
    assert re.search(r"@media \(min-width: 992px\)\s*{[^@]*\.desk-only\s*{\s*display:", css()), "desk-only not shown on desktop"


SOCIAL_LABELS = ["GitHub", "LinkedIn", "Gmail", "Telegram", "Instagram"]
SOCIAL_ICONS = ["#i-github", "#i-linkedin", "#b-gmail", "#i-telegram", "#b-instagram"]


@check
def about_numbers():
    block = re.search(r'<div class="about-numbers">.*?(?=<ul class="about-socials")', section("about"), re.S)
    assert block, "no .about-numbers"
    nums = re.findall(r"<strong[^>]*>([^<]+)</strong>", block.group(0))
    assert nums[:2] == ["3+", "17.57"] and len(nums) == 3, "numbers %s" % nums
    assert 'id="cert-count"' in block.group(0), "certificates number is not #cert-count"
    assert "MSc" not in text(block.group(0)), "MSc tile still there"


@check
def about_socials():
    ul = re.search(r'<ul class="about-socials".*?</ul>', section("about"), re.S)
    assert ul, "no ul.about-socials"
    links = tags("a", ul.group(0))
    assert [a.get("href") for a in links] == SOCIAL, "hrefs %s" % [a.get("href") for a in links]
    labels = re.findall(r'<span class="social-label">([^<]+)</span>', ul.group(0))
    assert labels == SOCIAL_LABELS, "labels %s" % labels
    assert [a.get("href") for a in tags("use", ul.group(0))] == SOCIAL_ICONS, "icons"
    for a in links:
        if a["href"].startswith("http"):
            assert a.get("target") == "_blank" and a.get("rel") == "noopener", a["href"]


@check
def brand_icons():
    block = re.search(r"<!-- brand-icons:start.*?-->(.*?)<!-- brand-icons:end -->", html(), re.S)
    assert block, "no brand-icons block"
    svg = tags("svg", block.group(1))[0]
    assert "hidden" not in svg and "display" not in svg.get("style", ""), "display:none breaks the gradients"
    assert svg.get("width") == "0" and svg.get("height") == "0", "hide the block by size"
    gm = re.search(r'<symbol id="b-gmail".*?</symbol>', block.group(1), re.S).group(0).lower()
    for c in ("#4285f4", "#34a853", "#fbbc04", "#ea4335", "#c5221f"):
        assert c in gm, "gmail lacks %s" % c
    ig = re.search(r'<symbol id="b-instagram".*?</symbol>', block.group(1), re.S).group(0)
    grad = re.search(r'fill="url\(#([\w-]+)\)"', ig)
    assert grad and ('id="%s"' % grad.group(1)) in block.group(1), "instagram gradient undefined"


@check
def contact_landing():
    sec = section("about")
    assert html().count('id="contact"') == 1, "id=contact count"
    reach = re.search(r'<div class="about-contact" id="contact" data-scroll="center">(.*?)</ul>', sec, re.S)
    assert reach and "about-socials" in reach.group(1), "#contact does not wrap the socials"
    js = mainjs()
    assert 'block: "center"' in js, "no centered scroll"
    assert re.search(r'reduceMotion \? "instant" : "smooth"', js), "scroll ignores reduced motion"
    assert re.search(r"prefers-reduced-motion: reduce\)\s*{\s*html\s*{\s*scroll-behavior:\s*auto", css()), "CSS smooth scroll not gated"


@check
def intro_toggle():
    sec = section("about")
    assert '<div class="about-intro" id="about-intro">' in sec, "intro must ship expanded (no JS = full text)"
    btn = re.search(r"<button[^>]*\bintro-toggle\b[^>]*>Read more</button>", sec)
    assert btn, "no Read more button"
    for attr in ('type="button"', 'aria-expanded="false"', 'aria-controls="about-intro"', " hidden"):
        assert attr in btn.group(0), "button lacks %s" % attr.strip()
    js = mainjs()
    for s in ('"Show less"', '"Read more"', '"aria-expanded"', "(min-width: 992px)", "is-collapsed"):
        assert s in js, "main.js lacks %s" % s
    assert re.search(r"\.about-intro\.is-collapsed\s*{[^}]*max-height", css()), "no collapsed height"
    desk = re.findall(r"@media \(min-width: 992px\)\s*{(.*?)\n}", css(), re.S)
    assert any(".intro-toggle" in b and "is-collapsed" in b for b in desk), \
        "desktop must undo the collapse and hide the button"


@check
def skills_divider():
    sec = section("about")
    assert '<h3 class="about-divider">Skills</h3>' in sec, "no Skills divider heading"
    assert ".about-divider::before" in css() and ".about-divider::after" in css(), "divider lines"


@check
def about_old_removed():
    sec, c = section("about"), css()
    for cls in ("about-top", "about-photo", "info-list", "contact-card", 'class="facts"', "about-subtitle"):
        assert cls not in sec, "old markup %s" % cls
    for sel in (".about-top", ".about-photo", ".info-list", ".contact-card", ".about .fact", ".about-subtitle"):
        assert sel not in c, "dead CSS %s" % sel


@check
def about_desktop_grid():
    desk = "\n".join(re.findall(r"@media \(min-width: 992px\)\s*{(.*?)\n}", css(), re.S))
    m = re.search(r"\.about \.about-profile\s*{([^}]*)}", desk)
    assert m and "grid-template-columns: 320px minmax(0, 1fr)" in m.group(1), "no two-column desktop profile"
    m = re.search(r"\.about \.skills\s*{([^}]*)}", desk)
    assert m and "repeat(4, minmax(0, 1fr))" in m.group(1), "skills not four columns on desktop"


@check
def socials_not_spread_on_tablets():
    # Hadi: circles too far apart on wide screens; tablets get the phone layout, so cap the row
    rule = re.search(r"\.about \.about-socials\s*{([^}]*)}", css())
    assert rule and re.search(r"max-width:\s*\d+", rule.group(1)) and "margin: 0 auto" in rule.group(1), \
        "social row not capped and centered"


@check
def details_one_per_row_on_phones():
    rule = re.search(r"\.about \.about-details\s*{([^}]*)}", css())
    assert rule and "grid-template-columns: 1fr;" in rule.group(1), "details not one per row on phones"
    desk = "\n".join(re.findall(r"@media \(min-width: 992px\)\s*{(.*?)\n}", css(), re.S))
    m = re.search(r"\.about \.about-details\s*{([^}]*)}", desk)
    assert m and "repeat(2, minmax(0, 1fr))" in m.group(1), "details not 2 x 2 on desktop"


@check
def about_hover_effects():
    for sel in (r"\.about \.profile-tag:hover", r"\.about \.skill-group \.tag:hover"):
        rule = re.search(sel + r"\s*{([^}]*)}", css())
        assert rule and "border-color" in rule.group(1) and "background" in rule.group(1), "no hover on %s" % sel
    for sel in (r"\.about \.profile-tag", r"\.about \.skill-group \.tag"):
        rule = re.search(sel + r"\s*{([^}]*)}", css())
        assert rule and "cursor: default" in rule.group(1), "text cursor on %s" % sel


# --------------------------------------------------- SEO & cleanup

JUNK = [
    "vendors/bootstrap-5.3.3-dist/js", "vendors/bootstrap-5.3.3-dist/css/bootstrap.min.css.map",
    "vendors/glightbox/css/plyr.css", "vendors/glightbox/css/plyr.min.css",
    "vendors/glightbox/css/glightbox.css", "vendors/glightbox/js/glightbox.js",
    "vendors/typed.js/typed.js", "vendors/typed.js/typed.min.js.map",
    "images/hero/hero-bg-mobile.jpg", "images/hero/hero-bg.jpg", "images/hero/hero-bg_001.jpg",
    "images/hero/hero-bg_001.jpg~", "images/hero/hero-bg_0012.jpg", "images/avatar/me2.jpg",
    "images/portfolio", "images/main", "images/favicon/index-about-social.html",
    "images/svg/about-social-divider-bottom.svg", "images/svg/about-social-divider-top.svg",
    "images/svg/devider.svg", "images/svg/hero-bottom.svg", "images/svg/hobby.svg",
    "images/svg/portfolio-single-footer.svg", "images/svg/portfolio-single-header.svg",
    "images/svg/resume-bg.svg",
] + ["images/hobbies/" + f for f in (
    "book1.jpg", "book2.jpg", "chess1.jpg", "friends1.jpg", "music2.webp",
    "psycho1.jpg", "psycho2.jpg", "default.webp", "default_back.jpg")] + ["fonts/" + f for f in (
    "Arizonia-Regular.ttf", "DancingScript-VariableFont_wght.ttf",
    "GreatVibes-Regular.ttf", "Niconne-Regular.ttf")] + [
    "resume.pdf", "resume/Resume.pdf", "resume/resume.pdf", "resume/Docs/Hadi_Jafari.pdf",
    "docs/superpowers/plans/2026-10-21-cleanup-candidates.md",
] + ["resume/Docs/" + f for f in (
    "Advanced_Python.png", "Basic_Python.png", "Django.png", "Git.png",
    "OOP_Python.png", "Web Development_Front-end.png")] + ["vendors/bootstrap-5.3.3-dist"]

UNPUBLISHED = ["docs", "tools", "CLAUDE.md", "README.md", "resume/CV.odt",
               "resume/logos", "resume/Docs", "vendors/bootstrap-icons-1.11.3"]


@check
def no_junk_files():
    left = [p for p in JUNK if os.path.exists(os.path.join(ROOT, p))]
    assert not left, "still present: %s" % left


@check
def publish_hygiene():
    assert "__pycache__/" in read(".gitignore").split("\n"), "__pycache__ not ignored"
    assert not os.path.exists(os.path.join(ROOT, ".nojekyll")), ".nojekyll disables _config.yml exclude"
    cfg = read("_config.yml")
    excluded = re.findall(r"^\s*-\s*\"?([^\"\n]+?)\"?\s*$", cfg, re.M)
    missing = [p for p in UNPUBLISHED if p not in excluded]
    assert re.search(r"^exclude:", cfg, re.M) and not missing, "not excluded: %s" % missing
    for p in ("resume/hadi_jafari_resume.pdf", "images/certifications/EF-SET-Certificate.pdf",
              "images/certifications/BTCO-Certificate.pdf", "images/svg/footer-top.svg"):
        assert os.path.exists(os.path.join(ROOT, p)), "needed file deleted: %s" % p


SITE = "https://hadij.ir/"


def metas():
    return {a.get("property") or a.get("name"): a.get("content", "") for a in tags("meta")}


@check
def head_meta():
    m = metas()
    canon = [a["href"] for a in tags("link") if a.get("rel") == "canonical"]
    assert canon == [SITE], "canonical %s" % canon
    assert m.get("og:url") == SITE, "og:url %s" % m.get("og:url")
    expect = {"og:type": "profile", "og:site_name": "Hadi Jafari", "og:locale": "en_US",
              "profile:first_name": "Hadi", "profile:last_name": "Jafari",
              "theme-color": "#0b0b0f", "twitter:image": SITE + "images/og-image.jpg"}
    bad = {k: m.get(k) for k, v in expect.items() if m.get(k) != v}
    assert not bad, "wrong meta %s" % bad
    for k in ("og:image:alt", "twitter:title", "twitter:description", "twitter:image:alt"):
        assert m.get(k), "missing %s" % k
    assert m["twitter:title"] == m["og:title"] and m["twitter:description"] == m["og:description"], "twitter != og"
    assert "keywords" not in m, "meta keywords is ignored by Google; drop it"
    icons = {(a.get("rel"), a.get("href")) for a in tags("link")}
    assert ("icon", "images/favicon/favicon.ico") in icons, "favicon.ico not linked"
    assert ("icon", "images/favicon/android-chrome-192x192.png") in icons, "no 48px-multiple PNG icon"


@check
def manifest():
    d = json.loads(read("images/favicon/site.webmanifest"))
    assert d.get("name") == "Hadi Jafari" and d.get("short_name") == "Hadi Jafari", "names"
    assert d.get("theme_color") == "#0b0b0f" and d.get("background_color") == "#0b0b0f", "colors"
    assert d.get("start_url") == "/", "start_url"
    for icon in d["icons"]:
        path = os.path.normpath(os.path.join(ROOT, "images/favicon", icon["src"]))
        assert os.path.exists(path), "manifest icon 404: %s" % icon["src"]


@check
def jsonld_graph():
    nodes = jsonld_graph_nodes()
    ids = {n["@id"] for n in nodes}
    assert {n["@type"] for n in nodes} == {"WebSite", "ProfilePage", "Person"}, "node types"
    refs = re.findall(r'\{"@id":\s*"([^"]+)"\}', json.dumps(nodes))
    assert refs and all(r in ids for r in refs), "dangling @id refs %s" % [r for r in refs if r not in ids]
    page = next(n for n in nodes if n["@type"] == "ProfilePage")
    assert page["url"] == SITE and page["mainEntity"] == {"@id": SITE + "#person"}, "ProfilePage"
    p = jsonld_data()
    assert p["@id"] == SITE + "#person" and p["url"] == SITE, "Person id/url"
    assert p.get("alternateName") == "هادی جعفری", "alternateName"


@check
def not_found_page():
    page = read("404.html")
    robots = [a.get("content") for a in tags("meta", page) if a.get("name") == "robots"]
    assert robots == ["noindex"], "404 must be noindex"
    refs = [a.get(k) for t, a in _collect(page).tags for k in ("href", "src") if a.get(k)]
    rel = [r for r in refs if is_local(r) and not r.startswith("/")]
    assert not rel, "relative refs break at nested 404 URLs: %s" % rel
    assert any(a.get("href") == "/" for a in tags("a", page)), "no link home"
    for r in refs:
        if is_local(r):
            assert os.path.exists(local_path(r)), "404 ref missing: %s" % r


@check
def no_bootstrap():
    # the Front-end skills list mentions "Bootstrap" as text, so only check what the page loads
    loaded = [a.get("href") or a.get("src") or "" for a in tags("link") + tags("script")]
    assert not [u for u in loaded if "bootstrap" in u.lower()], "Bootstrap still linked"
    assert "data-bs-theme" not in html(), "data-bs-theme is meaningless without Bootstrap"
    assert re.search(r":root\s*{[^}]*color-scheme:\s*dark", css()), "no color-scheme: dark"
    for cls in (".container", ".d-flex", ".d-lg-none", ".flex-column", ".justify-content-center",
                ".align-items-center", ".visually-hidden"):
        assert re.search(re.escape(cls) + r"\s*[{,]", css()), "utility %s not defined" % cls


# ------------------------------------------------------------------ main

def main(argv):
    k = None
    if len(argv) >= 2 and argv[0] == "-k":
        k = argv[1]
    failed = 0
    for fn in CHECKS:
        if k and k not in fn.__name__:
            continue
        try:
            fn()
            print("PASS", fn.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL %s: %s" % (fn.__name__, e))
        except Exception as e:  # a broken check is a failure, not a crash
            failed += 1
            print("FAIL %s: %s: %s" % (fn.__name__, type(e).__name__, e))
    if k and not any(k in fn.__name__ for fn in CHECKS):
        print("no checks match %r" % k)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
