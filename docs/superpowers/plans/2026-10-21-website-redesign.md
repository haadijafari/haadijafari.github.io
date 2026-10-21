# hadij.ir Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the single-page `hadij.ir` site so it is fast, truthful, current as of Oct 2026, and designed phone-first, following the approved design.

**Architecture:** It stays a static, single-file site (`index.html` + `css/base.css` + `css/style.css` + `js/main.js`) with vendored libraries and no build step. Two repo-local Python tools support the work: `tools/build_assets.py` generates every optimized asset (WebP images, WOFF2 fonts, cleaned SVG) from originals, and `tools/check_site.py` is the test suite (static assertions over `index.html` and the files it references, plus a page-weight budget). Layout is verified with headless Firefox screenshots.

**Tech Stack:** HTML, CSS (custom Bootstrap 5.3.3 build, unchanged), vanilla JS, Typed.js, GLightbox, Python 3 + Pillow + fontTools/brotli (installed), `pdftoppm`, Firefox (snap) headless.

**Spec:** `docs/superpowers/specs/2026-10-21-website-redesign-design.md`. Read it fully. It holds all copy, facts, URLs and decisions. This plan doesn't repeat copy the spec already fixes. It points to spec sections.

## Global Constraints

- **No commits.** Hadi said: "don't commit for now till I say so." Skip every git commit and do not stage. Leave changes in the working tree.
- No CDN, no build step, no package manager for the site. Everything served is committed in the repo (CLAUDE.md).
- Don't edit `vendors/bootstrap-5.3.3-dist/css/bootstrap.min.css`. New colors are CSS custom properties in `css/style.css`.
- Colors: primary `#8E05C2`, `#700B97`, dark `#3E065F`, accent `#c77dff`, background `#0b0b0f`, surface `#16161c`, border `#2a2a33`.
- Dark mode only (`data-bs-theme="dark"` stays).
- Tone: plain, confident, first person. No jokes, no hype, no unverifiable numbers, no percentages.
- Phone number appears nowhere (no `tel:`, no `wa.me`). No Twitter/X. No German except the footer quote.
- Instagram: `https://instagram.com/hadijafari.exe`, handle `@hadijafari.exe`. LinkedIn: `https://www.linkedin.com/in/haadijafari/`.
- The secret product is never named or described.
- Persian (Jalali) dates, in Persian digits, appear **only** in My Resume → Professional Experience and Education.
- Initial-view page weight on a phone is **≤ 600 KB** (as measured by `tools/check_site.py`).
- No horizontal scroll at 360, 390, 430, 768 or 1280 px widths.
- CSS keeps the `/*----- # Section -----*/` banner-comment convention. `base.css` = global/utilities, `style.css` = per-section.
- Original photos are never served. Only generated WebP derivatives are referenced from the page.
- Do not delete repo files except those this plan names explicitly. Cleanup candidates are listed for Hadi (Task 14).

## Review Focus

1. **A 360px phone with the long email address** in the About contact card and the info list. Expect it to wrap or ellipsize inside its card, with no page-wide horizontal scroll. → Task 6 screenshot at 360px.
2. **A landscape phone (844×390) opening the hero.** Expect the face fully visible and the text readable, not a sliver of coat. → Task 5 screenshot at 844×390.
3. **A keyboard-only visitor on the polaroid deck.** Expect to Tab to the deck, press Enter/Space to shuffle, and have the caption text change (announced via `aria-live`). → Task 11 check + manual keyboard test.
4. **A visitor with `prefers-reduced-motion: reduce`.** Expect no tilt/shuffle animation on the polaroids and no typing animation in the hero (static first role). → Tasks 5 and 11 checks.
5. **Hadi adding a new certificate later by copying a card.** Expect the counter to update with no edits, and a duplicated `descN` to be caught. → Task 8 check `cert_desc_unique` + `cert_count_fallback_matches`.

---

## File Structure

