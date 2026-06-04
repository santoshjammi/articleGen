#!/usr/bin/env python3
"""
generate_eeat_pages.py
Generates the 7 EEAT-required static pages into dist/
Required before AdSense approval and for Google E-E-A-T signals.

Pages generated:
  dist/about/index.html
  dist/editorial-policy/index.html
  dist/fact-checking-policy/index.html
  dist/corrections-policy/index.html
  dist/privacy-policy/index.html
  dist/terms/index.html
  dist/contact/index.html
"""

import os
import sys
from datetime import datetime

SITE_NAME = "CountrysNews"
SITE_DOMAIN = "countrysnews.com"
BASE_URL = f"https://{SITE_DOMAIN}"
OWNER = "Sai Ameya Technologies LLP"
CONTACT_EMAIL = f"editorial@{SITE_DOMAIN}"
OUTPUT_DIR = "dist"

# ── Shared CSS ────────────────────────────────────────────────────────────────
_STYLE = """
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           background: #f9fafb; color: #111827; line-height: 1.7; }
    header { background: #0f172a; padding: 0 1.5rem; }
    header .inner { max-width: 900px; margin: 0 auto; display: flex;
                    align-items: center; height: 56px; gap: 1rem; }
    header a.logo { color: #f1f5f9; font-weight: 700; font-size: 1.1rem;
                    text-decoration: none; }
    header nav a { color: #94a3b8; font-size: .875rem; text-decoration: none;
                   margin-left: .75rem; }
    header nav a:hover { color: #fff; }
    .hero { background: #0f172a; color: #e2e8f0; padding: 3rem 1.5rem 2.5rem; }
    .hero .inner { max-width: 900px; margin: 0 auto; }
    .hero h1 { font-size: 2rem; font-weight: 700; color: #f1f5f9; margin-bottom: .5rem; }
    .hero p { color: #94a3b8; font-size: 1rem; }
    main { max-width: 900px; margin: 2.5rem auto; padding: 0 1.5rem 4rem; }
    h2 { font-size: 1.25rem; font-weight: 600; color: #0f172a;
         margin: 2rem 0 .75rem; border-left: 3px solid #3b82f6; padding-left: .75rem; }
    h3 { font-size: 1rem; font-weight: 600; margin: 1.25rem 0 .5rem; }
    p, li { font-size: .9375rem; color: #374151; margin-bottom: .75rem; }
    ul { padding-left: 1.5rem; }
    a { color: #2563eb; }
    .last-updated { font-size: .8rem; color: #6b7280; margin-bottom: 1.5rem; }
    .info-box { background: #eff6ff; border: 1px solid #bfdbfe;
                border-radius: .5rem; padding: 1rem 1.25rem; margin: 1.5rem 0; }
    .info-box p { margin: 0; color: #1e40af; }
    footer { background: #0f172a; color: #64748b; text-align: center;
             padding: 1.5rem; font-size: .8rem; margin-top: 4rem; }
    footer a { color: #94a3b8; }
  </style>
"""

