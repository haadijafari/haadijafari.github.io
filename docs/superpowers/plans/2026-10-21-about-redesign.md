# About Section Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plain About section with Hadi's approved "demo 3" profile (ringed photo, name, tags, collapsible intro, details, numbers, brand-color social circles, Skills divider), laid out in two columns from 992px up, and make the hero's Contact button land the numbers and social circles mid-screen.

**Architecture:** Static page, no build step. Markup goes in `index.html` `#about`; styles go in the `# About Me` block of `css/style.css` (watermark size goes in `css/base.css`); behavior goes in `js/main.js`. Every task is driven by a new `@check` in `tools/check_site.py` that is watched failing before the change.

**Tech Stack:** HTML, CSS (custom properties from `css/base.css`), vanilla JS, Python 3 stdlib checks, headless Firefox screenshots (`tools/screens.sh`).

**Spec:** `docs/superpowers/specs/2026-10-21-about-redesign-design.md`. The approved visual reference is `.superpowers/brainstorm/54550-1792577861/content/about-details-v5.html`. It is git-ignored; follow its proportions, not its pixel values.

## Global Constraints

- **No commits** until Hadi says so. The commit steps below are "no commit". Stage nothing.
- Work stays on `main` in the working tree, as with the previous plan; Hadi approved that ("proceed native"). No worktree.
- **Content rules:**
  - The secret product name never appears anywhere in the repo, this plan included.
  - No phone number anywhere.
- **Static site:**
  - No CDN and no new libraries.
  - Colors come from the `css/base.css` tokens (`--c-primary #8E05C2`, `--c-primary-2`, `--c-primary-dark #3E065F`, `--c-accent #c77dff`, `--c-bg`, `--c-surface`, `--c-border`, `--c-text`, `--c-muted`). The only exceptions are the brand colors on the social logos.
- **Breakpoint:**
  - The phone layout applies below 992px, written as `@media (min-width: 992px)` for desktop.
  - Phone-only rules go in the base styles. No `max-width` queries are needed except in JS.
- **Copy:**
  - The intro paragraphs are exactly `ABOUT_P1` and `ABOUT_P2` in `tools/check_site.py`.
  - The social hrefs and their order are exactly `SOCIAL`.
  - The skills are exactly `SKILLS`.
- **Icons:**
  - Bootstrap glyphs come from the generated sprite: run `python3 tools/build_assets.py sprite` after adding any `<use href="#i-…">`.
  - The two brand logos (Gmail, Instagram) are hand-written symbols in their own block, which the sprite builder does not touch.
- **Layout and access:**
  - No horizontal overflow at 360, 390, 430, 768, 844 or 1280px.
  - Every link and the Read more button show the global `:focus-visible` ring. Never set `outline: none`.
- **Whole suite:** `python3 tools/check_site.py` must be all PASS at the end of every task.
- **Alignment (from the mockup):**
  - On phones, these are centered: the photo, name, tags, numbers, social circles, Skills divider and skill groups.
  - The intro paragraphs and the details list stay start-aligned (left), as in the mockup, because centered paragraphs are hard to read.

## Review Focus

1. **The brand gradients disappear.** An SVG `<linearGradient>`/`<radialGradient>` inside a `display:none` (or `hidden`) `<svg>` does not paint through `<use>` in Firefox or Chrome. The brand block must be hidden by size (`width="0" height="0"`, `position:absolute`), never with `hidden`. → Task 3 `brand_icons` asserts this; Task 6 screenshots confirm that the Instagram gradient and the four-color Gmail M paint.
2. **No JavaScript.** Expect the full intro and no Read more button. → Task 4 `intro_toggle` asserts the button ships with `hidden` and the collapse class is added only by JS.
3. **Resizing across 992px with the intro open or closed** (rotating a tablet). Desktop must never show a clipped intro or the button. The CSS at ≥992px overrides the collapsed state; JS doesn't need to listen. → Task 4 asserts the desktop override in the CSS.
4. **A 360px phone.** The two tags, the five circles and the long Freelance row must fit without sideways scroll. → Task 6 screenshots at 360x800.
5. **A `prefers-reduced-motion` visitor clicking Contact.** Expect an instant jump to the centered block, not a smooth scroll. → Task 3 `contact_landing` asserts both the JS behavior and the CSS `scroll-behavior` override.

