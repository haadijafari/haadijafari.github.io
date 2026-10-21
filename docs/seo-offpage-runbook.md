# Hadi Jafari — Off-Page SEO & Identity Authority Runbook

This runbook guides the external actions needed to establish **"Hadi Jafari"** as the #1 search query result on Google, unify your entity in Google's Knowledge Graph, and direct search authority to `https://hadij.ir`.

---

## 1. GitHub Profile Optimization (`github.com/haadijafari`)

GitHub possesses extremely high domain authority. Aligning your GitHub profile settings directly transfers PageRank and entity signals to `hadij.ir`.

- [ ] **1.1 Profile Settings (`https://github.com/settings/profile`)**
  - **Name:** `Hadi Jafari` (exact spelling, capitalized).
  - **Bio:** `Hadi Jafari — Django Developer & Software Engineer. Building clean web systems and practicing AI & Machine Learning.`
  - **Pronouns:** (Optional)
  - **Company:** `Vira Kavane Zista`
  - **Location:** `Isfahan, Iran`
  - **Website:** `https://hadij.ir` (explicitly with `https://`)
  - **Social Accounts:** Add your LinkedIn profile URL (`https://www.linkedin.com/in/haadijafari/`).

- [ ] **1.2 Deploy Special Profile Repository (`haadijafari/haadijafari`)**
  - Create a public repository named `haadijafari` under account `@haadijafari`.
  - Copy the prepared markdown from `docs/github-profile/README.md` into that repository's `README.md`.
  - This displays your profile README prominently on `https://github.com/haadijafari`.

- [ ] **1.3 Add Website to Top Repositories**
  - On public repositories such as `VetYar` and `haadijafari.github.io`, open **"About" (gear icon)** and set the Website field to `https://hadij.ir`.

---

## 2. Google Search Console (GSC) Indexing Protocol

Force Google to crawl your new entity metadata immediately rather than waiting weeks for periodic discovery.

- [ ] **2.1 Add & Verify Property in Google Search Console**
  - Visit [Google Search Console](https://search.google.com/search-console).
  - Add property:
    - **URL Prefix:** `https://hadij.ir/`
    - Or **Domain Property:** `hadij.ir` (via DNS TXT record).
  - Verification meta tag `google-site-verification` is already embedded in `index.html`.

- [ ] **2.2 Submit Sitemap**
  - In the left sidebar, click **Sitemaps**.
  - Enter `sitemap.xml` (full URL: `https://hadij.ir/sitemap.xml`) and click **Submit**.
  - Verify that the status shows **"Success"**.

- [ ] **2.3 Force URL Inspection & Request Indexing**
  - In the top search bar ("Inspect any URL in https://hadij.ir/"), paste `https://hadij.ir/`.
  - Click **"Test Live URL"** to confirm Google sees the updated `<title>`, `<meta>`, and JSON-LD markup.
  - Click **"Request Indexing"**.

- [ ] **2.4 Validate Rich Results**
  - Open [Google Rich Results Test](https://search.google.com/test/rich-results).
  - Enter `https://hadij.ir/`.
  - Confirm the `ProfilePage` and `Person` schema markup are valid with 0 errors.

---

## 3. LinkedIn Profile Alignment (`linkedin.com/in/haadijafari`)

LinkedIn ranks at the top of personal name search results. Proper cross-linking reinforces your bidirectional identity graph.

- [ ] **3.1 Display Name & Headline**
  - **First Name:** `Hadi`
  - **Last Name:** `Jafari`
  - **Headline:** `Django Developer | AI & Soft Computing MSc Student | Co-founder & CTO at Vira Kavane Zista`

- [ ] **3.2 Custom Action / Website Button (Creator Mode or Premium accounts)**
  - If your account supports it, click **Edit** (pencil icon) on your profile intro.
  - Under **Custom button**, select **Link**:
    - **Link:** `https://hadij.ir/`
    - **Link text:** `Personal Portfolio (hadij.ir)`

- [ ] **3.3 Contact Info (Available on all accounts)**
  - In your profile intro, click **Contact info**.
  - Under **Website**, set URL to `https://hadij.ir` and select type `Personal`.

---

## 4. Off-Page Entity Signals (IndieWeb & High-Authority Profiles)

Surround your core domains (`hadij.ir` and `github.com/haadijafari`) with trusted 3rd-party profile anchors:

- [ ] **4.1 Gravatar (`https://gravatar.com`)**
  - Claim or update your Gravatar profile under your primary email (`haadijafari2003@gmail.com`).
  - Set Display Name to `Hadi Jafari`.
  - Upload the same portrait photo (`hadi-jafari.jpg`).
  - Add verified links to `https://hadij.ir` and `https://github.com/haadijafari`.

- [ ] **4.2 Technical Blogging (Dev.to / Medium / Hashnode)**
  - Register or update profile with handle `@haadijafari` and full name **Hadi Jafari**.
  - Link bio to `https://hadij.ir`.
  - When publishing technical articles (e.g. on Django, AI, ML), include an author bio line linking back to `https://hadij.ir`.

---

## 5. Monitoring & Knowledge Graph Tracking

- **Week 1:** Check Search Console **Coverage / Pages** report to verify `https://hadij.ir/` is indexed.
- **Week 2:** Search in Google incognito mode:
  - `"Hadi Jafari" hadij`
  - `"Hadi Jafari" github`
  - `"Hadi Jafari" django`
- **Weeks 3–6:** Search `"Hadi Jafari"`. Monitor the rise of `hadij.ir` and `github.com/haadijafari` to the top positions and verify Google knowledge panel emergence.