# ── Shared header / footer ────────────────────────────────────────────────────
def _header(active_page: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{BASE_URL}/{active_page}/">
  {_STYLE}
</head>
<body>
<header>
  <div class="inner">
    <a class="logo" href="/">{SITE_NAME}</a>
    <nav>
      <a href="/about/">About</a>
      <a href="/editorial-policy/">Editorial</a>
      <a href="/contact/">Contact</a>
    </nav>
  </div>
</header>
"""


def _footer() -> str:
    year = datetime.now().year
    return f"""
<footer>
  <p>&copy; {year} {OWNER} · <a href="/privacy-policy/">Privacy</a> ·
     <a href="/terms/">Terms</a> · <a href="/contact/">Contact</a></p>
  <p style="margin-top:.5rem;">
    <a href="/about/">About</a> ·
    <a href="/editorial-policy/">Editorial Policy</a> ·
    <a href="/fact-checking-policy/">Fact-Checking</a> ·
    <a href="/corrections-policy/">Corrections</a>
  </p>
</footer>
</body></html>
"""


def _write(slug: str, title: str, description: str, body: str) -> None:
    out_dir = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "index.html")

    head_extra = f"""  <title>{title} — {SITE_NAME}</title>
  <meta name="description" content="{description}">
  <meta property="og:title" content="{title} — {SITE_NAME}">
  <meta property="og:url" content="{BASE_URL}/{slug}/">
  <meta property="og:type" content="website">"""

    html = _header(slug).replace(
        "<meta name=\"robots\"", head_extra + "\n  <meta name=\"robots\""
    ) + body + _footer()

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✅ {path}")


# ── Page content ──────────────────────────────────────────────────────────────

def page_about():
    body = f"""
<div class="hero">
  <div class="inner">
    <h1>About {SITE_NAME}</h1>
    <p>Technology intelligence for the AI transformation era.</p>
  </div>
</div>
<main>
  <p class="last-updated">Last updated: {datetime.now().strftime("%B %Y")}</p>

  <div class="info-box">
    <p><strong>{SITE_NAME}</strong> is a technology intelligence platform covering AI infrastructure,
    enterprise transformation, smart mobility, and India's digital economy —
    published by <strong>{OWNER}</strong>.</p>
  </div>

  <h2>Our Mission</h2>
  <p>We publish analytical, research-backed intelligence for builders, operators, and executives
  navigating the AI transformation era. We are not a news wire. We take positions, cite evidence,
  and connect developments to operational consequences.</p>

  <h2>What We Cover</h2>
  <ul>
    <li><strong>AI Infrastructure</strong> — local LLMs, inference economics, AI agents, GPU infrastructure, MLOps</li>
    <li><strong>Enterprise Transformation</strong> — AI adoption, ERP evolution, SaaS modernisation, workflow automation</li>
    <li><strong>Smart Mobility</strong> — EV ecosystems, battery supply chains, AI-powered logistics, charging infrastructure</li>
    <li><strong>India Digital Transformation</strong> — ONDC, UPI, smart cities, startup ecosystem, government AI</li>
  </ul>

  <h2>What We Don't Cover</h2>
  <p>We do not publish generic world news, celebrity content, sports, entertainment, or
  low-information AI rewrites. Our <a href="/editorial-policy/">Editorial Policy</a> defines our standards.</p>

  <h2>Who We Are</h2>
  <p>{SITE_NAME} is owned and operated by <strong>{OWNER}</strong>, a technology publishing and
  intelligence company. Our editorial team combines AI-assisted research with human editorial
  oversight to ensure accuracy, depth, and strategic relevance.</p>

  <h2>Contact</h2>
  <p>For editorial queries, corrections, or partnership enquiries:
     <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
  <p>For our corrections process, see our <a href="/corrections-policy/">Corrections Policy</a>.</p>
</main>
"""
    _write("about", "About Us", f"{SITE_NAME} is a technology intelligence platform for the AI transformation era, published by {OWNER}.", body)


def page_editorial_policy():
    body = f"""
<div class="hero">
  <div class="inner">
    <h1>Editorial Policy</h1>
    <p>Our standards for research, accuracy, and intelligence publishing.</p>
  </div>
</div>
<main>
  <p class="last-updated">Last updated: {datetime.now().strftime("%B %Y")}</p>

  <h2>Editorial Independence</h2>
  <p>{SITE_NAME} maintains full editorial independence. Sponsored content is clearly labelled
  and never influences our editorial coverage. Advertisers and sponsors have no input into
  article selection, framing, or conclusions.</p>

  <h2>Content Standards</h2>
  <p>Every article published on {SITE_NAME} must meet the following criteria:</p>
  <ul>
    <li><strong>Minimum 1,200 words</strong> of substantive analysis</li>
    <li><strong>Named sources and real-world examples</strong> — no anonymous statistics or fabricated data</li>
    <li><strong>Original framing</strong> — we do not republish press releases or rewrite competitor articles</li>
    <li><strong>Pillar alignment</strong> — content must serve one of our four editorial pillars</li>
    <li><strong>7-part mandatory structure</strong>: Context → Why It Matters → Operational Implications →
        Economic Implications → Winners & Losers → Future Outlook → Strategic Takeaway</li>
  </ul>

  <h2>Prohibited Practices</h2>
  <ul>
    <li>Fake or unverifiable statistics ("recent studies show…", "experts say…")</li>
    <li>Keyword stuffing or SEO-first headline writing</li>
    <li>Shallow rewrites of other publications</li>
    <li>Hype language ("revolutionary", "groundbreaking", "unprecedented")</li>
    <li>Unsubstantiated claims or speculation presented as fact</li>
  </ul>

  <h2>AI-Assisted Publishing</h2>
  <p>{SITE_NAME} uses AI-assisted research and drafting tools to accelerate intelligence publishing.
  All AI-generated content passes through editorial review, quality scoring, and human oversight
  before publication. We disclose AI assistance transparently and take full editorial responsibility
  for published content.</p>

  <h2>Corrections</h2>
  <p>Errors are corrected promptly and transparently. See our
     <a href="/corrections-policy/">Corrections Policy</a> for the full process.</p>

  <h2>Contact the Editorial Team</h2>
  <p><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</main>
"""
    _write("editorial-policy", "Editorial Policy",
           f"Our standards for accuracy, sourcing, and intelligence publishing at {SITE_NAME}.", body)


def page_fact_checking_policy():
    body = f"""
<div class="hero">
  <div class="inner">
    <h1>Fact-Checking Policy</h1>
    <p>How we verify claims before publication.</p>
  </div>
</div>
<main>
  <p class="last-updated">Last updated: {datetime.now().strftime("%B %Y")}</p>

  <h2>Our Commitment</h2>
  <p>{SITE_NAME} is committed to publishing accurate, verifiable intelligence. We do not publish
  claims we cannot substantiate.</p>

  <h2>Verification Process</h2>
  <ul>
    <li><strong>Primary sources preferred</strong> — company announcements, regulatory filings,
        academic papers, and official government data</li>
    <li><strong>No anonymous statistics</strong> — all quantitative claims must reference a named source</li>
    <li><strong>Named companies and products</strong> — we verify that cited organisations and products
        exist and that attributed information is accurate</li>
    <li><strong>Date verification</strong> — we confirm the recency of all cited data points</li>
  </ul>

  <h2>AI-Generated Content</h2>
  <p>AI-assisted articles are reviewed for factual accuracy before publication. Any AI-generated
  statistics or claims that cannot be independently verified are removed or clearly marked as
  illustrative estimates.</p>

  <h2>Report an Inaccuracy</h2>
  <p>If you believe a published article contains a factual error, please contact us at
     <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> with the article URL and the specific
     claim in question. We aim to respond within 48 hours.</p>
</main>
"""
    _write("fact-checking-policy", "Fact-Checking Policy",
           f"How {SITE_NAME} verifies claims and maintains accuracy in technology intelligence publishing.", body)


def page_corrections_policy():
    body = f"""
<div class="hero">
  <div class="inner">
    <h1>Corrections Policy</h1>
    <p>How we handle errors and corrections.</p>
  </div>
</div>
<main>
  <p class="last-updated">Last updated: {datetime.now().strftime("%B %Y")}</p>

  <h2>Our Commitment to Accuracy</h2>
  <p>When {SITE_NAME} publishes incorrect information, we correct it promptly, transparently,
  and without attempting to obscure the original error.</p>

  <h2>Correction Process</h2>
  <ul>
    <li><strong>Minor corrections</strong> (spelling, formatting, broken links) — fixed silently within 24 hours</li>
    <li><strong>Factual corrections</strong> — corrected with a visible correction note at the top of the article
        stating the original claim and the correction</li>
    <li><strong>Significant errors</strong> — corrected with an editorial note, and where appropriate,
        the article is updated or retracted</li>
  </ul>

  <h2>How to Report an Error</h2>
  <p>Email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> with:</p>
  <ul>
    <li>The URL of the article containing the error</li>
    <li>The specific claim you believe is incorrect</li>
    <li>Source or evidence supporting the correction</li>
  </ul>
  <p>We aim to acknowledge corrections within 48 hours and resolve them within 5 business days.</p>

  <h2>Retractions</h2>
  <p>In cases of serious factual inaccuracy or editorial failure, {SITE_NAME} will publish a
  formal retraction notice linked to the original article.</p>
</main>
"""
    _write("corrections-policy", "Corrections Policy",
           f"How {SITE_NAME} handles factual errors and publishes corrections.", body)


def page_privacy_policy():
    body = f"""
<div class="hero">
  <div class="inner">
    <h1>Privacy Policy</h1>
    <p>How we collect, use, and protect your information.</p>
  </div>
</div>
<main>
  <p class="last-updated">Last updated: {datetime.now().strftime("%B %Y")}</p>

  <h2>Information We Collect</h2>
  <ul>
    <li><strong>Usage data</strong> — pages visited, time on site, referral source (via Google Analytics, anonymised)</li>
    <li><strong>Newsletter subscriptions</strong> — email address only, with explicit opt-in consent</li>
    <li><strong>Contact forms</strong> — name and email when you reach out to us</li>
  </ul>

  <h2>How We Use Your Information</h2>
  <ul>
    <li>To improve content and site performance using aggregated analytics</li>
    <li>To deliver the newsletter you subscribed to</li>
    <li>To respond to enquiries you send us</li>
  </ul>
  <p>We do not sell, rent, or share your personal information with third parties for marketing purposes.</p>

  <h2>Advertising</h2>
  <p>{SITE_NAME} uses Google AdSense to display contextual advertisements. Google may use cookies
  to serve ads based on your prior visits to this and other websites. You can opt out of
  personalised advertising at <a href="https://www.google.com/settings/ads" rel="nofollow noopener">
  Google Ad Settings</a>.</p>

  <h2>Cookies</h2>
  <p>We use essential cookies for site functionality and analytics cookies (Google Analytics)
  to understand aggregate site usage. You can disable cookies in your browser settings.</p>

  <h2>Data Retention</h2>
  <p>Analytics data is retained for 26 months. Newsletter subscription data is retained until
  you unsubscribe. Contact form submissions are retained for 12 months.</p>

  <h2>Your Rights</h2>
  <p>You may request access to, correction of, or deletion of your personal data by contacting
     <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

  <h2>Contact</h2>
  <p><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</main>
"""
    _write("privacy-policy", "Privacy Policy",
           f"How {SITE_NAME} collects, uses, and protects your information.", body)


def page_terms():
    body = f"""
<div class="hero">
  <div class="inner">
    <h1>Terms &amp; Conditions</h1>
    <p>Terms governing use of {SITE_NAME}.</p>
  </div>
</div>
<main>
  <p class="last-updated">Last updated: {datetime.now().strftime("%B %Y")}</p>

  <h2>Acceptance of Terms</h2>
  <p>By accessing {SITE_DOMAIN}, you agree to these Terms &amp; Conditions.
  If you do not agree, please do not use the site.</p>

  <h2>Intellectual Property</h2>
  <p>All content published on {SITE_NAME} — including articles, analysis, infographics, and
  images — is the property of {OWNER} unless otherwise credited. You may not reproduce,
  republish, or distribute our content without prior written permission.</p>

  <h2>Permitted Use</h2>
  <p>You may share links to our articles. Brief quotations (under 100 words) with attribution
  and a link back to the original are permitted for editorial and educational purposes.</p>

  <h2>Disclaimer</h2>
  <p>Content on {SITE_NAME} is provided for informational purposes only. It does not constitute
  financial, legal, or investment advice. {OWNER} accepts no liability for decisions made
  based on information published on this site.</p>

  <h2>External Links</h2>
  <p>We may link to third-party sites for reference. We are not responsible for the content
  or privacy practices of external websites.</p>

  <h2>Changes to These Terms</h2>
  <p>We may update these terms periodically. Continued use of the site constitutes acceptance
  of updated terms.</p>

  <h2>Contact</h2>
  <p><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</main>
"""
    _write("terms", "Terms & Conditions",
           f"Terms and conditions governing use of {SITE_NAME}.", body)


def page_contact():
    body = f"""
<div class="hero">
  <div class="inner">
    <h1>Contact Us</h1>
    <p>Get in touch with the {SITE_NAME} editorial team.</p>
  </div>
</div>
<main>
  <p class="last-updated">Last updated: {datetime.now().strftime("%B %Y")}</p>

  <div class="info-box">
    <p>For the fastest response, email us directly at
       <strong><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></strong></p>
  </div>

  <h2>Editorial Enquiries</h2>
  <p>To pitch a story, submit a correction, or discuss editorial coverage:
     <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>

  <h2>Corrections &amp; Fact-Checks</h2>
  <p>If you believe an article contains an error, see our
     <a href="/corrections-policy/">Corrections Policy</a> then email us with the article URL
     and specific claim.</p>

  <h2>Sponsorships &amp; Partnerships</h2>
  <p>For sponsorship enquiries, intelligence briefing partnerships, or advertising:
     <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>

  <h2>About the Organisation</h2>
  <p>{SITE_NAME} is published by <strong>{OWNER}</strong>.<br>
  See our <a href="/about/">About page</a> for full details.</p>
</main>
"""
    _write("contact", "Contact Us",
           f"Get in touch with the {SITE_NAME} editorial team for enquiries, corrections, and partnerships.", body)


# ── Main ─────────────────────────────────────────────────────────────────────

def generate_eeat_pages() -> None:
    if not os.path.isdir(OUTPUT_DIR):
        print(f"❌ {OUTPUT_DIR}/ not found — run generateSite_advanced.py first")
        sys.exit(1)

    print("📄 Generating EEAT pages…")
    page_about()
    page_editorial_policy()
    page_fact_checking_policy()
    page_corrections_policy()
    page_privacy_policy()
    page_terms()
    page_contact()
    print(f"\n✅ 7 EEAT pages generated in {OUTPUT_DIR}/")


if __name__ == "__main__":
    generate_eeat_pages()