---

## File Structure

- **Modify `index.html`:**
  - `#about` is replaced wholesale, part by part, across Tasks 2–5.
  - A new hand-written brand-icon `<svg>` goes right after `<!-- icons:end -->` (Task 3).
  - The sprite is regenerated.
- **Modify `css/base.css`:**
  - the `.section-title .title-watermark` font-size (Task 1)
  - a reduced-motion `scroll-behavior` override (Task 3)
- **Modify `css/style.css`:** the whole `# About Me` block is rewritten. Each task deletes the old rules its new markup replaces.
- **Modify `js/main.js`:**
  - `scrollto` learns to center (Task 3)
  - a new intro toggle (Task 4)
- **Modify `tools/check_site.py`:**
  - new checks under a `# ------------------------------------------------- About redesign` banner
  - `about_copy` is updated (Task 2)
  - a `clamp_px` helper is added (Task 1)

Target `#about` structure. Each task fills in its part; class names are the interface between the tasks:

```
section#about.section.about > .container
  .section-title                      (unchanged)
  .about-profile                      (grid on desktop: 320px | 1fr)
    .profile-card                     (left on desktop)
      .profile-ring > img.profile-photo
      h3.profile-name                 "Hadi Jafari"
      ul.profile-tags > li.profile-tag ×2
    .profile-body                     (right on desktop)
      #about-intro.about-intro > p ×2
      button.intro-toggle
      dl.about-details > div ×4
      #contact.about-reach
        .about-numbers > .about-number ×3
        ul.about-socials > li > a ×5
  h3.skills-divider                   "Skills"
  .skills > .skill-group ×4           (existing markup, kept)
```

---

### Task 1: Bigger faded handwriting on phones (all section titles)

**Files:**
- Modify: `css/base.css` (`.section-title .title-watermark` font-size and top)
- Test: `tools/check_site.py`

**Interfaces:**
- Produces: `clamp_px(expr: str, vw: float) -> float`, a test helper that evaluates `clamp(Arem, Brem + Cvw, Drem)` (or a plain `Nrem`) at a viewport width, with 1rem = 16px.

- [ ] **Step 1: Write the failing test** (new banner `About redesign`, plus the helper near `font_faces`)

```python
@check
def watermark_size_phone():
    wm = re.search(r"\.section-title \.title-watermark\s*{[^}]*font-size:\s*([^;]+);", css()).group(1)
    h2 = re.search(r"\.section-title h2\s*{[^}]*font-size:\s*([^;]+);", css()).group(1)
    ratio = clamp_px(wm, 360) / clamp_px(h2, 360)
    assert ratio >= 2.3, "watermark only %.2fx the title at 360px" % ratio
    assert clamp_px(wm, 1280) == 160, "desktop watermark %spx, want 10rem" % clamp_px(wm, 1280)
```

