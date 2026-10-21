# Personal SEO & Entity Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish `https://hadij.ir` and `https://github.com/haadijafari` as the authoritative #1 Google search results for **"Hadi Jafari"**, unifying personal identity in Google's Knowledge Graph across domain, GitHub, and social channels.

**Architecture:** Plain static portfolio served by GitHub Pages at `hadij.ir`. The implementation embeds verified entity schema markup (Schema.org `Person`, `ProfilePage`, `WebSite`), explicit `rel="me"` bidirectional identity links, entity profile image assets, and generates the companion GitHub profile repository assets and Google Search Console / indexing verification procedures. All site changes are guarded by the repo's test suite `tools/check_site.py`.

**Tech Stack:** HTML5, Schema.org JSON-LD (`@graph`), CSS3, vanilla JS, Python 3 (`tools/check_site.py` with `fonttools` and `brotli`), GitHub Pages, Git.

**Spec:** `/home/hadi/Documents/personal_seo_implementation_plan.md`

## Global Constraints

- Site URL is strictly `https://hadij.ir/` (with trailing slash) in canonical, `og:url`, JSON-LD `url`, and `sitemap.xml`.
- Theme color everywhere is `#0b0b0f` (`--c-bg` token).
- All site assets must remain local to the repository; no external CDN links.
- Single `<h1>` tag on the homepage containing `Hadi Jafari`.
- Git commit conventions: `[TAG]` plus Title Case summary (e.g. `[ADD] ...`, `[FIX] ...`, `[UPDATE] ...`).
- Never `git add -A`. Stage named files explicitly.
- Run tests via `uv run --with fonttools --with brotli python tools/check_site.py` (or `-k <name>`). Must exit code `0` cleanly.

## Review Focus

1. **Title & Meta Tag Keyword Balance**: Preserving required primary keywords ("Hadi Jafari", "Django", "AI & ML") while explicitly introducing the handle (`haadijafari`) and engineer role so neither search ranking nor `check_site.py` assertions regress.
2. **Schema `@graph` Integrity**: Ensuring `alternateName` accepts both Persian script ("هادی جعفری") and aliases ("haadijafari", "Hadi J") without breaking JSON-LD syntax or dangling `@id` references.
3. **`rel="me"` Identity Verification**: Bidirectional identity linking between `hadij.ir` and `github.com/haadijafari` without altering UI button styling or breaking existing lightbox/icon layouts.
4. **Root Image Resolution (`hadi-jafari.jpg`)**: Ensuring `https://hadij.ir/hadi-jafari.jpg` is physically served from repo root or cleanly handled by Pages routing while maintaining image weight budget.
5. **Publish Hygiene and Jekyll Exclusions**: Ensuring newly created off-page documents and GitHub profile scaffolding in `docs/` remain excluded from GitHub Pages build by `_config.yml`.

---

### Task 1: Update Test Suite (`tools/check_site.py`) with SEO Entity Assertions

Add test checks to `tools/check_site.py` that enforce the new entity requirements: `profile:username` meta tag, `rel="me"` on GitHub and LinkedIn links, expanded JSON-LD `alternateName` array, and `hadi-jafari.jpg` entity image.

**Files:**
- Modify: `tools/check_site.py`

**Interfaces:**
- Consumes: Existing check functions in `tools/check_site.py`
- Produces: Stricter SEO checks in `head_meta`, `og_meta`, `social_links_exact`, `jsonld`, and `jsonld_graph`

- [ ] **Step 1: Write the updated assertions in `tools/check_site.py`**

In `tools/check_site.py`:
1. In `head_meta()`: Add assertion that `m.get("profile:username") == "haadijafari"`.
2. In `og_meta()`: Ensure title starts with `"Hadi Jafari"`, description contains `"haadijafari"`, and title and description continue to include `"Django"` and `"AI"`.
3. In `social_links_exact()`: Assert that the GitHub link `a` tag has `rel` containing both `"me"` and `"noopener"`, and LinkedIn has `rel` containing both `"me"` and `"noopener"`.
4. In `jsonld()`: Assert `d.get("givenName") == "Hadi"`, `d.get("familyName") == "Jafari"`, and `d.get("alternateName")` contains `"haadijafari"` and `"هادی جعفری"`.
5. Add `@check def seo_entity_image()`: Assert `os.path.exists(os.path.join(ROOT, "hadi-jafari.jpg"))` or `os.path.exists(os.path.join(ROOT, "images/hadi-jafari.jpg"))`.