| File | Responsibility |
|---|---|
| `tools/check_site.py` (new) | Test suite: named checks over `index.html`, CSS and referenced files, plus the weight budget. `python3 tools/check_site.py [-k substring]` prints `PASS name` / `FAIL name: reason` and exits 1 on any failure. |
| `tools/screens.sh` (new) | `tools/screens.sh <label>` serves the repo on :8765 and saves headless Firefox screenshots at 360×800, 390×844, 430×932, 844×390, 768×1024 and 1280×800 to `~/snap/firefox/common/claude-prof/shots/<label>-<w>x<h>.png` (the snap Firefox can only write under `~/snap/firefox/common`). |
| `tools/build_assets.py` (new) | Idempotent generator. Reads originals and writes optimized outputs (paths below). Re-run it whenever an original changes or a certificate is added. |
| `index.html` | All content and markup, plus the inline SVG icon sprite at the top of `<body>`. |
| `css/base.css` | Tokens (`:root` custom properties), fonts, body, nav, back-to-top, icon class, section shell, section titles, buttons/pills, footer. |
| `css/style.css` | Per-section styles: hero, about, projects, certifications, resume, services, hobbies. |
| `js/main.js` | Nav (active state, mobile toggle, smooth scroll), back-to-top, Typed init, age, cert count, GLightbox init, polaroid deck, footer year. |

**Generated asset paths** (`tools/build_assets.py` → page):

| Source | Output |
|---|---|
| `images/hero/IMG_0154.jpg` | `images/hero/hadi-600.webp`, `images/hero/hadi-1200.webp` (crop: head-to-waist portrait, 2:3), `images/og-image.jpg` (1200×630, face centered) |
| `images/hobbies/{chess2.jpg,jiu-jitsu.jpg,music1.webp,brain.jpeg,friends2.jpg}` | `images/hobbies/{chess,martial-arts,guitar,learning,friends}.webp`, 480px long edge |
| `images/certifications/*` (the 9 currently used) + `resume/Docs/Machine Learning Foundations for Product Managers.pdf` (via `pdftoppm -r 110 -png -singlefile`) | `images/certifications/<slug>-thumb.webp` (480w) and `<slug>.webp` (1600w max) |
| `images/edu/{ATU.svg,sku.png,Sampad.png}` | `images/edu/atu.min.svg` (embedded `<image>`, `<metadata>`, `sodipodi:*`/`inkscape:*` removed), `images/edu/{sku,sampad}.webp` (200px) |
| `fonts/PinyonScript-Regular.ttf`, `fonts/Satisfy-Regular.ttf` | `fonts/pinyon-script.woff2`, `fonts/satisfy.woff2` (pyftsubset, Basic Latin + `&'`) |

Certificate slugs: `ml-foundations-duke`, `basic-python`, `advanced-python`, `python-oop`, `django-basic`, `git`, `frontend`, `c`, `ef-set`, `odoo`.

---

### Task 1: Test harness and screenshot tool

**Files:**
- Create: `tools/check_site.py`, `tools/screens.sh`

**Interfaces:**
- Produces: `check(name)` decorator registering `fn() -> None` (raises `AssertionError(reason)` to fail). Helpers: `html() -> str` (index.html text), `tags(name) -> list[dict]` (attrs of every `<name>` tag, via `html.parser`), `text() -> str` (visible text with tags stripped), `css() -> str` (base.css + style.css concatenated), `initial_weight() -> int` (bytes). Later tasks add checks by appending `@check` functions.
- `initial_weight()` = size of `index.html` + each `<link rel="stylesheet">` href + each `<script src>` + each `<img>` **without** `loading="lazy"` (its `src`) + each `url(...)` in `@font-face` rules in `css()` whose `font-family` is actually used elsewhere in `css()` + `url(...)` background images in `css()` under a `#hero` selector.

- [ ] **Step 1: Write the harness with the first checks:**
  - `refs_exist`: every local `src`/`href`/`srcset` URL in `index.html` and every `url()` in `css()` resolves to an existing file.
  - `weight_budget`: `initial_weight() <= 600_000`.
  - `no_template_leftovers`: none of `{{`, `{%` in `html()`.
