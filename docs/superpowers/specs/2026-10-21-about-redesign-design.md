# About section redesign

Date: 2026-10-21. Builds on `2026-10-21-website-redesign-design.md`, which still governs everything outside `#about` (and that document's "Changes after Hadi's first look" list wins where the two touch, such as the section title style).

## Why

Hadi called the current About section simple, typical and spiritless. In his words, the reaction he wants from an Instagram follower who lands there is "wow, he is a high value guy!" Recruiters and classmates should get the same impression, just more quietly. The fix is in the design, not the copy. Chess, guitar, MMA and the rest stay in their own sections, and the About text keeps its current wording.

His specific complaints about the current section:
- The portrait is about as big as the hero photo, so it feels repeated.
- The faded handwriting behind section titles is too small on phones.
- The hero's Contact button scrolls so that the social links end up at the top edge of the screen instead of the middle.
- "Skills" is plain.
- Overall it looks like a typical, boring template.

## Goals

- Phones come first. The phone layout was designed first, and desktop is a wider arrangement of the same parts.
- A memorable profile at the top: a big round photo with a purple story ring, as on Instagram.
- A quiet tone about the CTO role: one small tag, not a headline.
- Every fact that the current section shows stays, apart from the "MSc" stat tile, whose content moves into Degree.

## Non-goals and anti-goals

- No rewrite of the intro paragraphs. Their wording stays exactly as in `tools/check_site.py` (`ABOUT_P1`, `ABOUT_P2`).
- No showing off: no big CTO tile, no "CTO at 23" headline, no inflated numbers.
- No Instagram colors. The story ring is purple. Brand colors appear only on the social logos.
- No new motion beyond what answers a tap (opening the intro). The ring doesn't spin or pulse.
- The phone number never appears (unchanged rule).

## The design

The approved mockup is in `.superpowers/brainstorm/54550-1792577861/content/about-details-v5.html`. It's git-ignored and local, so it's only reference, not something to ship. Its sizes are scaled for the companion's frames: follow its proportions, not its pixel values.

### Phone layout (below 992px), top to bottom, all centered

1. **Section title:** unchanged ("About Me" with the faded handwriting behind it).
2. **Photo:** a big round portrait (`images/avatar/me-*.webp`) inside a purple story ring. The ring is a conic gradient through `#c77dff`, `#8E05C2` and `#3E065F`, with a thin gap in the page background between the ring and the photo. The ring is about 65–70% of the content width, capped near 260px. The photo is decorative in its frame and not interactive.
3. **Name:** "Hadi Jafari" in plain bold type (the body font, not script). It's the largest text after the section title.
4. **Tags (pills):** two outlined pills side by side, each with a small purple icon:
   - "Co-founder & CTO, Vira Kavane Zista" (briefcase icon)
   - "Isfahan, Iran" (location pin icon)

   There is no student tag; the MSc lives under Degree.
5. **Intro:** both paragraphs are in the HTML. On phones the block is collapsed to about three lines, fading into the background, with a "Read more" control under it. Tapping the text or the control opens the block, and the control then reads "Show less". The control is a real `<button>` with `aria-expanded` and `aria-controls`. The collapse is added by JavaScript, so without JS the full text shows.
6. **Details list (`<dl>`):** two columns, each label with a small grey outline icon:
   - **Birthday** (calendar icon): "April 2003 (23 years)". The 23 is `#age`, computed by the existing `ageFrom(2003, 3)`, so it ticks over each April.
   - **Degree** (graduation cap icon): "BSc Computer Science" with "MSc AI & Soft Computing" on the next line.
   - **Freelance** (laptop icon), on a full row:
     - a green dot and "Available", then a simple outlined "Contact me" pill button
     - the button has a thin purple border, purple text, and no fill, glow or icon
     - it links to `mailto:haadijafari2003@gmail.com?subject=Freelance%20project`
   - **Hidden on phones only:** the Email row and the "(in progress)" note after the MSc. Both are in the HTML and shown on desktop.
7. **Numbers row:** three centered items between thin top and bottom rules:
   - **3+**, years of Django
   - **17.57**, BSc GPA / 20
   - **10**, certificates. This is the existing self-updating `#cert-count`.
8. **Social circles:** five round links with their official logos in brand colors, each with a small label under it. In order:
   - GitHub (white mark)
   - LinkedIn (#0A66C2)
   - Gmail (the official four-color M)
   - Telegram (#26A5E4)
   - Instagram (the official gradient glyph)

   The circles have a dark fill and a thin neutral ring, as story highlights do. On phones they spread across the full width. Their hrefs and order are exactly `SOCIAL` in `tools/check_site.py`.
9. **Skills:** a divider heading with "Skills" between two thin purple lines that fade outward (`—— Skills ——`). It's a real heading element. Under it are the four existing groups (Back-end, AI & ML, DevOps & Tools, Front-end), each with a small grey label and its current tags, centered.

### Desktop layout (992px and wider): "D1, two columns"

- **Left column** (about 320px), centered within itself: the ringed photo at about 280px, then the name and the two tags.
- **Right column:**
  - the intro, both paragraphs in full, with no collapse and no "Read more"
  - the details list in a 2 × 2 grid: Birthday and Degree on top, Email (a mailto link) and Freelance below; Degree shows "(in progress)"
  - the numbers row
  - the social circles, centered in the column and grouped close together, not spread out
- **Skills:** full width under both columns, with the four groups in four columns side by side.
- The left nav rail stays, as on the rest of the page.

### Contact landing

`id="contact"` moves to the block that holds the numbers and the social circles. The hero's Contact button (`#contact`) must scroll so that this block sits in the vertical middle of the screen, on phones and on desktop. That means `block: "center"` or an equivalent scroll offset, and it respects reduced motion like the other in-page scrolls.

### Section titles, page-wide

The faded handwriting behind every section title gets bigger on phones. At 360px wide it should be at least about 2.3 times the title's size (today it's about 1.3 times). Desktop stays at its current 10rem. The words may run past the screen edges; `.section` already clips horizontal overflow, and nothing may cause sideways scrolling.

## What goes away

- **Removed:**
  - the "Django Developer → AI & Machine Learning" subheading
  - the separate Age item (age now sits in brackets after the birthday)
  - the "MSc" stat tile
  - the five contact cards and the "Get in touch" subheading
  - the "Skills" subtitle styling
- **Updated with the markup:**
  - in `tools/check_site.py`, `ABOUT_HEADING` and any check that expects the removed pieces
  - `CLAUDE.md` and the JSON-LD if they mention them (the JSON-LD doesn't today)

## Constraints

- Everything in the parent spec's Global Constraints still holds:
  - static site, no CDN, no new libraries
  - purple and black tokens from `css/base.css`
  - the initial page weight stays under the budget check
  - every image is lazy and sized
  - no secret product name
  - no phone number
  - stage specific files only
  - **no commits until Hadi says so**
- Icons come from the existing generated sprite (`tools/build_assets.py sprite`), using Bootstrap Icons 1.11.3 shapes. Gmail isn't in Bootstrap Icons, and both the four-color Gmail mark and the gradient Instagram glyph need their own colors. The builder adds them as sprite symbols that keep their own fills, or as small inline SVGs.
- No horizontal overflow at 360, 390, 430, 768, 844 or 1280px (the existing screenshot harness).
- Keyboard: every link and the Read more button is reachable and has a visible focus ring. Social circles have accessible names ("GitHub" and so on).

## Left to the builder

- Exact spacing, font sizes and the ring thickness, within the proportions of the mockup.
- Whether "fades into the background" is a gradient mask or an overlay.
- How the tests are split, following the TDD style of `tools/check_site.py`.

## Calls Claude made (for Hadi to check)

- **Breakpoint:** 992px, the same as the nav rail. Below that, tablets get the phone layout, including the collapsed intro and the hidden Email row.
- **Subheading:** "Django Developer → AI & Machine Learning" is dropped, because none of the approved mockups had it.
- **Official logos:** Gmail uses the official four-color M and Instagram its gradient glyph. The mockup showed single-color stand-ins.
- **Tags:** the two remaining tags sit side by side when they fit, and wrap otherwise.
- **Handwriting size:** the bigger faded handwriting applies to every section title, not just About.