- [ ] **Step 2: Run test suite to verify the new checks fail**

Run:
```bash
uv run --with fonttools --with brotli python tools/check_site.py -k head_meta -k og_meta -k social_links_exact -k jsonld -k seo_entity_image
```
Expected: FAIL with missing `profile:username`, `rel="me"`, `givenName`, or `seo_entity_image`.

- [ ] **Step 3: Commit test updates**

```bash
git add tools/check_site.py
git commit -m "[UPDATE] Add Personal SEO Entity Checks To Test Suite"
```

---

### Task 2: Implement On-Page Meta Tags & Entity Photo (`index.html` & `hadi-jafari.jpg`)

Implement the updated `<title>`, meta description, Open Graph profile tags, and generate the root-level entity image `hadi-jafari.jpg`.

**Files:**
- Create: `hadi-jafari.jpg`
- Modify: `index.html:9-34`

**Interfaces:**
- Consumes: High-resolution source `images/og-image.jpg`
- Produces: `hadi-jafari.jpg` at repo root, updated `<head>` tags in `index.html`

- [ ] **Step 1: Generate `hadi-jafari.jpg` from `images/og-image.jpg`**

Copy/optimize `images/og-image.jpg` to `hadi-jafari.jpg` in repo root:
```bash
cp images/og-image.jpg hadi-jafari.jpg
```

- [ ] **Step 2: Update `<head>` in `index.html`**

Update lines in `index.html`:
```html
  <title>Hadi Jafari | Django Developer · AI &amp; ML Engineer</title>
  <meta name="description" content="Official portfolio of Hadi Jafari (haadijafari). Django developer moving into AI and machine learning, and AI &amp; Soft Computing MSc student." />
  <meta name="author" content="Hadi Jafari" />
  <meta name="theme-color" content="#0b0b0f" />

  <!-- Canonical URL -->
  <link rel="canonical" href="https://hadij.ir/" />

  <meta property="og:title" content="Hadi Jafari | Django Developer · AI &amp; ML Engineer" />
  <meta property="og:description" content="Official portfolio of Hadi Jafari (haadijafari). Django developer moving into AI and machine learning, and AI &amp; Soft Computing MSc student." />
  <meta property="og:image" content="https://hadij.ir/hadi-jafari.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Hadi Jafari in a black coat and red scarf, adjusting his glasses under autumn trees" />
  <meta property="og:url" content="https://hadij.ir/" />
  <meta property="og:type" content="profile" />
  <meta property="profile:first_name" content="Hadi" />
  <meta property="profile:last_name" content="Jafari" />
  <meta property="profile:username" content="haadijafari" />
  <meta property="og:site_name" content="Hadi Jafari" />
  <meta property="og:locale" content="en_US" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Hadi Jafari | Django Developer · AI &amp; ML Engineer" />
  <meta name="twitter:description" content="Official portfolio of Hadi Jafari (haadijafari). Django developer moving into AI and machine learning, and AI &amp; Soft Computing MSc student." />
  <meta name="twitter:image" content="https://hadij.ir/hadi-jafari.jpg" />
  <meta name="twitter:image:alt" content="Hadi Jafari in a black coat and red scarf, adjusting his glasses under autumn trees" />
```

- [ ] **Step 3: Run test suite to verify Task 2 checks pass**

Run:
```bash
uv run --with fonttools --with brotli python tools/check_site.py -k head_meta -k og_meta -k seo_entity_image
```
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add index.html hadi-jafari.jpg
git commit -m "[UPDATE] Optimize Meta Tags And Add Entity Photo For Hadi Jafari"
```

---

### Task 3: Visible HTML & Identity Verification (`rel="me"`)

Enhance visible anchor tags to connect `hadij.ir` directly to `github.com/haadijafari` and `linkedin.com/in/haadijafari` using `rel="me"` for Google entity graph and IndieWeb verification. Ensure profile image `alt` attributes prominently feature `Hadi Jafari`.

**Files:**
- Modify: `index.html:250-296`

**Interfaces:**
- Consumes: Contact links in `#contact` section of `index.html`
- Produces: Validated `rel="me noopener"` links and entity alt texts