- [ ] **Step 2: Run** `python3 tools/check_site.py`. Expected: `refs_exist` PASS, `no_template_leftovers` FAIL (the `{{ language.* }}` leftovers), and `weight_budget` FAIL (it reports a number above 600000; record it).
- [ ] **Step 3: Write `tools/screens.sh`.** It starts `python3 -m http.server 8765` in the repo root if the port is free, then for each size runs `firefox --headless --no-remote --profile ~/snap/firefox/common/claude-prof --window-size=W,H --screenshot <out> http://localhost:8765/`. `--window-size` sets the viewport, so the shots show the first screen. To check lower sections, the script also accepts an optional `#anchor` second argument appended to the URL.
- [ ] **Step 4: Run** `tools/screens.sh before`. Expected: 6 PNGs exist. View the 390 one; the current hero shows.

### Task 2: Asset pipeline

**Files:**
- Create: `tools/build_assets.py`
- Generated: all outputs in the table above

**Interfaces:**
- Consumes: originals listed above.
- Produces: the output paths above. `HERO_CROP = (left, top, right, bottom)` as a module constant in source-pixel coordinates of the EXIF-transposed 3549×5323 image, chosen so the 2:3 crop runs from just above the hair to the waist with the face in the upper third. Verify by viewing the output.

- [ ] **Step 1: Add check `assets_generated`.** Every output path in the table exists, and each WebP is under its cap: hero-600 ≤ 70 KB, hero-1200 ≤ 200 KB, hobby ≤ 60 KB, cert thumb ≤ 40 KB, cert full ≤ 250 KB, edu ≤ 15 KB, `atu.min.svg` ≤ 30 KB, each woff2 ≤ 40 KB. Run it. Expected FAIL (files missing).
- [ ] **Step 2: Implement `tools/build_assets.py`.** Use Pillow `ImageOps.exif_transpose`, `thumbnail` with LANCZOS, WebP `quality=78, method=6`. For the ATU SVG, strip with `xml.etree.ElementTree`: drop `<image>`, `<metadata>`, and attributes and elements in the sodipodi/inkscape namespaces. For fonts, use `fontTools.subset` with `flavor="woff2"`. For the PDF, run `pdftoppm` into a temp dir. If a size cap fails, lower `quality` for that output only.
- [ ] **Step 3: Run** `python3 tools/build_assets.py && python3 tools/check_site.py -k assets`. Expected: PASS.
- [ ] **Step 4: View** `hadi-600.webp`, `og-image.jpg` and `atu.min.svg` (open the SVG via the local server in a Firefox screenshot). Expected: face fully in frame, and the ATU logo looks identical to the original.

### Task 3: Strip dead weight and set up icons and fonts

**Files:**
- Modify: `index.html` (head links, scripts, preloader div, every `<i class="bi …">`, commented template blocks), `js/main.js` (remove preloader, Isotope, portfolio lightboxes, Waypoints skills block), `css/base.css` (remove `#preloader` rules, `.svg-devider`), `css/style.css` (remove all `@font-face` and font references except the new two)

**Interfaces:**
- Produces: icon markup `<svg class="icon" aria-hidden="true"><use href="#i-NAME"/></svg>`. Sprite: one hidden `<svg>` right after `<body>` containing `<symbol id="i-NAME" viewBox="0 0 16 16">`, with path data copied from `vendors/bootstrap-icons-1.11.3/NAME.svg`. Icon names used site-wide: `house-door person kanban patch-check file-earmark-person hdd-stack controller list x-lg chevron-down arrow-up-short arrow-up-right github linkedin envelope-fill telegram instagram download code-slash diagram-3 cart graph-up cpu diagram-2 zoom-in patch-check-fill mortarboard briefcase` (add others only when a task needs them). `.icon { width:1em; height:1em; fill:currentColor; vertical-align:-.125em; }` in base.css.
- Produces: font families `"Pinyon Script"` (`fonts/pinyon-script.woff2`) and `"Satisfy"` (`fonts/satisfy.woff2`), both `font-display: swap`, declared in base.css. Body font: system UI stack `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` (no new font download).