- [ ] **Step 2: Run it.** Run `python3 tools/check_site.py -k watermark_size`. Expected: `FAIL watermark_size_phone: watermark only 1.30x the title at 360px`.
- [ ] **Step 3: Implement.**
  - Set the watermark font-size to `clamp(4.25rem, 2.5rem + 9vw, 10rem)`. That gives about 72px at 360 (2.45×) and 160px at 1280.
  - Leave `top` (it's keyed to the h2 size) and `opacity: 0.3` as they are.
  - `.section` already has `overflow-x: clip`.
- [ ] **Step 4: Run the whole suite.** Run `python3 tools/check_site.py`. Expected: all PASS.
- [ ] **Step 5: Look at the result.** Run `SIZES="360x800 1280x800" tools/screens.sh wm '#about'` and `… '#services'`. Expected: the handwriting is large behind each title and there's no horizontal scrollbar.
- [ ] **Step 6: No commit** (Hadi's rule).

---

### Task 2: Profile head and details list

**Files:**
- Modify: `index.html` (`#about`: replace `.about-top` and `dl.info-list` with `.about-profile`, `.profile-card` and the start of `.profile-body`)
- Modify: `css/style.css` (delete the `.about-top`, `.about-photo`, `.about-intro h3` and `.info-list` rules, and add the new ones)
- Modify: `tools/check_site.py` (`about_copy`, plus the new checks)

**Interfaces:**
- Consumes: the `ageFrom(2003, 3)` writes into `#age` (unchanged `js/main.js`)
- Produces:
  - the `.about-profile`, `.profile-card` and `.profile-body` containers
  - `#about-intro.about-intro`, holding the two paragraphs (moved here unchanged; Task 4 adds the toggle)
  - the `.desk-only` utility: hidden below 992px, shown at ≥992px

- [ ] **Step 1: Write the failing tests.** Change `about_copy` to `assert ABOUT_HEADING not in t, "old subheading still shown"` and keep the P1/P2 asserts. Add:

```python
@check
def about_profile():
    sec = section("about")
    imgs = tags("img", sec)
    assert "profile-photo" in classes(imgs[0]), "first #about image is not .profile-photo"
    assert '<div class="profile-ring">' in sec, "no story ring"
    assert re.search(r'<h3 class="profile-name">Hadi Jafari</h3>', sec), "name"
    tag_block = re.search(r'<ul class="profile-tags".*?</ul>', sec, re.S)
    got = [unescape(s.strip()) for s in re.findall(r"</svg>([^<]+)</li>", tag_block.group(0))] if tag_block else []  # from html import unescape
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
    assert 'April 2003 (<span id="age">23</span> years)' in dl, "birthday line with #age inside"
    assert "<dt>Age" not in dl and ">Age<" not in dl, "separate Age row"
    t = text(dl)
    assert "BSc Computer Science" in t and "MSc AI & Soft Computing" in t, "degree lines"
    assert re.search(r'<span class="[^"]*\bdesk-only\b[^"]*">\(in progress\)</span>', dl), "(in progress) not desk-only"
    assert re.search(r'<div class="desk-only"><dt><svg[^>]*><use href="#i-envelope"/></svg>Email</dt>', dl), "Email row not desk-only"
    assert 'class="hire-link" href="mailto:haadijafari2003@gmail.com?subject=Freelance%20project">Contact me</a>' in dl, "hire link"
    assert re.search(r"\.desk-only\s*{\s*display:\s*none;", css()), "desk-only not hidden on phones"
    assert re.search(r"@media \(min-width: 992px\)\s*{[^@]*\.desk-only\s*{\s*display:", css()), "desk-only not shown on desktop"
```

- [ ] **Step 2: Run them.** Run `python3 tools/check_site.py -k about_`. Expected:
  - `about_profile`, `about_details` and `about_copy` FAIL ("old subheading still shown")
  - `about_photo` still PASS
- [ ] **Step 3: Implement the markup.**
  - **Photo:**
    - Wrap the existing `<img>` in `.profile-ring`, with the class `profile-photo`. Keep its `srcset`, `width="479" height="605"`, `loading="lazy"` and `decoding`.
    - Set `sizes="(min-width: 992px) 280px, min(68vw, 260px)"`.
    - Keep the alt text. The photo isn't a link.
  - **Tags:** each `li.profile-tag` is `<li class="profile-tag"><svg class="icon" aria-hidden="true"><use href="#i-briefcase"/></svg>Co-founder &amp; CTO, Vira Kavane Zista</li>`. The location tag uses `#i-geo-alt` and reads `Isfahan, Iran`.
  - **Intro:** drop the `<h3>` subheading and move the two paragraphs into `<div class="about-intro" id="about-intro">`.
  - **Details:** each `dt` is `<dt><svg class="icon" aria-hidden="true"><use href="#i-NAME"/></svg>Label</dt>`.
    - Birthday dd: `April 2003 (<span id="age">23</span> years)`
    - Degree dd: `BSc Computer Science<br>MSc AI &amp; Soft Computing <span class="muted desk-only">(in progress)</span>`
    - Email row div: has the class `desk-only`; its dd is the mailto link.
    - Freelance dd: `<span class="available">Available</span>` followed by the `hire-link`.
  - Leave `.facts`, the contact cards and the skills alone; later tasks replace them.
  - Run `python3 tools/build_assets.py sprite`.
- [ ] **Step 4: Implement the CSS.** Use the existing tokens throughout.
  - **Ring:**
    - `.profile-ring`: `width: min(68%, 260px)`, `aspect-ratio: 1`, `margin-inline: auto`, `padding: 4px`, `border-radius: 50%`, `background: conic-gradient(from 210deg, var(--c-accent), var(--c-primary), var(--c-primary-dark), var(--c-primary), var(--c-accent))`.
    - `.profile-photo`: fills the ring, `border: 4px solid var(--c-bg)` (the gap), `border-radius: 50%`, `object-fit: cover`, `object-position: center 16%`.
  - **Name:** `.profile-name` is the body font, weight 800, about `var(--fs-2xl)`, centered, `#fff`.
  - **Tags:** `.profile-tags` is a centered `flex-wrap: wrap` row. Each `.profile-tag` is an outlined pill: a `rgba(199,125,255,.35)` border, a purple `--c-accent` icon, `var(--fs-sm)` text and `#fff`.
  - **Details:**
    - `.about-details`: `grid-template-columns: repeat(2, minmax(0, 1fr))`.
    - The Email and Freelance rows span both columns on phones (`.about-details > div:nth-child(n+3) { grid-column: 1 / -1 }`).
    - `dt`: inline-flex, small, `var(--c-muted)`, with a grey icon.
    - `dd`: `overflow-wrap: anywhere`.
  - **Freelance row:** `.about-details .available` keeps the green dot (`#4ade80` with a 6px glow, inline-block). The dd is flex with `justify-content: space-between`, `align-items: center` and `flex-wrap: wrap`.
  - **Hire link:** `.hire-link` is a simple outlined pill: `1px solid var(--c-primary)`, `--c-accent` text, weight 600, `var(--fs-sm)`, no fill, no glow and no icon. On hover the background becomes `#1d1426`.
  - **Desk-only utility:** `.desk-only { display: none; }` in the base styles. Under `@media (min-width: 992px)`, use `.desk-only { display: revert; }` and `div.desk-only { display: block; }`.
- [ ] **Step 5: Run the whole suite.** Run `python3 tools/check_site.py`. Expected: all PASS, including `info_list`, `about_photo`, `imgs_lazy_sized` and `icons_defined`.
- [ ] **Step 6: No commit.**

---

### Task 3: Numbers, brand social circles, contact landing

**Files:**
- Modify: `index.html`:
  - replace `.facts`, `h3#contact` and `.contact-cards` with `#contact.about-reach`
  - add the brand-icon block after `<!-- icons:end -->`
- Modify: `css/style.css` (delete the `.facts`/`.fact` and contact-card rules, and add the new ones)
- Modify: `css/base.css` (add the reduced-motion `scroll-behavior` override)
- Modify: `js/main.js` (`scrollto`)
- Test: `tools/check_site.py`

**Interfaces:**
- Consumes: `.profile-body` (Task 2), `#cert-count` (kept), `SOCIAL`
- Produces:
  - `#contact.about-reach`, the scroll target
  - the symbols `#b-gmail` and `#b-instagram`
  - `scrollto(hash)`, which centers elements that carry `data-scroll="center"`

- [ ] **Step 1: Write the failing tests.**

```python
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
    block = re.search(r"<!-- brand-icons:start -->(.*?)<!-- brand-icons:end -->", html(), re.S)
    assert block, "no brand-icons block"
    svg = tags("svg", block.group(1))[0]
    assert "hidden" not in svg and 'display' not in svg.get("style", ""), "display:none breaks the gradients"
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
    reach = re.search(r'<div class="about-reach" id="contact" data-scroll="center">(.*)', sec, re.S)
    assert reach and "about-numbers" in reach.group(1) and "about-socials" in reach.group(1), "#contact does not wrap numbers + socials"
    js = mainjs()
    assert 'block: "center"' in js, "no centered scroll"
    assert re.search(r'reduceMotion \? "instant" : "smooth"', js), "scroll ignores reduced motion"
    assert re.search(r"prefers-reduced-motion: reduce\)\s*{\s*html\s*{\s*scroll-behavior:\s*auto", css()), "CSS smooth scroll not gated"
```

- [ ] **Step 2: Run them.** Run `python3 tools/check_site.py -k "about_numbers"`, then each of the other three names. Expected: all four FAIL ("no .about-numbers", "no ul.about-socials", "no brand-icons block", "#contact does not wrap…").
- [ ] **Step 3: Implement the brand block.** Place it right after `<!-- icons:end -->`:

```html
  <!-- brand-icons:start (hand-written: official multicolor logos; hidden by size, since display:none breaks gradients) -->
  <svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
    <defs>
      <radialGradient id="b-ig-grad" cx="30%" cy="107%" r="150%">
        <stop offset="0" stop-color="#fdf497"/><stop offset=".05" stop-color="#fdf497"/>
        <stop offset=".45" stop-color="#fd5949"/><stop offset=".6" stop-color="#d6249f"/><stop offset=".9" stop-color="#285aeb"/>
      </radialGradient>
    </defs>
    <symbol id="b-gmail" viewBox="52 42 88 66">
      <path fill="#4285f4" d="M58 108h14V74L52 59v43c0 3.32 2.69 6 6 6"/>
      <path fill="#34a853" d="M120 108h14c3.32 0 6-2.69 6-6V59l-20 15"/>
      <path fill="#fbbc04" d="M120 48v26l20-15v-8c0-7.42-8.47-11.65-14.4-7.2"/>
      <path fill="#ea4335" d="M72 74V48l24 18 24-18v26L96 92"/>
      <path fill="#c5221f" d="M52 51v8l20 15V48l-5.6-4.2c-5.94-4.45-14.4-.22-14.4 7.2"/>
    </symbol>
    <symbol id="b-instagram" viewBox="0 0 16 16"><path fill="url(#b-ig-grad)" d="(copy the d of #i-instagram from the sprite)"/></symbol>
  </svg>
  <!-- brand-icons:end -->
```

- [ ] **Step 4: Implement the markup.**
  - `<div class="about-reach" id="contact" data-scroll="center">` closes `.profile-body`.
  - **Numbers:** `<div class="about-numbers">` holds three `<div class="about-number"><strong>…</strong><span>…</span></div>`:
    - `3+` / `years of Django`
    - `17.57` / `BSc GPA / 20`
    - `<strong id="cert-count">10</strong>` / `certificates`
  - **Social circles:** `<ul class="about-socials" aria-label="Social links">` with five `<li><a href="…"><span class="social-circle"><svg class="icon" aria-hidden="true"><use href="…"/></svg></span><span class="social-label">GitHub</span></a></li>`, in `SOCIAL` order.
    - The external links get `target="_blank" rel="noopener"`.
    - Each brand color goes on its circle: `.social-github` gets `#fff`, `.social-linkedin` gets `#0A66C2` and `.social-telegram` gets `#26A5E4`, set as `color` (the sprite paths use `currentColor`).
  - Delete the `.facts` div, `h3#contact` and `.contact-cards`, then run `python3 tools/build_assets.py sprite`.
    - The sprite drops `arrow-up-right` if nothing else uses it.
    - `envelope-fill` stays for the hero button.
- [ ] **Step 5: Implement the CSS.**
  - **Numbers:** `.about-numbers` is a 3-column grid, centered, with top and bottom `1px solid var(--c-border)` rules and padding of about 1rem 0.
    - `strong`: block, weight 900, `var(--fs-2xl)`, `#fff`.
    - `span`: `var(--fs-sm)`, `var(--c-muted)`.
  - **Social circles:**
    - `.about-socials`: no list style, flex, `justify-content: space-between`, margin about 1.5rem 0 0. At ≥992px it becomes `justify-content: center; gap: 1rem`.
    - Each `a`: a column flex, centered, `var(--c-text)`, 0.75rem label.
    - `.social-circle`: 56px, `border-radius: 50%`, `background: var(--c-surface)`, a thin neutral ring (`box-shadow: 0 0 0 2px var(--c-bg), 0 0 0 3px var(--c-border)`) and a 1.5rem icon. On `a:hover`, the ring becomes `var(--c-primary)`.
  - Delete the old fact and contact-card rules.
  - **Reduced motion:** in `css/base.css`, after `html { scroll-behavior: smooth; }`, add `@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }`.
- [ ] **Step 6: Implement `scrollto` in `js/main.js`.**
  - Hoist `const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;` above `scrollto`, and delete its later declaration. Typed.js keeps using it.
  - `scrollto(el)`:
    - Let `target = select(el)` and `behavior = reduceMotion ? "instant" : "smooth"`.
    - If `target.dataset.scroll === "center"`, call `target.scrollIntoView({ block: "center", behavior })`.
    - Otherwise, call `window.scrollTo({ top: target.offsetTop, behavior })`.
  - The click handler and the load-with-hash handler already call `scrollto`, so `hadij.ir/#contact` centers too.
- [ ] **Step 7: Run the whole suite.** Run `python3 tools/check_site.py`. Expected: all PASS, including `social_links_exact` (footer pills unchanged), `no_inflated_stats` ("MSc" now comes from Degree), `cert_count_fallback_matches` and `icons_defined`.
- [ ] **Step 8: No commit.**

---

### Task 4: Collapsible intro on phones

**Files:**
- Modify: `index.html` (add the toggle button after `#about-intro`)
- Modify: `css/style.css`
- Modify: `js/main.js`
- Test: `tools/check_site.py`

**Interfaces:**
- Consumes: `#about-intro.about-intro` (Task 2)
- Produces: the `button.intro-toggle` and the `.is-collapsed` class, added only by JS

- [ ] **Step 1: Write the failing test.**

```python
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
```

- [ ] **Step 2: Run it.** Run `python3 tools/check_site.py -k intro_toggle`. Expected: `FAIL intro_toggle: no Read more button`.
- [ ] **Step 3: Implement.**
  - **Markup:** `<button type="button" class="intro-toggle" aria-expanded="false" aria-controls="about-intro" hidden>Read more</button>`.
  - **CSS:**
    - `.about-intro.is-collapsed`: `max-height: 4.8em` (about three lines), `overflow: hidden`, `cursor: pointer`, and `mask-image: linear-gradient(#000 40%, transparent)` with the `-webkit-` prefix.
    - `.intro-toggle`: a text button with no border or background, `--c-accent`, weight 700, `var(--fs-sm)`, and a small top margin.
    - In the About block's `@media (min-width: 992px)`: `.about-intro.is-collapsed { max-height: none; mask-image: none; -webkit-mask-image: none; cursor: auto; }` and `.intro-toggle { display: none; }`.
  - **JS:** add a `/** About intro: collapsed on phones, Read more / Show less */` block in the IIFE.
    - `const wide = window.matchMedia("(min-width: 992px)")`.
    - On init: remove `hidden` from the button and add `is-collapsed` to the intro.
    - `setOpen(open)`: toggles `is-collapsed`, sets `aria-expanded` and swaps the label between `"Read more"` and `"Show less"`.
    - Clicking the button toggles.
    - Clicking the intro toggles only when `!wide.matches` and it's still collapsed. Opening is the tap target; closing goes through the button, so selecting text doesn't collapse it.
- [ ] **Step 4: Run the whole suite.** Run `python3 tools/check_site.py`. Expected: all PASS.
- [ ] **Step 5: No commit.**

---

### Task 5: Skills divider, desktop two-column layout, old styles gone

**Files:**
- Modify: `index.html` (`h3.about-subtitle` "Skills" becomes `h3.skills-divider`)
- Modify: `css/style.css`
- Test: `tools/check_site.py`

**Interfaces:**
- Consumes: `.about-profile`, `.profile-card`, `.profile-body` (Task 2) and `.about-socials` (Task 3)

- [ ] **Step 1: Write the failing tests.**

```python
@check
def skills_divider():
    sec = section("about")
    assert '<h3 class="skills-divider">Skills</h3>' in sec, "no Skills divider heading"
    assert ".skills-divider::before" in css() and ".skills-divider::after" in css(), "divider lines"
    assert re.search(r"\.about \.skill-group\s*{[^}]*text-align:\s*center", css()), "skill groups not centered"


@check
def about_old_removed():
    sec, c = section("about"), css()
    for cls in ("about-top", "about-photo", "info-list", "contact-card", 'class="facts"', "about-subtitle"):
        assert cls not in sec, "old markup %s" % cls
    for sel in (".about-top", ".about-photo", ".info-list", ".contact-card", ".about .fact", ".about-subtitle"):
        assert sel not in c, "dead CSS %s" % sel


@check
def about_desktop_grid():
    m = re.search(r"@media \(min-width: 992px\)\s*{[^@]*?\.about \.about-profile\s*{([^}]*)}", css(), re.S)
    assert m and "grid-template-columns: 320px minmax(0, 1fr)" in m.group(1), "no two-column desktop profile"
    m = re.search(r"@media \(min-width: 992px\)\s*{[^@]*?\.about \.skills\s*{([^}]*)}", css(), re.S)
    assert m and "repeat(4, minmax(0, 1fr))" in m.group(1), "skills not four columns on desktop"
```

- [ ] **Step 2: Run them.** Run `python3 tools/check_site.py -k skills_divider`, `-k about_old` and `-k about_desktop`. Expected: all FAIL. `about_old_removed` fails on `about-subtitle`.
- [ ] **Step 3: Implement.**
  - **Skills divider:**
    - Swap the heading. `.about .skills-divider` is flex, centered, with a `1rem` gap, `var(--fs-lg)`, weight 700, `#fff` and a margin of about 3rem 0 1.5rem.
    - `::before` and `::after`: `content: ""; flex: 1; height: 1px`. The gradients are `linear-gradient(90deg, transparent, var(--c-primary))` and the reverse.
  - **Skill groups:**
    - `.about .skill-group { text-align: center; }`, with its `h4` small, `var(--c-muted)` and weight 600.
    - `.about .skill-group .tags { justify-content: center; }`.
    - `.about .skills` is one column, `repeat(2, minmax(0, 1fr))` at ≥576px, and `repeat(4, minmax(0, 1fr))` at ≥992px.
    - Delete the old `.about-subtitle` and the 768px skills rules.
  - **Desktop (≥992px):**
    - `.about .about-profile`: `display: grid; grid-template-columns: 320px minmax(0, 1fr); gap: 3.5rem; align-items: start`.
    - `.profile-ring`: `width: 280px`.
    - `.about-details`: 2 × 2, so the `nth-child(n+3)` span resets to `auto`.
- [ ] **Step 4: Run the whole suite.** Run `python3 tools/check_site.py`. Expected: all PASS.
- [ ] **Step 5: No commit.**

---

### Task 6: Visual verification and hand-off

**Files:** none changed, unless the screenshots show a defect. A defect gets a failing check first if it can be expressed statically. Otherwise it's a ruling in the ledger plus a CSS fix.

- [ ] **Step 1: Run the whole suite.** Run `python3 tools/check_site.py > "$WS/final.txt"; tail -3 "$WS/final.txt"`. Expected: every line PASS, exit 0.
- [ ] **Step 2: Take the screenshots.** Run `tools/screens.sh about '#about'`, `tools/screens.sh about '#about' 700` and `tools/screens.sh about '#about' 1400` (all six sizes).
- [ ] **Step 3: Read each PNG and compare it against `about-details-v5.html`.** Expected:
  - **Ring and photo:** a round photo in a purple ring with a dark gap, about 2/3 of the width on phones and 280px on desktop.
  - **Name and tags:** the name is bold and not script. The two tags fit side by side at 390px and above, and wrap cleanly at 360px.
  - **Intro:** about three faded lines and a Read more button on phones and the 768/844 tablets. Full text and no button at 1280.
  - **Details:**
    - Phones: no Email row and no "(in progress)".
    - 1280: a 2 × 2 grid with both shown.
    - Birthday reads "April 2003 (23 years)".
  - **Numbers:** a row of 3 between rules.
  - **Social circles:**
    - Five circles with official logos: a white GitHub mark, blue LinkedIn and Telegram, the four-color Gmail M and the gradient Instagram glyph. If any of these is blank, that's Review Focus 1.
    - Spread across on phones, centered and close together at 1280.
  - **Skills:** the divider, then centered groups.
  - **Page:** no horizontal scrollbar at any size.
- [ ] **Step 4: Check the Contact landing.** It can't be screenshotted through `tools/frame.html`, which scrolls by its own offset. Load `http://localhost:8765/#contact` with `--window-size=390,844` and `--window-size=1280,800` in headless Firefox (`firefox --headless --no-remote --profile ~/snap/firefox/common/claude-prof --screenshot …`). The load handler calls `scrollto`. Expected: the numbers and the circles sit in the middle band of the shot.
- [ ] **Step 5: Final review.** Follow superpowers:executing-plans' final review, using the review package of the working-tree diff for the files above. There are no commits, so diff against `HEAD`.
- [ ] **Step 6: Hand off to Hadi.**
  - Send the screenshot paths and the rulings.
  - Ask for a manual tap test on his phone: Read more / Show less, and Contact in the hero.
  - Remind him that nothing is committed.