- [ ] **Step 1: Update Social Links in `index.html`**

In `index.html` within `<ul class="about-socials" aria-label="Social links">`:
1. Change GitHub link:
```html
<li><a class="social-github" href="https://github.com/haadijafari" target="_blank" rel="me noopener"><span class="social-circle"><svg class="icon" aria-hidden="true"><use href="#i-github"/></svg></span><span class="social-label">GitHub</span></a></li>
```
2. Change LinkedIn link:
```html
<li><a class="social-linkedin" href="https://www.linkedin.com/in/haadijafari/" target="_blank" rel="me noopener"><span class="social-circle"><svg class="icon" aria-hidden="true"><use href="#i-linkedin"/></svg></span><span class="social-label">LinkedIn</span></a></li>
```

- [ ] **Step 2: Verify `<h1>` and Profile Image Alts**

Confirm `<h1>Hadi Jafari</h1>` is intact. Confirm `img.profile-photo` has `alt="Portrait of Hadi Jafari in a black shirt"` and `hero-photo` has `alt="Hadi Jafari in a black coat and red scarf, adjusting his glasses under autumn trees"`.

- [ ] **Step 3: Run test suite to verify social links check passes**

Run:
```bash
uv run --with fonttools --with brotli python tools/check_site.py -k social_links_exact -k brand_icons -k contact_landing
```
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "[UPDATE] Add Rel Me Verification To GitHub And LinkedIn Profiles"
```

---

### Task 4: Enrich Schema.org JSON-LD Entity Graph

Enrich the Schema.org `@graph` `Person` node with `givenName`, `familyName`, an array of `alternateName` values (`["haadijafari", "Hadi J", "هادی جعفری"]`), and entity image reference `https://hadij.ir/hadi-jafari.jpg`.

**Files:**
- Modify: `index.html:54-140`

**Interfaces:**
- Consumes: Existing Schema.org `@graph` (`WebSite`, `ProfilePage`, `Person`)
- Produces: Google Rich Results-compliant Knowledge Graph entity node

- [ ] **Step 1: Update JSON-LD Script in `index.html`**

Inside `<script type="application/ld+json">`:
Update `ProfilePage` and `Person` nodes:
```json
      {
        "@type": "ProfilePage",
        "@id": "https://hadij.ir/#profile",
        "url": "https://hadij.ir/",
        "name": "Hadi Jafari | Django Developer · AI & ML Engineer",
        "isPartOf": {
          "@id": "https://hadij.ir/#website"
        },
        "mainEntity": {
          "@id": "https://hadij.ir/#person"
        }
      },
      {
        "@type": "Person",
        "@id": "https://hadij.ir/#person",
        "name": "Hadi Jafari",
        "givenName": "Hadi",
        "familyName": "Jafari",
        "alternateName": [
          "haadijafari",
          "Hadi J",
          "هادی جعفری"
        ],
        "url": "https://hadij.ir/",
        "image": "https://hadij.ir/hadi-jafari.jpg",
        "sameAs": [
          "https://github.com/haadijafari",
          "https://www.linkedin.com/in/haadijafari/",
          "https://t.me/haadijafari",
          "https://instagram.com/hadijafari.exe"
        ],
        "description": "Django developer moving into AI and machine learning; AI & Soft Computing MSc student.",
        "jobTitle": [
          "Co-founder & CTO",
          "Django Developer",
          "Software Developer"
        ],
        ...
```

- [ ] **Step 2: Run test suite to verify JSON-LD graph checks pass**

Run:
```bash
uv run --with fonttools --with brotli python tools/check_site.py -k jsonld -k jsonld_graph
```
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "[UPDATE] Enrich Person Entity Schema In JSON-LD Graph"
```

---

### Task 5: Scaffold GitHub Profile Repository (`haadijafari/haadijafari`)

Create the SEO-optimized `README.md` for the special profile repository `haadijafari/haadijafari` so that searching "Hadi Jafari" ranks the GitHub profile alongside `hadij.ir`.

**Files:**
- Create: `docs/github-profile/README.md`

**Interfaces:**
- Consumes: Spec Phase 3.2
- Produces: Production-ready README for `https://github.com/haadijafari/haadijafari`