- [ ] **Step 1: Add checks:**
  - `no_dead_libs`: no `isotope`, `waypoints`, `purecounter`, `bootstrap.bundle`, `bootstrap-icons` or `preloader` in `html()`.
  - `icons_defined`: every `#i-NAME` referenced by `<use>` has a matching `<symbol id>`.
  - `fonts_used_only`: `@font-face` families in `css()` are exactly {Pinyon Script, Satisfy}.
  - `no_undefined_fonts`: no `Raleway`/`Poppins` in `css()`.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement.** PureCounter is removed: the counts become static text (Task 6). Keep Typed.js and GLightbox `<script>` tags, with `defer` on all scripts. Keep `js/main.js`'s IIFE structure, `select`/`on` helpers and the banner comments.
- [ ] **Step 3: Run** `python3 tools/check_site.py`. Expected: the four new checks PASS, and `refs_exist` still passes.
- [ ] **Step 4: Delete** these unused vendor folders, which this plan names explicitly: `vendors/isotope-docs`, `vendors/waypoints`, `vendors/purecounter`, `vendors/aos`, `vendors/aos-next`, `vendors/bootstrap-icons` (the older duplicate). Keep `vendors/bootstrap-icons-1.11.3` as the SVG source. Re-run `refs_exist`. Expected: PASS.

### Task 4: Foundation: tokens, section shell, titles, nav

**Files:**
- Modify: `css/base.css`, `index.html` (`<header>` nav, every `<section>` class list), `js/main.js` (nav)

**Interfaces:**
- Produces CSS tokens on `:root` in base.css: `--c-primary:#8E05C2; --c-primary-2:#700B97; --c-primary-dark:#3E065F; --c-accent:#c77dff; --c-bg:#0b0b0f; --c-surface:#16161c; --c-border:#2a2a33; --c-text:#ececf1; --c-muted:#a8a8b3; --radius:14px; --shell-pad: clamp(1rem, 4vw, 3rem);`
- Produces classes used by every later task: `.section` (vertical rhythm, `padding-inline: var(--shell-pad)`, no fixed side margins), `.section-title` (eyebrow `<span>` in small caps accent + `<h2>` sans + optional `<p>` muted; the giant script watermark is removed), `.card` (surface, border, radius, hover border `--c-primary`), `.pill` (rounded-full, surface bg, icon in accent), `.btn-primary-pill`, `.btn-outline-pill`, `.tag` (small outlined chip).
- Nav order and ids: `#hero` Home (`house-door`), `#about` About (`person`), `#projects` Projects (`kanban`), `#certifications` Certifications (`patch-check`), `#resume` Resume (`file-earmark-person`), `#services` Services (`hdd-stack`), `#hobbies` Hobbies (`controller`). The mobile toggle becomes a `<button class="mobile-nav-toggle" aria-label="Open menu" aria-expanded="false">` that swaps `list`/`x-lg` icons and updates `aria-expanded`.

- [ ] **Step 1: Add checks:**
  - `nav_matches_sections`: nav `href`s equal the ordered list above, and each id exists as a `<section>` (Projects fails until Task 7; list it as an expected failure in the output until then).
  - `no_typos`: "Hobbbies" absent.
  - `toggle_is_button`: an element with class `mobile-nav-toggle` is a `<button>` with `aria-label`.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement** tokens, shell, titles and nav restyle in the purple/black direction. Nav structure stays (desktop left rail of 56px pills, mobile drawer). Every interactive element (nav links, toggle, pills, buttons, cards that link) gets a tap target of at least 44×44px. Each later section task rewrites its own section intro per the spec's tone.
- [ ] **Step 3: Run checks** (`no_typos`, `toggle_is_button` PASS). Then `tools/screens.sh t4`. Expected at 360/390: no horizontal scroll, sections use the full width minus the gutter, and the drawer opens and closes.

### Task 5: Hero (split layout)

**Files:**
- Modify: `index.html` `#hero`, `css/style.css` `# Hero`, `js/main.js` Typed init

