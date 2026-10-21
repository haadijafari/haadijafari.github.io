# hadij.ir redesign: design

Date: 2026-10-21
Status: draft for approval (builder check done)

## Intent

`hadij.ir` is Hadi Jafari's personal brand. Anyone might land on it: a recruiter, an Instagram follower, a classmate. It has to come across as **legit and elegant** to all of them: credible enough for a recruiter, personal enough for a friend.

The current site is out of date (it predates Hadi's BSc graduation, MSc admission, new company and new skills), loads slowly, has visible design and credibility flaws, and is weak on mobile. This redesign fixes all of that while keeping the same single-page static site.

The one-sentence brief, in Hadi's words: *"A Django developer with a high obsession with clean structure who is moving to AI and machine learning but hasn't abandoned Django yet."*

## Goals

1. **Fast.** A first visit should feel instant on a phone on mobile data. No blocking preloader. No libraries that aren't used. Every image resized to its display size and served as WebP.
2. **Credible.** Every fact and number on the page is true and checkable. No inflated stats, no typos, no template leftovers, no contradictions between sections.
3. **Current.** Reflects Hadi as of October 2026 (see Content below).
4. **Elegant on mobile.** Every section is designed for a ~390px-wide phone first, with no horizontal scroll and no text overflow.
5. **Complete.** Adds a Projects section and proper contact links.

## Non-goals

- No build step, framework, package manager or CDN. It stays a plain static site served by GitHub Pages, with every dependency committed to the repo (see CLAUDE.md).
- No light mode. The site stays dark (`data-bs-theme="dark"`).
- No Persian or multilingual version of the page. English only (Persian dates are the one exception, see below).
- No mention of the secret product by name or description until it launches.
- Updating the downloadable CV PDF is not part of this work. Hadi will update it himself.

## Anti-goals (would count as failure even if it "works")

- Any claim Hadi can't back up: inflated counts, self-rated percentage bars, "expert" claims about things he's still learning.
- A jokey or hype-y tone ("Don't you know who I am?", "∞ coffee").
- A page that looks great on desktop but cramped or overflowing on a phone.
- Breaking the purple-and-black identity.

## Constraints

- **Static GitHub Pages site**, single `index.html`, custom domain in `CNAME`.
- **No CDN.** All libraries live in `vendors/`.
- **Custom Bootstrap build.** `bootstrap.min.css` is compiled from `vendors/bootstrap-5.3.3-dist/sass/bootstrap.scss`, and no Sass compiler is installed. Don't rely on new Bootstrap theme colors. New colors go in `css/style.css` as CSS custom properties that build on the existing `--bs-purple*`/`--bs-dark-gray` variables.
- **Git:** follow the commit conventions in CLAUDE.md (`[ADD]`/`[FIX]`/`[UPDATE]` tags, stage specific files only, because every file shows a mode-only change).
- `.superpowers/` holds brainstorming mockups and is git-ignored. It isn't part of the site.

## Visual direction (decided)

- **Colors: purple and black**, Hadi's two favorite colors. Primary `#8E05C2`, with `#700B97`, `#3E065F` and the lighter accent `#c77dff` used in mockups. Black/near-black backgrounds (`#0b0b0f`), subtle dark-gray card surfaces (`#16161c`, border `#2a2a33`).
- **Tone:** plain, confident, first person. No jokes, no hype.
- Mockups Hadi reacted to are in `.superpowers/brainstorm/54550-1792577861/content/` (`hero-layout.html` option A, `social-design.html` options B and C, `hobbies-mobile.html` option 3). They are rough sketches of layout and feel, not pixel specs.

**My calls (Claude), open to override:**
- Keep the script font (PinyonScript) for Hadi's name in the hero only, as a signature. All other headings and body text use a clean sans-serif. The faded giant script watermark behind section titles (`.section-title span`) is dropped, since it's a big part of the dated look.
- Drop the decorative wavy SVG dividers (`images/svg/*divider*`, `footer-top.svg`).
- Remove the fixed side margins and heavy padding around sections that squeeze content on phones.

## Page structure (in order)

1. Navigation
2. Hero
3. About (with Counts, Skills, contact cards)
4. Projects (new)
5. Certifications
6. My Resume (Languages, Professional Experience, Education)
7. Services
8. Hobbies
9. Footer

The nav, `sitemap.xml` and JSON-LD must all match this list (CLAUDE.md: they move together). Add `#projects` to the nav and sitemap.

### 1. Navigation

Keep the current pattern: a left icon rail on desktop and a hamburger drawer on mobile. Add Projects. Fix the "Hobbbies" typo. The builder may restyle the nav to match the new look, but its structure isn't changing.

### 2. Hero: split layout (decided, mockup `hero-layout.html` A)

- **Desktop:** text on the left, the new photo on the right, about 45–50% of the width, full height. The photo's left edge fades into the black background. *My call:* a faint purple glow behind the subject, so the warm photo (red scarf, autumn gold) blends with the purple theme without being recolored.
- **Phone:** photo on top (~55–60% of the viewport height) fading into black at its bottom edge, text below.
- **Photo:** `images/hero/IMG_0154.jpg` (3549×5323, 9.9 MB, Canon, portrait). Crop it to keep head to waist, then export responsive WebP sizes (for example ~600w and ~1200w) via `srcset`. The 9.9 MB original must never be served. It replaces `hero-bg_001.jpg` as the hero image.
- **Text:**
  - Name: **Hadi Jafari** (script signature font).
  - Typed line: "I'm a *Django Developer* / *Machine Learning Practitioner* / *AI & Soft Computing MSc Student*" (Typed.js, keep it).
  - Tagline: "I build clean, well-structured Django back-ends, and I'm bringing the same discipline to AI and machine learning."
  - Buttons: **Download CV** (primary, purple) and **Contact** (outline, scrolls to the About contact cards or opens mailto, builder's choice).
  - Under the buttons: the social links in **pill style** (see About → Social links, style B).

### 3. About

**Heading under the name:** "Django Developer → AI & Machine Learning"

**Intro text** (Claude's draft; Hadi may edit wording):
> I'm a back-end developer who cares a lot about structure: clear architecture, readable code, and systems that are easy to grow. I've spent the last few years building web applications with Django, and I'm still building with it today.
>
> After finishing my BSc in Computer Science at Shahrekord University, I started a master's in AI & Soft Computing at Allameh Tabataba'i University. I'm now applying the same engineering habits to machine learning, from leak-free pipelines to models that hold up outside a notebook.

**Info list:** Birthday (2003 Apr), Age (computed in `main.js`), Degree, Location, Email, Freelance. No phone row.
- Degree: "BSc Computer Science · MSc student, AI & Soft Computing"
- Location: **Isfahan, Iran** (fixes "Isfahan, Persia")
- Freelance: **Available (Contact Me)**, where "Contact Me" is a `mailto:` link to haadijafari2003@gmail.com (not Telegram).
- Remove all `text-nowrap` that causes overflow on phones. The email address must wrap or fit at 390px.
- Phone: **removed** (no number anywhere on the site).

**Social links: contact cards (decided, mockup `social-design.html` C).** A responsive grid of cards. Each card has an icon, the platform name, the handle, and an ↗ arrow. Order (my call, recruiters first):

| Platform | Handle shown | Link |
|---|---|---|
| GitHub | @haadijafari | https://github.com/haadijafari |
| LinkedIn | in/haadijafari | https://www.linkedin.com/in/haadijafari/ |
| Email | haadijafari2003@gmail.com | mailto:haadijafari2003@gmail.com |
| Telegram | @haadijafari | https://t.me/haadijafari |
| Instagram | @hadijafari.exe | https://instagram.com/hadijafari.exe |

**Removed everywhere:** Twitter/X and WhatsApp. Email uses a plain envelope icon (my call).

The **pill style** (mockup `social-design.html` B) is used for the same five links in the **hero** and the **footer**.

**Counts.** Replace the four counters with true facts:

| Value | Label |
|---|---|
| 3+ | Years building with Django (since 2023) |
| 17.57 / 20 | BSc GPA |
| *auto* | Certifications |
| MSc | AI & Soft Computing, Allameh Tabataba'i |

- The certifications number is **computed at page load** by counting the certificate cards in the Certifications section. Adding a card updates it automatically, with no manual number anywhere. Count cards, not `.certifications-lightbox` links: each card currently contains two of those.
- The counter uses Gregorian years only. Persian dates appear only in My Resume (see Dates).
- Whether the numbers animate is the builder's choice. If PureCounter stays, the computed value must be set before it initializes.

**Skills.** Replace the percentage bars with grouped tags. No percentages anywhere.

- **Back-end:** Python, Django, Django REST Framework, SQL
- **AI & ML:** scikit-learn, NumPy, pandas, Jupyter, Streamlit
- **DevOps & Tools:** Docker, Git & GitHub, Linux, DVC, uv
- **Front-end:** HTML, CSS, Bootstrap, JavaScript
- *(GUI/other, optional:* PyQt5, Pygame)

Every tool listed must be backed by a project, a certificate or Hadi's stated work. These are.

**Download CV** button stays (links to `resume/hadi_jafari_resume.pdf`). It can move to the hero instead of being duplicated, builder's choice.

### 4. Projects (new)

Text-only cards (my call: no screenshots, for speed and consistency; optionally the Tetris gameplay GIF as one card's media, converted to an efficient format). Each card has a title, a one-line summary, a key result, tech tags, and a "View on GitHub" link. Order:

1. **Tehran House Price Prediction**: https://github.com/haadijafari/House-Price-Prediction
   Predicts Tehran residential prices in USD, so the model isn't skewed by Rial inflation. Random Forest reaches **R² 0.822** on a holdout set of 3,450 real listings. Leak-free scikit-learn pipelines and an interactive Streamlit app.
   *Python · scikit-learn · pandas · Streamlit · DVC*
2. **Tetris AI**: https://github.com/haadijafari/Tetris_AI
   A university AI project: a greedy agent that scores each move on aggregate height, completed lines, holes and bumpiness.
   *Python · Pygame*
3. **Persian Character Recognizer**: https://github.com/haadijafari/Alphabet-Recognition
   A Hebbian neural network written from scratch that recognizes hand-drawn ه and ج, with a PyQt5 drawing app and graphics-tablet support.
   *Python · NumPy · PyQt5*

The structure should make adding a fourth card trivial (for the secret product after launch). No placeholder or teaser card for it now.

### 5. Certifications

Keep the GLightbox gallery behavior (a click opens the full certificate plus the description block). Restyle the cards to match the new look.

**Add:** *Machine Learning Foundations for Product Managers*, Duke University via Coursera, completed Sep 29, 2026.
- Source: `resume/Docs/Machine Learning Foundations for Product Managers.pdf`. Render it to an image (WebP) for the card and the lightbox.
- Description: "From: Duke University (Coursera)", plus a **Verify** link to https://coursera.org/verify/6DB82NPQSW6L.
- Needs a unique `descN` class (CLAUDE.md).

Order (my call): newest and most relevant first. The Duke/Coursera ML certificate leads.

Existing certificates keep their descriptions (hours, provider link, instructor). Fix the EF SET card title to show the level: "English: EF SET C2 Proficient". Add Verify links to older certificates only if Hadi provides them.

### 6. My Resume

**Dates (decided):** In **Professional Experience** and **Education only**, each date shows Gregorian first, then the Persian (Jalali) year next to it in a lighter, smaller style using **Persian digits**:

> **2021 – 2025** ۱۴۰۰ – ۱۴۰۴
> **2023 – Present** ۱۴۰۲ – اکنون

Everywhere else on the site uses Gregorian only.

**Languages.** Replace the four bars (and the `{{ language.* }}` template leftovers) with one line:
> English: **C2 Proficient** (EF SET 76/100) · Persian: **Native**

German is not listed (Hadi stopped learning it).

**Professional Experience** (newest first):

1. **Co-founder & CTO**, Vira Kavane Zista
   **2026 – Present** ۱۴۰۵ – اکنون
   > Leading the technical side of our first product, launching soon. I own the Django back-end, the project architecture, Docker-based production and deployment, and server management.

   Don't name or describe the product. Make no claims beyond this (no "leading a team", no "scaling"). If the company has a website or LinkedIn page later, link the name.

2. **Django Back-end Developer**
   **2023 – Present** ۱۴۰۲ – اکنون · Isfahan, Iran
   Rewrite the existing paragraph without the "two years" figure (it contradicts the counter). Keep the substance: custom Django solutions, clean architecture, database work, working directly with clients.

**Education** (newest first):

1. **MSc, Artificial Intelligence & Soft Computing**, Allameh Tabataba'i University
   **2026 – Present** ۱۴۰۵ – اکنون
   Logo: `images/edu/ATU.svg` (supplied by Hadi). Notes for the builder:
   - It's an Inkscape export (65 KB) that is mostly **black** paths with some white and green. On the dark theme it needs a light backdrop, for example a white rounded tile. Give the SKU and Sampad logos the same treatment so all three match.
   - It contains an embedded base64 PNG placed far outside the 1700×2000 canvas (`<image x="6395…">`) plus Inkscape metadata. Strip both, or export a clean optimized copy, so the file is a fraction of its size. Check that it renders the same afterwards.
2. **BSc, Computer Science**, Shahrekord University
   **2021 – 2025** ۱۴۰۰ – ۱۴۰۴ · GPA **17.57 / 20**
   Spell it "Shahrekord University" consistently (the site currently uses "Shahr-e Kord").
3. **Diploma, Mathematics & Physics**, Shahid Ejei High School (Sampad), Najafabad
   **2018 – 2021** ۱۳۹۷ – ۱۴۰۰
   *My call:* keep it, shortened to a line or two.

### 7. Services

Six services, same card style family as the rest of the page:

1. **Web Applications**: secure, scalable, maintainable web apps with Django.
2. **API Development**: RESTful APIs for services and third-party integrations.
3. **E-Commerce Solutions**: product management, carts, payment integration.
4. **Data Analysis & Visualization**: data cleaning, analysis and dashboards.
5. **AI & Machine Learning**: ML prototypes such as classifiers, recommendation systems and predictive models.
6. **Architecture & Refactoring** *(replaces Automation & Scripting)*: "Restructuring messy or growing Django codebases into clean, maintainable architecture, so new features stop breaking old ones."

Section intro: replace "Services I can provide you are listed below" with a plain one-liner, builder's wording.

### 8. Hobbies: polaroid deck (decided, mockup `hobbies-mobile.html` 3)

Five hobbies:

| Hobby | Photo | Draft text (Hadi to approve wording) |
|---|---|---|
| **Chess** | `images/hobbies/chess2.jpg` | King's Gambit with white, Alekhine Defense with black. I like sharp positions. |
| **Martial Arts & Workout** | `images/hobbies/jiu-jitsu.jpg` | MMA, jiu-jitsu, and the gym. Discipline, humility, and a lot of tapping out. |
| **Guitar** | `images/hobbies/music1.webp` | Classical pieces like "Romance de Amor". My way to slow down and switch off. |
| **Learning** | `images/hobbies/brain.jpeg` | Machine learning, Django, Linux, books, and people skills. Always in the middle of learning something. |
| **Friends** | `images/hobbies/friends2.jpg` | Long talks, late coffees, and the people who keep me grounded. |

- **No belt badge,** and no belt mention in the text.
- **Phone:** a compact stack of tilted instant-photo (polaroid) cards with handwritten captions. Tapping sends the top card to the back and shows its text below the stack. It takes roughly a quarter to a third of the screen, not the whole thing. It must also work with the keyboard (a focusable button) and show a small "tap to shuffle" hint.
- **Desktop (my call):** all five polaroids spread across the section like photos tossed on a table, slightly overlapping and tilted. Hover or focus lifts and straightens one and shows its text.
- Caption font: **Satisfy** (already in `fonts/`), so no new font download.
- Respect `prefers-reduced-motion`: no shuffle/tilt animation, just instant changes.
- Removes the Bootstrap accordion and the second-person, AI-sounding texts.

### 9. Footer

- "© 2023" → the current year (computed in JS or written as 2026).
- Social links in **pill style**, the same five as About.
- *My call:* keep the German quote („Ich habe gelitten, gelernt und mich verändert") as a small personal touch, but link it to nothing or a plain translation tooltip instead of a Google Translate URL.

## Performance (goals and decided measures)

The current first visit downloads about 2.5 MB, behind a blocking preloader. Target: **under ~600 KB for the initial view on a phone**, with everything below the fold lazy-loaded.

Decided:
- **Remove the preloader** (`#preloader` and its JS/CSS).
- **Remove unused libraries:** Isotope (`isotope.pkgd.min.js`) and the portfolio JS in `main.js`; Waypoints (skill bars are gone); the Bootstrap JS bundle, unless something still needs it (the accordion is gone, and the mobile nav is custom JS).
- **Images:** every image displayed on the page is converted to **WebP**, resized to at most ~2× its largest display size, and given `width`/`height` attributes. Everything below the hero gets `loading="lazy"` and `decoding="async"`. The hero image uses `srcset`/`sizes` and `fetchpriority="high"`.
- Certificate thumbnails get their own small WebP. The lightbox may load a larger WebP.
- **Fonts:** only fonts actually used are declared (PinyonScript for the name, Satisfy for the polaroids). Convert them to WOFF2 and use `font-display: swap`. Drop the unused `@font-face` rules (GreatVibes, Dancing Script, HerrVonMuellerhoff) and the undefined "Raleway"/"Poppins" references.
- **Icons:** the Bootstrap Icons font is ~210 KB for ~25 icons. Builder's choice: subset it, or replace the icons with inline SVG.
- Scripts at the end of `<body>` or `defer`.

Left to the builder: whether to keep Typed.js (12 KB, wanted) and GLightbox (needed) as is, how to trim CSS, and whether to self-subset Bootstrap CSS.

## Metadata and SEO

Update together with the content:
- `<title>`, `meta description`, `og:*`: reflect "Django developer · AI & ML · MSc student". `og:image` becomes a 1200×630 crop of the new photo (JPEG or WebP).
- JSON-LD `Person`:
  - `sameAs`: GitHub, `https://www.linkedin.com/in/haadijafari/`, Instagram `hadijafari.exe`. Remove X.
  - `jobTitle`: "Co-founder & CTO" and "Django Developer".
  - `worksFor`: Vira Kavane Zista.
  - `alumniOf`: Shahrekord University, the high school.
  - Add the MSc: Allameh Tabataba'i University, as `affiliation` or similar.
  - `knowsAbout`: update. `knowsLanguage`: English, Persian (remove German).
- `sitemap.xml`: add `#projects`.
- Fix image `alt` texts (for example "Hadi Jafari - My Happy SVG" goes away along with the dividers). Every content image gets a real description.

## Credibility fixes checklist

- "Hobbbies" typo; "© 2023"; "Isfahan, Persia".
- "Freelance: Unknown".
- Counter vs. text contradictions (4 years vs "two years").
- "100 Projects", "10 Awards", "∞ Coffee" removed.
- Skill bar mismatch (80% label vs. 90% bar) gone with the bars.
- `{{ language.* }}` and `{% ... %}` template leftovers removed, including the commented-out portfolio/contact include comments.
- Section intros rewritten without jokes ("Don't you know who I am?…", "People have hobbies, and I'm not exceptional…").
- Second-person hobby text gone.

## Repo cleanup (needs Hadi's OK before deleting)

The repo carries ~18 MB of vendor files and unused images (for example `images/avatar/me3.jpg~` 2 MB, `images/hero/hero-bg-mobile.jpg` 2.4 MB, `images/portfolio/`, unused hero variants, `*~` backups, unused fonts). Visitors don't download them, so this is housekeeping, not speed. The builder should **list** the candidates and get Hadi's approval before deleting anything. Original high-res photos (for example `IMG_0154.jpg`) should be kept out of the deployed path or confirmed for deletion, since a copy exists in `~/Pictures/Me/Keyv/`.

## Mobile requirements

- Design and check at 360px, 390px and 430px widths, plus tablet (768px) and desktop (1280px+).
- No horizontal scroll at any width. Long strings (email) wrap or shrink.
- Tap targets of at least 44px.
- The hero photo crop must keep the face fully visible at every breakpoint.

## What's left to the builder

- Exact spacing, type scale and component styling within the purple/black direction and the mockups.
- Whether counters animate.
- Icon strategy (subset font or inline SVG).
- CSS organization (keep `base.css`/`style.css` and the banner-comment convention).
- Exact image sizes and quality settings, within the targets above.
- Wording of short section intros and the rewritten Django-developer paragraph, in the tone described. Hadi reviews all copy before it ships.

## Decisions from Hadi (after builder check)

- **CV PDF:** Hadi will update `resume/hadi_jafari_resume.pdf` himself later. The Download CV button stays and keeps linking to that path. Updating the PDF is not part of this work.
- **LinkedIn:** the correct URL is `https://www.linkedin.com/in/haadijafari/`. Use it everywhere: contact card, both pill rows, JSON-LD `sameAs`.
- **Location:** "Isfahan, Iran" (About info list, experience entry, JSON-LD if present).
- **Phone number:** **not shown anywhere on the site.** Remove the About "Phone" row and every `tel:` link. Together with WhatsApp's removal, the number no longer appears in the page.
- **German:** remove every mention (JSON-LD `knowsLanguage`, and anywhere else it appears). The Languages line is English and Persian only. **Keep** the German quote in the footer.
- **Jiu-jitsu belt:** not mentioned in the hobby text (default, unless Hadi asks).
- **Hobby photos:** `jiu-jitsu.jpg` and `brain.jpeg` are used as chosen. Claude noted they may be web/stock images (copyright, and the jiu-jitsu photo shows other people), and Hadi kept them.

## Changes after Hadi's first look (2026-10-21)

These override the sections above where they conflict:
1. **Footer waves are back:** the purple wave divider (`images/svg/footer-top.svg`) sits above the footer, served as `images/svg/footer-waves.svg` with its black backdrop removed.
2. **Faded handwritten section names are back:** each section title has the big faded Herr Von Muellerhoff word behind it ("About Me", "Projects", "Certifications", "My Resume", "Services", "Hobbies"), centered on the heading.
3. **Services hover color change is back:** a hovered card turns purple, with a black title and white text and icon.
4. **The About portrait is back:** `images/avatar/me.jpg` (served as WebP) sits beside the intro on wide screens and above it on phones.
5. **Jalali dates use Latin digits and "Now",** for example "1405 – Now", with no Persian font or digits. They still appear only in Experience and Education.
6. **No purple glow on the hero photo.**
7. **No social links in the hero.** They remain in About (contact cards) and the footer (pills).
8. **Original section title design is back:** titles and their descriptions are centered, the heading is large, weight 900 and purple (`--c-primary`), with no underline bar, and the handwritten word sits centered behind the heading's lower half (opacity 0.3). Headings read "About Me" and "My Resume" again, matching their handwriting.