- [ ] **Step 1: Write `docs/github-profile/README.md`**

Create `docs/github-profile/README.md`:
```markdown
# Hi, I'm Hadi Jafari 👋

Welcome to the official GitHub profile of **Hadi Jafari** ([@haadijafari](https://github.com/haadijafari)).

- 🌐 **Official Website & Portfolio:** [hadij.ir](https://hadij.ir)
- 💼 **Role:** Django Developer & Software Engineer | AI & Soft Computing MSc Student
- 📍 **Location:** Isfahan, Iran
- 🔗 **LinkedIn:** [Hadi Jafari on LinkedIn](https://www.linkedin.com/in/haadijafari/)

## About Hadi Jafari
I am a back-end software engineer specializing in clean, well-architected Django systems and applying engineering rigor to Machine Learning and Artificial Intelligence.

## Featured Repositories
- **[VetYar](https://github.com/haadijafari/VetYar)** — Modern veterinary practice management & clinic platform.
- **[haadijafari.github.io](https://github.com/haadijafari/haadijafari.github.io)** — Source code for [hadij.ir](https://hadij.ir).
```

- [ ] **Step 2: Commit GitHub profile asset**

```bash
git add docs/github-profile/README.md
git commit -m "[ADD] Create SEO Optimized Profile README For GitHub haadijafari"
```

---

### Task 6: Technical Sitemap & Crawling Refresh

Bump `sitemap.xml` `<lastmod>` to trigger re-crawling upon deployment, and verify `robots.txt` configuration against `check_site.py`.

**Files:**
- Modify: `sitemap.xml`

**Interfaces:**
- Consumes: Current date `2026-10-21`
- Produces: Fresh `sitemap.xml` with updated `<lastmod>`

- [ ] **Step 1: Update `sitemap.xml` `<lastmod>`**

Set `<lastmod>` in `sitemap.xml` to `2026-10-21`.

- [ ] **Step 2: Run site check for sitemap**

Run:
```bash
uv run --with fonttools --with brotli python tools/check_site.py -k sitemap
```
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add sitemap.xml
git commit -m "[UPDATE] Refresh Lastmod In Sitemap For Search Engine Crawl"
```

---

### Task 7: Off-Page Entity Authority Runbook

Document the external off-page steps (Google Search Console URL inspection, GitHub settings, LinkedIn, Gravatar, Dev.to) in a structured checklist for Hadi Jafari.

**Files:**
- Create: `docs/seo-offpage-runbook.md`

**Interfaces:**
- Consumes: Spec Phases 3, 4, and 5
- Produces: Actionable post-deploy runbook

- [ ] **Step 1: Write `docs/seo-offpage-runbook.md`**

Include step-by-step instructions for:
1. **GitHub Profile Settings**: Set Name to `Hadi Jafari`, Bio to include full name and handle, Website to `https://hadij.ir`.
2. **Google Search Console**: Verifying property, submitting `https://hadij.ir/sitemap.xml`, and requesting URL indexing for `https://hadij.ir/`.
3. **LinkedIn**: Updating headline, custom URL, and Website link with "Personal Website".
4. **Dev.to / Medium / Gravatar**: Unifying avatar and display name "Hadi Jafari" with backlinks.

- [ ] **Step 2: Commit**

```bash
git add docs/seo-offpage-runbook.md
git commit -m "[ADD] Add Off-Page SEO Authority Runbook And Verification Steps"
```

---

### Task 8: Comprehensive Suite & Regression Verification

Run the entire test suite `tools/check_site.py` to ensure all 70+ automated checks pass with zero regressions.

**Files:**
- Test: All files in repository

- [ ] **Step 1: Run complete `check_site.py`**

Run:
```bash
uv run --with fonttools --with brotli python tools/check_site.py
```
Expected: All checks PASS, exit code 0.

- [ ] **Step 2: Check Git status and working directory hygiene**

Run:
```bash
git status
```
Expected: Clean working tree on current branch.