**Interfaces:**
- Consumes: `hadi-600.webp`/`hadi-1200.webp` (Task 2), `.btn-*-pill`, `.pill`, `.icon` (Tasks 3–4), and the social pill row partial markup defined here.
- Produces: `.social-pills` markup (a `<ul>` of five `<a class="pill">` items, in the order and with the URLs of spec § About → Social links), reused verbatim in the footer (Task 12).

- [ ] **Step 1: Add checks:**
  - `hero_image`: `#hero img` has `srcset` containing both hero WebPs, `sizes`, `width`, `height`, non-empty `alt`, `fetchpriority="high"`, and no `loading="lazy"`.
  - `hero_copy`: `text()` contains the name, the three typed roles (exact strings from spec § Hero) in `data-typed-items`, and the tagline verbatim.
  - `social_links_exact`: across the page, social anchors' hrefs ⊆ {the five spec URLs}, Instagram is `hadijafari.exe`, and no `x.com`/`twitter`/`wa.me`/`tel:`.
  - `reduced_motion_typed`: `main.js` reads `matchMedia('(prefers-reduced-motion: reduce)')` before creating Typed.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement the layout.**
  - Desktop (≥992px): a 2-column grid, text left. The photo is right, ~46% wide, full viewport height, `object-fit: cover; object-position: 50% 20%`. A left-edge `linear-gradient(90deg, var(--c-bg), transparent 35%)` overlay, and a faint radial purple glow (`radial-gradient(… rgba(142,5,194,.25) …)`) behind the subject.
  - Phone: photo on top at `55svh`, a bottom fade to `--c-bg`, text below.
  - Landscape phones (`max-height: 500px` and landscape): use the desktop split so the face isn't cropped.
  - Buttons: Download CV (`resume/hadi_jafari_resume.pdf`, `download="Hadi Jafari Resume.pdf"`) and Contact (`href="#contact"`, the About contact-cards block id). Social pills sit below them.
  - Under reduced motion, show the first role as static text and skip Typed.
- [ ] **Step 3: Run checks.** Expected PASS. Run `tools/screens.sh t5`.
- [ ] **Step 4: Verify the screenshots** at all six sizes, especially **844×390** and **360×800**. The face is fully visible, the text doesn't overlap the face on desktop, and nothing scrolls horizontally.

### Task 6: About (text, info list, contact cards, counts, skills)

**Files:**
- Modify: `index.html` `#about`, `css/style.css` `# About`, `js/main.js` (age, cert count)

