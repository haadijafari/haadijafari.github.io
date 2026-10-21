# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal portfolio/resume site for Hadi Jafari, served by GitHub Pages at the custom domain in `CNAME` (`hadij.ir`). It is a plain static site: there is no build step, package manager, or linter (the test suite is `tools/check_site.py`, see below). Everything the page needs, third-party libraries included, is committed to the repo, and nothing loads from a CDN.

Preview locally by serving the repo root, for example `python3 -m http.server 8000`, then opening http://localhost:8000.

## Architecture

- **Single page.** All content is in `index.html`. Each section is a `<section id="...">` (`hero`, `about`, `projects`, `certifications`, `resume`, `services`, `hobbies`). The nav links use the `.scrollto` class and point at these ids. The JSON-LD `@graph` in `<head>` (WebSite, ProfilePage, Person) repeats the profile facts (roles, schools, languages, social links), so update it when a profile fact changes. `sitemap.xml` lists only `https://hadij.ir/` (fragment URLs are duplicates to Google); bump its `<lastmod>` when content changes.
- **Libraries in `vendors/`.** `index.html` loads them with `<script>`/`<link>` tags, and `js/main.js` initializes them. The behavior is driven from HTML attributes:
  - Typed.js: hero roles come from `data-typed-items` (comma-separated) on `.typed`.
  - GLightbox: every certificate is an `<a class="certifications-lightbox" data-gallery="certificationsGallery" data-glightbox="title: ...; description: .descN">` linked to a `<div class="glightbox-desc descN">` (hidden by `css/base.css`, since the GLightbox CSS loads deferred). A new certificate needs a unique `descN` class. Its full image and `-thumb.webp` go in `images/certifications/`.
  - Certifications: highlighted certificates are `<a class="cert-card ...">` cards in `.cert-rail` (styled like project cards, with inline `--glow-1`/`--glow-2`). The rest are `.cert-row` links in `.cert-list`. To feature or unfeature one, move its markup between the two. A CSS counter numbers cards and rows in order. `js/main.js` builds the phone swipe-row dots from the cards. The About "certificates" count counts every `.certifications-lightbox`.
  - Projects: each `<article class="project-card">` in `[data-projects]` is one card (its glow colors come from the inline `--glow-1`/`--glow-2`). `js/main.js` builds the counter, dots, and the desktop contents list from the cards, so a new project only needs a new card. Phones get a swipeable deck; at 992px and up, a list plus fanned cards.
  - The age shown in About is computed in `js/main.js` by `ageFrom(2003, 3)` (year and 0-based month); the footer year is set there too.
- **No CSS framework.** Styles are self-contained. `css/base.css` starts with a small reset (the parts of Bootstrap Reboot the page relied on), then the color/type tokens on `:root` (the palette lives there, e.g. `--c-primary`, `--c-bg`), and ends with the few layout utilities `index.html` uses (`.container`, `.d-flex`, `.d-lg-none`, `.visually-hidden`, ...). The page is dark only (`color-scheme: dark`).
- **Styles.** `css/base.css` holds the reset, tokens, global components and utilities (back-to-top, cards, pills, etc.). `css/style.css` holds per-section styles. Both use the `/*----- # Section -----*/` banner-comment convention.
- **Tools (`tools/`, not published).** `check_site.py` is the test suite: run `python3 tools/check_site.py` (or `-k <name>`) after every change; it must exit 0. `build_assets.py` regenerates every served WebP/SVG/WOFF2 from the originals kept in the repo (e.g. `images/certifications/*.jpg|png`, `images/svg/footer-top.svg`, `fonts/*.ttf`). `screens.sh` takes headless Firefox screenshots; clear `~/snap/firefox/common/claude-prof/cache2` first, or it may render stale CSS.

## Resume files

The "Download CV" button links to `resume/hadi_jafari_resume.pdf`. The editable source is `resume/CV.odt` (unpublished). The Persian/English `resume/هادی_جعفری-*.pdf` versions are the only other CVs.

## Publishing

GitHub Pages publishes the whole repo except what `_config.yml` lists under `exclude` (`docs/`, `tools/`, `CLAUDE.md`, `resume/CV.odt`, ...). Add any new private or dev-only path there. Don't add a `.nojekyll` file: it would disable that filter. `404.html` must use root-absolute paths (`/css/...`), because Pages serves it at any missing URL.

## Git conventions

- Commit subjects use a bracketed tag plus a Title Case summary: `[ADD] ...`, `[FIX] ...`, `[UPDATE] ...`.
- Every file in the working copy is mode 777, so this clone has `core.fileMode false`. Still stage specific files rather than `git add -A`.
