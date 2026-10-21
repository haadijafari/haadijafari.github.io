# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Personal portfolio/resume site for Hadi Jafari, served by GitHub Pages at the custom domain in `CNAME` (`hadij.ir`). It is a plain static site: there is no build step, package manager, linter, or test suite. Everything the page needs, third-party libraries included, is committed to the repo, and nothing loads from a CDN.

Preview locally by serving the repo root, for example `python3 -m http.server 8000`, then opening http://localhost:8000.

## Architecture

- **Single page.** All content is in `index.html`. Each section is a `<section id="...">` (`hero`, `about`, `projects`, `certifications`, `resume`, `services`, `hobbies`). The nav links use the `.scrollto` class and point at these ids. `sitemap.xml` lists the same anchors, and the JSON-LD `Person` block in `<head>` repeats the profile facts (roles, schools, languages, social links). When a section or a profile fact changes, update all of these together.
- **Libraries in `vendors/`.** `index.html` loads them with `<script>`/`<link>` tags, and `js/main.js` initializes them. The behavior is driven from HTML attributes:
  - Typed.js: hero roles come from `data-typed-items` (comma-separated) on `.typed`.
  - PureCounter: the "Counts" stats use `data-purecounter-*` attributes on `.purecounter`.
  - Waypoints: skill progress bars animate to their `aria-valuenow` value when scrolled into view.
  - GLightbox: every certificate is an `<a class="certifications-lightbox" data-gallery="certificationsGallery" data-glightbox="title: ...; description: .descN">` linked to a hidden `<div class="glightbox-desc descN">`. A new certificate needs a unique `descN` class. Its full image and `-thumb.webp` go in `images/certifications/`.
  - Certifications: highlighted certificates are `<a class="cert-card ...">` cards in `.cert-rail` (styled like project cards, with inline `--glow-1`/`--glow-2`). The rest are `.cert-row` links in `.cert-list`. To feature or unfeature one, move its markup between the two. A CSS counter numbers cards and rows in order. `js/main.js` builds the phone swipe-row dots from the cards. The About "certificates" count counts every `.certifications-lightbox`.
  - Projects: each `<article class="project-card">` in `[data-projects]` is one card (its glow colors come from the inline `--glow-1`/`--glow-2`). `js/main.js` builds the counter, dots, and the desktop contents list from the cards, so a new project only needs a new card. Phones get a swipeable deck; at 992px and up, a list plus fanned cards.
  - The age shown in About is computed in `js/main.js` from a hardcoded `birthYear`.
- **No CSS framework.** Styles are self-contained. `css/base.css` starts with a small reset (the parts of Bootstrap Reboot the page relied on), then the color/type tokens on `:root` (the palette lives there, e.g. `--c-primary`, `--c-bg`), and ends with the few layout utilities `index.html` uses (`.container`, `.d-flex`, `.d-lg-none`, `.visually-hidden`, ...). The page is dark only (`color-scheme: dark`).
- **Styles.** `css/base.css` holds global and utility styles (back-to-top, preloader, etc.). `css/style.css` holds per-section styles. Both use the `/*----- # Section -----*/` banner-comment convention.
- **Template leftovers.** The page started as a Django/Jinja template. Comments like `{% include "./index-portfolio.html" %}` and the portfolio/Isotope code in `main.js` are inactive, because the page has no portfolio section. `images/portfolio/` is likewise unused.

## Resume files

The "Download CV" button links to `resume/hadi_jafari_resume.pdf`. The editable source is `resume/CV.odt`. The repo also contains other resume PDFs (`resume.pdf` at the root, `resume/Resume.pdf`, `resume/resume.pdf`, and the Persian/English `هادی_جعفری-*.pdf`). When updating "the resume", check which file is actually linked.

## Git conventions

- Commit subjects use a bracketed tag plus a Title Case summary: `[ADD] ...`, `[FIX] ...`, `[UPDATE] ...`.
- The working copy sits on a filesystem where every file is mode 777 and `core.fileMode` is `true`, so `git status` shows nearly every file as modified with mode-only changes. Do not stage these. Stage specific files rather than `git add -A`, or ask the user about running `git config core.fileMode false`.