**Interfaces:**
- Consumes: `.card`, `.tag`, `.icon`.
- Produces: `id="contact"` on the contact-cards wrapper (the hero's Contact button targets it). `<span id="cert-count">N</span>`, where N is the static fallback count in the HTML. `countCertificates(): number` in main.js = `document.querySelectorAll('#certifications .cert-card').length`, written into `#cert-count` on `DOMContentLoaded`. Task 8 gives each certificate card the `cert-card` class.
- Age: `ageFrom(year=2003, monthIndex=3) -> number`, which subtracts 1 if the current month is before April.

- [ ] **Step 1: Add checks:**
  - `about_copy`: the heading "Django Developer → AI & Machine Learning" and both intro paragraphs, verbatim from spec § About.
  - `info_list`: contains "Isfahan, Iran", "Available", a `mailto:haadijafari2003@gmail.com` link, and no `Persia`, `Unknown` or `Phone`.
  - `no_inflated_stats`: none of `100`, `Awards`, `Coffee`, `∞`, `Years of Experience` appear in `#about`. Contains `3+`, `17.57`, `MSc`, `id="cert-count"`.
  - `no_percent_bars`: no `progress-bar` and no `%` inside `#about`.
  - `skills_groups`: the four group headings and every tool listed in spec § Skills.
  - `no_nowrap_overflow`: no `text-nowrap` inside `#about`.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement.**
  - Info list: CSS grid, label/value pairs, 1 column below 576px.
  - Contact cards: `grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr))`. Handles use `overflow-wrap: anywhere`.
  - Counts: four `.card` stats with the exact labels from spec § Counts.
  - Skills: four groups of `.tag` chips.
  - Remove the Download CV button from About (it now lives in the hero).
- [ ] **Step 3: Run checks.** Expected PASS. Run `tools/screens.sh t6 '#about'`. **Verify at 360×800** that the email card and the email in the info list stay inside their boxes (Review Focus 1).

### Task 7: Projects (new section)

**Files:**
- Modify: `index.html` (new `<section id="projects">` after About), `css/style.css` (`# Projects`)

**Interfaces:**
- Consumes: `.card`, `.tag`, `.icon`.
- Produces: `.project-card` markup: `<article class="card project-card">` containing `h3`, a summary `p`, a `.project-result` line, a `ul.tags`, and an `a` with "View on GitHub" + `arrow-up-right`. Adding the secret product later = copying one `<article>`.

- [ ] **Step 1: Add check `projects`:** a section `#projects` with exactly three `.project-card`s in spec order. Each card's link equals its repo URL, "R² 0.822" appears in card 1, and the secret product name appears nowhere (checked by hash). Run it. Expected FAIL.
- [ ] **Step 2: Implement** with copy from spec § Projects. Grid: 1 column on phones, 3 on ≥992px. Text-only cards (skip the Tetris GIF).
- [ ] **Step 3: Run checks.** `projects` and `nav_matches_sections` PASS. Run screenshots at `'#projects'`.

### Task 8: Certifications

**Files:**
- Modify: `index.html` `#certifications`, `css/style.css` `# Certifications`, `js/main.js` (GLightbox init only)

**Interfaces:**
- Consumes: cert WebPs (Task 2), `countCertificates()` (Task 6).
- Produces: card markup, one per certificate. Exactly one anchor per card, no nested anchors:
  `<a class="card cert-card certifications-lightbox" href="images/certifications/<slug>.webp" data-gallery="certificationsGallery" data-glightbox="title: …; description: .descN">` containing `<img src="…-thumb.webp" loading="lazy" decoding="async" width height alt>` and the title, followed by its `<div class="glightbox-desc descN">`.

- [ ] **Step 1: Add checks:**
  - `cert_desc_unique`: every `descN` class referenced in `data-glightbox` exists exactly once as a `.glightbox-desc`.
  - `cert_count_fallback_matches`: the number in `#cert-count` equals the count of `.cert-card`.
  - `cert_new`: the first card is the Duke/Coursera one, and its description contains the `https://coursera.org/verify/6DB82NPQSW6L` link.
  - `cert_efset_title`: the title "English: EF SET C2 Proficient".
  - `imgs_lazy_sized`: every `<img>` outside `#hero` has `loading="lazy"`, `width`, `height` and a non-empty `alt`.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement.** Order: Duke ML first, then the existing order. Keep the existing descriptions (hours, provider link, instructor), restyled as a small definition list. The Duke description is "From: Duke University (Coursera)" plus a Verify link. Grid: 2 columns on phones, up to 5 on desktop.
- [ ] **Step 3: Run checks.** Expected PASS. Open the page locally in a browser (`python3 -m http.server 8765`) and click a card. The lightbox opens with its description, and arrows move through all 10.

### Task 9: My Resume (languages, experience, education)

**Files:**
- Modify: `index.html` `#resume`, `css/style.css` `# Resume`

**Interfaces:**
- Produces: date markup `<p class="resume-date"><strong>2021 – 2025</strong> <span class="jalali" lang="fa" dir="rtl">۱۴۰۰ – ۱۴۰۴</span></p>`. `.jalali` is `--c-muted`, `0.85em`. Exact pairs:
  - CTO: `2026 – Present` / `۱۴۰۵ – اکنون`
  - Django dev: `2023 – Present` / `۱۴۰۲ – اکنون`
  - MSc: `2026 – Present` / `۱۴۰۵ – اکنون`
  - BSc: `2021 – 2025` / `۱۴۰۰ – ۱۴۰۴`
  - Diploma: `2018 – 2021` / `۱۳۹۷ – ۱۴۰۰`
- Logos: `<span class="edu-logo">` white rounded tile (`background:#fff; border-radius:12px; padding:8px`) around `atu.min.svg`, `sku.webp` or `sampad.webp`.

- [ ] **Step 1: Add checks:**
  - `jalali_only_in_resume`: Persian digits `[۰-۹]` appear only inside `#resume .resume-date` (excluding the footer quote, which has none).
  - `resume_content`: the CTO entry, "Vira Kavane Zista", "17.57 / 20", "Allameh Tabataba'i", "Shahrekord University", and the languages line "C2 Proficient", "EF SET 76/100", "Native". No `German`, no `Shahr-e Kord`, no `two years`.
  - `newest_first`: in Experience, CTO precedes the Django dev; in Education, MSc precedes BSc precedes Diploma.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement** with copy from spec § My Resume. Rewrite the Django-dev paragraph per spec (no year count). Layout: Experience and Education stacked on phones, two columns on ≥992px. Languages is a single line above them.
- [ ] **Step 3: Run checks.** Expected PASS. Screenshot `'#resume'` at 390 and 1280. The Persian dates render right-to-left, lighter, beside the Gregorian dates, and the logos sit on white tiles.

### Task 10: Services

**Files:**
- Modify: `index.html` `#services`, `css/style.css` `# Services`

- [ ] **Step 1: Add check `services`:** exactly six `.service-card`s, titles in spec order, and the sixth is "Architecture & Refactoring" with the spec description verbatim. No "Automation". Run it. Expected FAIL.
- [ ] **Step 2: Implement** `.card.service-card` (icon, `h3`, `p`). Icons: `code-slash`, `diagram-3`, `cart`, `graph-up`, `cpu`, `diagram-2`. Write a plain one-line intro. Grid: 1 / 2 / 3 columns.
- [ ] **Step 3: Run check.** Expected PASS. Screenshot `'#services'`.

### Task 11: Hobbies (polaroid deck)

**Files:**
- Modify: `index.html` `#hobbies`, `css/style.css` `# Hobbies`, `js/main.js` (`# Hobbies deck`)

**Interfaces:**
- Consumes: hobby WebPs (Task 2), Satisfy font (Task 3).
- Produces markup: `<div class="polaroids" data-deck>` with five `<figure class="polaroid" data-text="…">` elements, each holding `<img>` + `<figcaption>`, in spec order (Chess, Martial Arts & Workout, Guitar, Learning, Friends). Then `<button class="deck-shuffle" type="button" aria-label="Show next hobby">` (on phones it covers the stack), `<p class="deck-text" aria-live="polite">`, and `<p class="deck-hint">Tap to shuffle</p>`.
- Produces `initDeck(root: HTMLElement): void` in main.js. Phones (<768px): stacked absolutely, the top card straight and the rest tilted by the fixed angles `[-4, 5, -8, 7, -2]`. Clicking or activating the button moves the top card to the back and sets `.deck-text` to the new top card's `data-text`. Desktop (≥768px): the cards are spread in a row with overlap and tilt. `:hover`/`:focus-within` lifts (translateY −8px), straightens, and shows that card's text. Each figure gets `tabindex="0"` on desktop.

- [ ] **Step 1: Add checks:**
  - `hobbies_content`: five `.polaroid`s in spec order. The second caption is exactly "Martial Arts & Workout". No `belt` and no `accordion` in `#hobbies`.
  - `deck_a11y`: the `.deck-shuffle` `<button>` exists with `aria-label`, and the `.deck-text` has `aria-live`.
  - `reduced_motion_deck`: `css()` has a `prefers-reduced-motion: reduce` block that sets `transition: none` for `.polaroid`.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement.** Use the draft texts from spec § Hobbies as `data-text`. Hadi reviews wording at the end. Captions are in Satisfy on an off-white frame (`#f3efe6`) with dark text. On phones, the section's height must stay ≤ ~45svh including the text.
- [ ] **Step 3: Run checks.** Expected PASS. Screenshot `'#hobbies'` at 390 and 1280.
- [ ] **Step 4: Manual keyboard test** in a real browser at 390 width (devtools). Tab to the shuffle button and press Enter, then Space. Each press shows the next hobby and its text changes. At 1280, Tab moves through the cards and each lifts and shows its text (Review Focus 3).

### Task 12: Footer

**Files:**
- Modify: `index.html` footer, `css/base.css` `# Footer Section`, `js/main.js` (year)

- [ ] **Step 1: Add check `footer`:**
  - Contains `.social-pills` with the same five hrefs as the hero.
  - Contains `<span id="year">2026</span>`.
  - The German quote text „Ich habe gelitten, gelernt und mich verändert" is present, with no `translate.google` link.
  - No `2023`.
  - No `footer-top.svg`.
  Also add `no_jokey_intros`: none of "Don't you know who I am", "missing piece of puzzle", "People have hobbies", "Services I can provide you", "I've attended in some courses" in `html()`. Every earlier section task must already have replaced its intro, so a failure here points to the section that missed it.
  Run them. Expected: `footer` FAIL, and `no_jokey_intros` PASS.
- [ ] **Step 2: Implement.** `main.js` sets `#year` to `new Date().getFullYear()`. Give the quote a `title="I have suffered, learned and changed"` tooltip and `lang="de"`.
- [ ] **Step 3: Run check.** Expected PASS.

### Task 13: Metadata, JSON-LD, sitemap

**Files:**
- Modify: `index.html` `<head>`, `sitemap.xml`

- [ ] **Step 1: Add checks:**
  - `jsonld`: parse the `ld+json` block. `sameAs` == [GitHub, `https://www.linkedin.com/in/haadijafari/`, `https://instagram.com/hadijafari.exe`]. `knowsLanguage` == ["English", "Persian"]. `worksFor.name` == "Vira Kavane Zista". `alumniOf` names include "Shahrekord University". Allameh Tabataba'i University is present as `affiliation`.
  - `og_meta`: `og:image` == `https://hadij.ir/images/og-image.jpg`. The title and description mention Django and AI.
  - `sitemap`: `#projects` is listed, and the anchors equal the nav ids except `#hero`.
  Run them. Expected FAIL.
- [ ] **Step 2: Implement.** Title: `Hadi Jafari | Django Developer · AI & ML`. Write the description in the spec's tone. `jobTitle`: ["Co-founder & CTO", "Django Developer"]. Update `knowsAbout`.
- [ ] **Step 3: Run checks.** Expected PASS.

### Task 14: Cleanup list for Hadi (no deletion)

**Files:**
- Create: `docs/superpowers/plans/2026-10-21-cleanup-candidates.md`

- [ ] **Step 1: List every file under `images/`, `fonts/` and the repo root (excluding `vendors/` handled in Task 3, `tools/` and `docs/`) not referenced by `index.html`, the CSS, `sitemap.xml` or `images/favicon/site.webmanifest`.** Do it with a one-off command that reuses `check_site.py`'s reference extraction. Include each file's size and the total. Flag originals that `build_assets.py` needs (they must stay, or move out of the served tree if Hadi prefers).
- [ ] **Step 2: Stop and ask Hadi** which to delete. Do not delete anything in this task.

### Task 15: Final verification

- [ ] **Step 1: Run** `python3 tools/check_site.py`. Expected: every check PASS, with `weight_budget` reporting ≤ 600000. Paste the full output into the hand-back.
- [ ] **Step 2: Run** `tools/screens.sh final` for each anchor (none, `#about`, `#projects`, `#certifications`, `#resume`, `#services`, `#hobbies`). View all of them. Check for no horizontal overflow, readable text, faces not cropped, and a consistent purple/black look.
- [ ] **Step 3: Run** the Review Focus items 1–5 once more by hand. For item 4, emulate reduced motion with Firefox devtools → Rendering.
- [ ] **Step 4: Report to Hadi.** Include the before/after weight, the screenshot paths, the list of copy he should review (About intro, Django-dev paragraph, section intros, hobby texts, meta description), and a reminder that `resume/hadi_jafari_resume.pdf` is still the old CV. Don't commit.
