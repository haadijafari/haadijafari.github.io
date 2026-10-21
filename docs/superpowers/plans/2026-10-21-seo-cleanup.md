# SEO, Optimization & Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every SEO, performance, correctness and repo-hygiene issue found in the 2026-10-21 repository review, so the redesign can be committed and published cleanly.

**Architecture:** Plain static site, no build step. Every change is to `index.html`, `css/base.css`, `js/main.js`, the root SEO files, or the repo layout. `tools/check_site.py` is the test suite: each requirement becomes an `@check` function, written first, seen failing, then made to pass.

**Tech Stack:** HTML/CSS/vanilla JS, GitHub Pages (Jekyll on, used only for its `exclude` list), Python 3 for `tools/check_site.py`, headless Firefox via `tools/screens.sh` for visual checks.

**Spec:** The review in this session (no separate spec file). Its findings, with the two corrections below, are the requirements.
- Correction 1: `images/svg/footer-top.svg` is the source `build_assets.py footer` reads. Keep it.
- Correction 2: `images/certifications/EF-SET-Certificate.png` and `EF-SET-Certificate-min.jpg` are sources for the `ef-set` cert. Keep them.

## Global Constraints

- Site URL is exactly `https://hadij.ir/` (with trailing slash) everywhere: canonical, `og:url`, JSON-LD `url`, sitemap.
- Theme color everywhere is `#0b0b0f` (the `--c-bg` token).
- Nothing loads from a CDN. All assets stay in the repo.
- Commit subjects: `[ADD]`/`[FIX]`/`[UPDATE]` plus a Title Case summary, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Never `git add -A`. Stage named paths only. Every file shows a mode-only change (`core.fileMode` is `true` on a 777 filesystem).
- Run checks with `python3 tools/check_site.py` (all) or `python3 tools/check_site.py -k <name>` (one). It exits 0 only when every check passes.
- New checks go at the end of `tools/check_site.py`, before the `# --- main` banner, under a `# --------------------------------------------------- SEO & cleanup` banner, in the file's existing style (`@check`, `assert cond, "reason"`, and the helpers `html()`, `css()`, `mainjs()`, `read()`, `tags()`, `section()`, `local_path()`, `is_local()`).

## Review Focus

1. **404 page at a nested path** (`hadij.ir/a/b/c`): GitHub Pages serves `404.html` at the requested URL, so relative asset paths break there. Expect a styled page. Pinned by `not_found_page` (Task 5): every local `href`/`src` starts with `/`.
2. **Jekyll build turned on by `_config.yml`**: a Liquid error, such as `{% include %}` inside `CLAUDE.md` or `docs/`, fails the Pages build and keeps serving the old site. Expect the build to succeed. Pinned by `publish_hygiene` (Task 2), which requires those paths in `exclude`, and by the post-push build check in Task 9.
3. **Rendering after Bootstrap is removed**, at each breakpoint (container widths, heading and list margins, `[hidden]`). Expect pixel-level parity. Pinned by the before/after screenshots in Task 6.
4. **GLightbox opened before its deferred CSS arrives, or with JS off**: expect working styles. Pinned by `glightbox_css_deferred` (Task 7), which requires a `<noscript>` fallback link.
5. **JSON-LD `@graph` references**: an `@id` that points nowhere silently breaks Google's ProfilePage parsing. Pinned by `jsonld_graph` (Task 4): every `{"@id": ...}` reference resolves to a node in the graph.

---

### Task 1: Green Baseline for `check_site.py`

Seven checks assert markup that was later changed on purpose. Update them to the current markup so that later failures mean something.

**Files:**
- Modify: `tools/check_site.py` (checks `projects` ~L429, `cert_count_fallback_matches` ~L458, `cert_efset_title` ~L472, `footer` ~L585, `contact_landing` ~L852, `skills_divider` ~L881, `socials_not_spread_on_tablets` ~L907)
- Modify: `.gitignore`

**Interfaces:**
- Produces: a suite that exits 0. Every later task relies on this.

- [ ] **Step 1: Run the suite and confirm exactly these 7 failures**

Run: `python3 tools/check_site.py | grep FAIL`
Expected: `projects`, `cert_count_fallback_matches`, `cert_efset_title`, `footer`, `contact_landing`, `skills_divider`, `socials_not_spread_on_tablets`.

- [ ] **Step 2: Update each check to the current markup**

| Check | Change |
|---|---|
| `projects` | regex `<article class="project-card"` (no `card `) |
| `cert_count_fallback_matches` | compare against `len(tags with class certifications-lightbox)` in `#certifications`, which is 10, not `len(cert_cards())` |
| `cert_efset_title` | assert `"English: EF SET C2 Proficient"` is in the `data-glightbox` attribute of the `ef-set.webp` link (it's an attribute, not text) |
| `footer` | drop `assert "2023" not in f`; assert `"© 2023–" in text(f)` instead. Keep the `footer-top.svg not in html()` assertion |
| `contact_landing` | match `<div class="about-contact" id="contact" data-scroll="center">` and require only `about-socials` inside it |
| `skills_divider` | `<h3 class="about-divider">Skills</h3>`; `.about-divider::before`/`::after` in CSS; keep the centered-group assertion only if it still holds, otherwise delete that line |
| `socials_not_spread_on_tablets` | read the current `.about .about-socials` rule in `css/style.css` and assert the cap/centering it actually uses. If it no longer caps, delete the check |

- [ ] **Step 3: Add `__pycache__/` to `.gitignore` and delete `tools/__pycache__/`**

- [ ] **Step 4: Run the suite**

Run: `python3 tools/check_site.py; echo exit=$?`
Expected: no `FAIL` lines, `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add .gitignore tools/
git commit -m "[FIX] Update Site Checks To Current Markup"
```

---

### Task 2: Publishing Hygiene and File Cleanup

Keep private and dev-only files off hadij.ir, delete unused files, then commit the redesign as a baseline.

**Files:**
- Create: `_config.yml`
- Delete: the paths in `JUNK` below
- Modify: `tools/check_site.py` (new checks `publish_hygiene`, `no_junk_files`)

**Interfaces:**
- Produces: `JUNK` (list of repo-relative paths) in `check_site.py`. Task 6 appends `vendors/bootstrap-5.3.3-dist` to it.

- [ ] **Step 1: Write the failing checks**

```python
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
    "OOP_Python.png", "Web Development_Front-end.png")]

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
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 tools/check_site.py -k junk; python3 tools/check_site.py -k hygiene`
Expected: `FAIL no_junk_files: still present: [...]` and `FAIL publish_hygiene: ... _config.yml` (FileNotFoundError).

- [ ] **Step 3: Confirm the resume group with Hadi before deleting it**

Ask before deleting `resume.pdf`, `resume/Resume.pdf`, `resume/resume.pdf`, `resume/Docs/Hadi_Jafari.pdf` and `resume/Docs/*.png`. For any file Hadi keeps, remove it from `JUNK` instead. Keep the Persian/English `هادی_جعفری-*.pdf` files, `resume/CV.odt` and `resume/logos/`.

- [ ] **Step 4: Delete the files and create `_config.yml`**

Delete tracked paths with `git rm -r --` and untracked ones with `rm`. `_config.yml` contains a short comment explaining why it exists (the Pages publish filter, with no Jekyll features used), then `exclude:` with one `- "<path>"` line for each `UNPUBLISHED` entry.

- [ ] **Step 5: Run the full suite**

Run: `python3 tools/check_site.py; echo exit=$?`
Expected: `exit=0`. `refs_exist` still passes, which proves nothing referenced was deleted.

- [ ] **Step 6: Ask Hadi about `git config core.fileMode false`**

If Hadi agrees, run it. Mode-only changes then disappear from `git status`.

- [ ] **Step 7: Commit the redesign baseline and the cleanup**

Stage only the paths below. Use `git add -u -- <dir>` for deletions under a directory.

```bash
git add _config.yml .gitignore CLAUDE.md index.html sitemap.xml css/base.css css/style.css js/main.js \
  fonts/*.woff2 images/avatar/me-*.webp images/certifications/*.webp images/edu/ images/hero/hadi-*.webp \
  images/hobbies/ images/og-image.jpg images/svg/ "resume/Docs/Machine Learning Foundations for Product Managers.pdf" \
  tools/ docs/
git add -u -- images/ fonts/ resume/ resume.pdf vendors/
git status --short   # review: nothing unintended staged
git commit -m "[UPDATE] Website Redesign And Repository Cleanup"
```

---

### Task 3: Head Metadata, Favicons and Web Manifest

**Files:**
- Modify: `index.html:5-29` (the `<head>` meta block)
- Modify: `images/favicon/site.webmanifest`
- Modify: `tools/check_site.py` (new checks `head_meta`, `manifest`)

- [ ] **Step 1: Write the failing checks**

```python
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
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 tools/check_site.py -k head_meta; python3 tools/check_site.py -k manifest`
Expected: `FAIL head_meta: og:url https://hadij.ir` and `FAIL manifest: names`.

- [ ] **Step 3: Edit `<head>`**

- Set `og:url` to `https://hadij.ir/`.
- Add `og:type` `profile`, `profile:first_name`/`profile:last_name`, `og:site_name` `Hadi Jafari`, `og:locale` `en_US`, and `og:image:alt` (reuse the hero alt text: "Hadi Jafari in a black coat and red scarf, adjusting his glasses under autumn trees").
- Add `twitter:title`/`twitter:description` (copies of the og values), `twitter:image` and `twitter:image:alt`.
- Add `<meta name="theme-color" content="#0b0b0f" />`.
- Delete the `keywords` meta.
- Add `<link rel="icon" href="images/favicon/favicon.ico" sizes="any" />` and `<link rel="icon" type="image/png" sizes="192x192" href="images/favicon/android-chrome-192x192.png" />` next to the existing favicon links.

- [ ] **Step 4: Rewrite the manifest**

Use `name`/`short_name` `Hadi Jafari`, `start_url` `/`, both colors `#0b0b0f`, `display` `standalone`, and icon `src`s relative to the manifest (`android-chrome-192x192.png`, `android-chrome-512x512.png`).

- [ ] **Step 5: Run the full suite**

Run: `python3 tools/check_site.py; echo exit=$?`
Expected: `exit=0`. `og_meta` still passes.

- [ ] **Step 6: Commit**

```bash
git add index.html images/favicon/site.webmanifest tools/check_site.py
git commit -m "[FIX] Complete Social Meta Tags And Web Manifest"
```

---

### Task 4: Structured Data and Sitemap

**Files:**
- Modify: `index.html:41-95` (the JSON-LD block)
- Modify: `sitemap.xml`
- Modify: `tools/check_site.py`: `jsonld_data()` ~L607, `jsonld()` ~L614, `sitemap()` ~L637; new check `jsonld_graph`

**Interfaces:**
- Consumes: `SITE` from Task 3.
- Produces: `jsonld_graph_nodes() -> list[dict]`. `jsonld_data()` now returns the `Person` node from the graph.

- [ ] **Step 1: Update and add the checks**

```python
def jsonld_graph_nodes():
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html(), re.S)
    assert m, "no JSON-LD"
    return json.loads(m.group(1))["@graph"]


def jsonld_data():
    people = [n for n in jsonld_graph_nodes() if n.get("@type") == "Person"]
    assert len(people) == 1, "%d Person nodes" % len(people)
    return people[0]


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
```

In `jsonld()`, change the `sameAs` assertion to `[SOCIAL[0], SOCIAL[1], SOCIAL[3], SOCIAL[4]]` (GitHub, LinkedIn, Telegram, Instagram). Verify the indices against `SOCIAL` ~L292.

Replace `sitemap()` with this:

```python
@check
def sitemap():
    s = read("sitemap.xml")
    assert re.findall(r"<loc>([^<]+)</loc>", s) == [SITE], "sitemap must list only %s" % SITE
    assert re.search(r"<lastmod>\d{4}-\d\d-\d\d</lastmod>", s), "no lastmod"
    assert "<priority>" not in s, "priority is ignored; drop it"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 tools/check_site.py -k jsonld; python3 tools/check_site.py -k sitemap`
Expected: `KeyError: '@graph'` failures, and `FAIL sitemap: sitemap must list only https://hadij.ir/`.

- [ ] **Step 3: Rewrite the JSON-LD block**

Use `{"@context": "https://schema.org", "@graph": [WebSite, ProfilePage, Person]}`:
- `WebSite`: `@id` `https://hadij.ir/#website`, `url`, `name` `Hadi Jafari`, `inLanguage` `en`.
- `ProfilePage`: `@id` `https://hadij.ir/#profile`, `url`, `name` (the `<title>` text), `isPartOf` `{"@id": "…#website"}`, `mainEntity` `{"@id": "…#person"}`.
- `Person`: the existing object, plus `@id` `https://hadij.ir/#person`, `url` with a trailing slash, `alternateName` `هادی جعفری`, and `https://t.me/haadijafari` in `sameAs` (in footer order).

- [ ] **Step 4: Rewrite `sitemap.xml`**

One `<url>` with `<loc>https://hadij.ir/</loc>` and `<lastmod>` set to the date of this commit (`2026-10-21` or later).

- [ ] **Step 5: Run the full suite**

Run: `python3 tools/check_site.py; echo exit=$?`
Expected: `exit=0`.

- [ ] **Step 6: Commit**

```bash
git add index.html sitemap.xml tools/check_site.py
git commit -m "[UPDATE] ProfilePage Structured Data And Single-URL Sitemap"
```

---

### Task 5: Custom 404 Page

**Files:**
- Create: `404.html`
- Modify: `tools/check_site.py` (new check `not_found_page`)

- [ ] **Step 1: Write the failing check**

```python
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
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 tools/check_site.py -k not_found`
Expected: `FAIL not_found_page: FileNotFoundError`.

- [ ] **Step 3: Create `404.html`**

The page has:
- `lang="en"`, the charset and viewport metas, `<meta name="robots" content="noindex" />`, and `<title>Page not found | Hadi Jafari</title>`.
- Root-absolute links to `/css/base.css`, `/images/favicon/favicon.ico` and `/fonts/pinyon-script.woff2` (used by the heading).
- A centered block with `<h1>` "Page not found" (in `var(--font-script)`), one sentence, and `<a class="btn-primary-pill" href="/">Back to hadij.ir</a>`.

Any extra styling goes in a small inline `<style>` that uses the tokens from `base.css`.

- [ ] **Step 4: Run the suite, then view the page**

Run: `python3 tools/check_site.py; echo exit=$?`, then `python3 -m http.server 8000` and open http://localhost:8000/404.html.
Expected: `exit=0`. The page is styled, dark and centered.

- [ ] **Step 5: Commit**

```bash
git add 404.html tools/check_site.py
git commit -m "[ADD] Custom 404 Page"
```

---

### Task 6: Replace Bootstrap With a Small Reset

The page uses only `container`, `card`, `d-flex`, `d-lg-none`, `flex-column`, `justify-content-center`, `align-items-center` and `visually-hidden`, and reads no `--bs-*` variable. Bootstrap's 240 KB of render-blocking CSS goes. Its reboot rules and those classes move into `base.css`.

**Files:**
- Modify: `css/base.css`: new `/*----- # Reset -----*/` section before `# Tokens`, and new `# Utilities` rules
- Modify: `index.html:2` (drop `data-bs-theme="dark"`) and `index.html:31-32` (drop the Bootstrap `<link>`)
- Delete: `vendors/bootstrap-5.3.3-dist/`
- Modify: `tools/check_site.py` (append `"vendors/bootstrap-5.3.3-dist"` to `JUNK`; new check `no_bootstrap`; `weight_budget` cap → `250_000`)
- Modify: `CLAUDE.md` (the "Custom Bootstrap build" bullet, plus mentions of Bootstrap and `data-bs-theme`)

- [ ] **Step 1: Take "before" screenshots**

Run: `tools/screens.sh before; for a in about projects certifications resume services hobbies; do tools/screens.sh before "#$a"; done`
Expected: one PNG per size per anchor under `~/snap/firefox/common/claude-prof/shots/`.

- [ ] **Step 2: Write the failing checks**

```python
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
```

Also append `"vendors/bootstrap-5.3.3-dist"` to `JUNK`, and change the `weight_budget` cap to `250_000` (it is 467,908 today, and Bootstrap is 240,123 of that).

- [ ] **Step 3: Run them to verify they fail**

Run: `python3 tools/check_site.py | grep FAIL`
Expected: `no_bootstrap`, `no_junk_files` and `weight_budget` fail.

- [ ] **Step 4: Add the Reset section to `base.css`**

Port only the Bootstrap 5.3.3 Reboot rules this page relies on, with these values:
- `*, ::before, ::after { box-sizing: border-box }`
- `body { margin: 0; -webkit-text-size-adjust: 100% }`
- `h1`–`h6`: `margin: 0 0 .5rem; font-weight: 500; line-height: 1.2`. Sizes: h1 `calc(1.375rem + 1.5vw)` → `2.5rem` at ≥1200px, h2 `calc(1.325rem + .9vw)` → `2rem`, h3 `calc(1.3rem + .6vw)` → `1.75rem`, h4 `calc(1.275rem + .3vw)` → `1.5rem`
- `p`, `ul`, `ol`, `dl`: `margin: 0 0 1rem`. `ul`/`ol`: `padding-left: 2rem`. `dt { font-weight: 700 }`. `dd { margin: 0 0 .5rem }`
- `figure { margin: 0 0 1rem }`. `img, svg { vertical-align: middle }`. `b, strong { font-weight: bolder }`
- `button { margin: 0; font: inherit; color: inherit; text-transform: none; border-radius: 0 }`. `button:not(:disabled) { cursor: pointer }`
- `[hidden] { display: none !important }`

Add `color-scheme: dark;` to `:root`.

- [ ] **Step 5: Add the utilities to `base.css`**

Add them under a `# Utilities` banner:
- `.container`: `width: 100%; padding-inline: .75rem; margin-inline: auto`. `max-width` 540/720/960/1140/1320px at 576/768/992/1200/1400px.
- `.d-flex { display: flex !important }`, `.flex-column { flex-direction: column !important }`, `.justify-content-center { justify-content: center !important }`, `.align-items-center { align-items: center !important }`
- `@media (min-width: 992px) { .d-lg-none { display: none !important } }`
- `.visually-hidden`: Bootstrap's exact rule (absolute, 1px × 1px, `margin: -1px`, `overflow: hidden`, `clip: rect(0,0,0,0)`, `white-space: nowrap`, `border: 0`, all `!important`)

`.card` is already styled in `base.css` `# Components`. Add `position: relative; display: flex; flex-direction: column; min-width: 0` only if the screenshots show a difference.

- [ ] **Step 6: Remove Bootstrap**

Delete the `<link>` for `bootstrap.min.css` and the `<!-- Bootstrap CSS -->` comment, remove `data-bs-theme="dark"` from `<html>`, and run `git rm -r vendors/bootstrap-5.3.3-dist`.

- [ ] **Step 7: Run the suite**

Run: `python3 tools/check_site.py; echo exit=$?`
Expected: `exit=0`.

- [ ] **Step 8: Take "after" screenshots and compare each pair**

Run the Step 1 commands with label `after`. Then, for each matching pair, run `python3 tools/combine.py ~/snap/firefox/common/claude-prof/shots/cmp-<name>.png <before> <after>` and look at the result.
Expected: no visible difference at any of the 6 sizes. Fix each difference with a rule in the Reset section, then re-shoot.

- [ ] **Step 9: Update `CLAUDE.md`**

Replace the "Custom Bootstrap build" bullet with one sentence: styles are self-contained, `css/base.css` holds the reset, tokens and the few layout utilities. Remove the `data-bs-theme` and `--bs-purple*` mentions.

- [ ] **Step 10: Commit**

```bash
git add css/base.css index.html tools/check_site.py CLAUDE.md
git add -u -- vendors/bootstrap-5.3.3-dist
git commit -m "[UPDATE] Replace Bootstrap With A Small Reset"
```

---

### Task 7: Font Preload and Non-Blocking GLightbox CSS

**Files:**
- Modify: `index.html` `<head>`
- Modify: `tools/check_site.py` (new checks `hero_font_preloaded`, `glightbox_css_deferred`)

- [ ] **Step 1: Write the failing checks**

```python
@check
def hero_font_preloaded():
    pre = [a for a in tags("link") if a.get("rel") == "preload" and a.get("as") == "font"]
    assert [a.get("href") for a in pre] == ["fonts/pinyon-script.woff2"], "preloads %s" % pre
    a = pre[0]
    assert a.get("type") == "font/woff2" and "crossorigin" in a, "preload needs type and crossorigin"


@check
def glightbox_css_deferred():
    head = html().split("</head>")[0]
    link = re.search(r'<link[^>]*glightbox\.min\.css[^>]*>', head.split("<noscript>")[0])
    assert link and 'media="print"' in link.group(0) and "this.media='all'" in link.group(0), "not deferred"
    assert re.search(r"<noscript>\s*<link[^>]*glightbox\.min\.css", head), "no <noscript> fallback"
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python3 tools/check_site.py -k font_preloaded; python3 tools/check_site.py -k deferred`
Expected: both FAIL.

- [ ] **Step 3: Edit `<head>`**

Before the stylesheets, add `<link rel="preload" href="fonts/pinyon-script.woff2" as="font" type="font/woff2" crossorigin />`. Change the GLightbox link to `media="print" onload="this.media='all'"` and add `<noscript><link rel="stylesheet" href="vendors/glightbox/css/glightbox.min.css" /></noscript>` right after it.

- [ ] **Step 4: Run the suite, then open a certificate in the browser**

Run: `python3 tools/check_site.py; echo exit=$?`. Then serve locally, open a certificate, and check the console.
Expected: `exit=0`. The lightbox is fully styled and the console has no errors.

- [ ] **Step 5: Commit**

```bash
git add index.html tools/check_site.py
git commit -m "[UPDATE] Preload Hero Font And Defer Lightbox CSS"
```

---

### Task 8: Small Correctness and Accessibility Fixes

**Files:**
- Modify: `js/main.js` (GLightbox config near the end of the IIFE)
- Modify: `index.html` (cert `download` attributes at lines ~375 and ~398, `.back-to-top` ~L576, resume org ~L449)
- Modify: `tools/check_site.py` (new check `small_fixes`)

- [ ] **Step 1: Write the failing check**

```python
@check
def small_fixes():
    assert mainjs().count("openEffect") == 1, "duplicate openEffect key"
    downloads = [a["download"] for a in tags("a") if "download" in a]
    assert downloads and all(d.endswith(".pdf") for d in downloads), "download names %s" % downloads
    btt = [a for a in tags("a") if "back-to-top" in classes(a)]
    assert btt and btt[0].get("aria-label") == "Back to top", "back-to-top has no name"
    assert '<p class="resume-org">Freelance</p>' in section("resume"), "freelance role has no org"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 tools/check_site.py -k small_fixes`
Expected: `FAIL small_fixes: duplicate openEffect key`.

- [ ] **Step 3: Make the four fixes**

- Keep `openEffect: "fade"` (it wins today, so behavior is unchanged) and delete the `"zoom"` line.
- Add `.pdf` to both certificate `download` names.
- Add `aria-label="Back to top"` to `.back-to-top`.
- Change the "Django Back-end Developer" `resume-org` from "Isfahan, Iran" to "Freelance".

- [ ] **Step 4: Run the suite**

Run: `python3 tools/check_site.py; echo exit=$?`
Expected: `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add js/main.js index.html tools/check_site.py
git commit -m "[FIX] Lightbox Config, Download Names And Back-To-Top Label"
```

---

### Task 9: Publish and Verify (Hadi does the manual steps)

**Files:**
- Modify: `CLAUDE.md` ("Resume files" section)

- [ ] **Step 1: Update the CLAUDE.md "Resume files" section**

List what remains: `resume/hadi_jafari_resume.pdf` (linked), `resume/CV.odt` (source, unpublished) and the `هادی_جعفری-*.pdf` versions. Add one line explaining that `_config.yml` `exclude` keeps dev-only paths off hadij.ir, and that new private paths go there.

- [ ] **Step 2: Run the full suite one last time**

Run: `python3 tools/check_site.py; echo exit=$?`
Expected: `exit=0`.

- [ ] **Step 3: Commit, then push only after Hadi says so**

```bash
git add CLAUDE.md
git commit -m "[UPDATE] Document Publishing Rules And Resume Files"
```

Pushing publishes the site, so ask Hadi first.

- [ ] **Step 4: Confirm the Pages build and the exclusions after the push**

Run: `gh api repos/haadijafari/haadijafari.github.io/pages/builds/latest --jq .status`
Expected: `built`. Then `curl -sI https://hadij.ir/CLAUDE.md https://hadij.ir/docs/ https://hadij.ir/tools/check_site.py | grep HTTP` returns three `404`s, and `curl -sI https://hadij.ir/nope/deep | grep HTTP` returns `404` (load that URL in a browser too and confirm the page is styled).

- [ ] **Step 5: Hadi's manual checklist (not code)**

- Rich Results Test on https://hadij.ir/ shows a valid ProfilePage. Check the link preview in the opengraph.xyz or LinkedIn Post Inspector.
- Search Console: submit `https://hadij.ir/sitemap.xml` and request indexing of `/`. Bing Webmaster Tools: import from Search Console.
- GitHub Pages settings: "Enforce HTTPS" is on, and `www.hadij.ir` redirects to the apex domain (needs a `www` CNAME DNS record).
- Link https://hadij.ir from your GitHub profile, LinkedIn "Website" and Instagram bio.
- Optional: run Lighthouse (mobile). Performance and SEO should both be ≥ 95.
