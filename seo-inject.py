#!/usr/bin/env python3
"""
seo-inject.py v2 — Inject SEO tags into all Whetstone website pages.
Safe to re-run: removes old injected tags (marked with data-seo-injected) before re-injecting.

IMPORTANT: This version uses simple string insertion, NOT BeautifulSoup re-serialization.
It only touches the <head> section and leaves all other HTML untouched.
"""

import os
import re
import json

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://whetstoneadmissions.com"
OG_IMAGE = f"{DOMAIN}/assets/whetstone_iconY.png"
SITE_NAME = "Whetstone Admissions"
FAVICON_PATH = "/assets/whetstone-favicon.png"

# Pages that are duplicates — canonical points to the primary version
CANONICAL_OVERRIDES = {
    "about-us": "/about/",
    "essay-writing": "/college-essay-coaching/",
    "extracurricular": "/extracurricular-mentorship/",
    "sat": "/sat-tutoring/",
}

# Pages that should NOT be in sitemap (redirects / duplicates)
SITEMAP_EXCLUDE = {"about-us", "essay-writing", "extracurricular", "sat", "academic-tutoring"}

# Regional pages that get LocalBusiness schema
REGIONAL_PAGES = {
    "new-york-city-college-admissions-counseling",
    "manhattan-college-admissions-counseling",
    "brooklyn-college-admissions-counseling",
    "westchester-college-admissions-counseling",
    "scarsdale-college-admissions-counseling",
}

# Sitemap priority levels
SITEMAP_PRIORITIES = {
    "": "1.0",
    "college-admissions-counseling": "0.9",
    "college-essay-coaching": "0.9",
    "contact": "0.9",
    "sat-tutoring": "0.9",
    "extracurricular-mentorship": "0.8",
    "graduate-admissions": "0.8",
    "about": "0.8",
    "results": "0.8",
    "reviews": "0.8",
    "our-method": "0.8",
    "resources": "0.8",
    "language-learning": "0.7",
    "privacy": "0.4",
}

# Team member info for Person schema
TEAM_MEMBERS = {
    "cole": {"name": "Cole Whetstone", "jobTitle": "Founder", "alumniOf": ["Harvard University", "University of Oxford"]},
    "ren": {"name": "Ren", "jobTitle": "Co-Founder"},
    "stephanie": {"name": "Stephanie", "jobTitle": "Essay Specialist", "alumniOf": ["Duke University", "University of North Carolina"]},
    "eric": {"name": "Eric", "jobTitle": "Advisor"},
    "howard": {"name": "Howard", "jobTitle": "Advisor"},
    "christopher": {"name": "Christopher", "jobTitle": "Advisor"},
    "athena": {"name": "Athena", "jobTitle": "Strategy & Technology", "alumniOf": ["Cornell University", "UC Berkeley"]},
}


def get_page_slug(filepath):
    rel = os.path.relpath(os.path.dirname(filepath), SITE_ROOT)
    if rel == ".":
        return ""
    return rel.replace("\\", "/")


def get_canonical_url(slug):
    if slug in CANONICAL_OVERRIDES:
        return f"{DOMAIN}{CANONICAL_OVERRIDES[slug]}"
    if slug == "":
        return f"{DOMAIN}/"
    return f"{DOMAIN}/{slug}/"


def extract_title(content):
    m = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else SITE_NAME


def extract_description(content):
    m = re.search(r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', content, re.IGNORECASE)
    if not m:
        m = re.search(r'<meta\s+[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', content, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "Personalized college admissions counseling in New York City. Expert advisors from Harvard, Oxford, and Princeton."


def extract_faq_questions(content):
    """Extract FAQ Q&A pairs from the HTML using regex.
    Handles two formats:
      1. <button class="faq-q">Question<span>+</span></button> + <div class="faq-a">Answer</div>
      2. <div class="faq-q"><h4>Question</h4></div> + <div class="faq-a">Answer</div>
    """
    faqs = []
    # Pattern 1: button.faq-q followed by div.faq-a
    for m in re.finditer(r'<button\s+class="faq-q"[^>]*>(.*?)</button>\s*<div\s+class="faq-a">(.*?)</div>', content, re.DOTALL):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        a = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if q and a:
            faqs.append({"q": q, "a": a})
    # Pattern 2: div.faq-q (with h4 inside) followed by div.faq-a
    if not faqs:
        for m in re.finditer(r'<div\s+class="faq-q"[^>]*>.*?<h4>(.*?)</h4>.*?</div>\s*<div\s+class="faq-a">(.*?)</div>', content, re.DOTALL):
            q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            a = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            if q and a:
                faqs.append({"q": q, "a": a})
    return faqs


def build_seo_block(slug, title, desc, content):
    """Build the SEO tag block to inject before </head>."""
    canonical_url = get_canonical_url(slug)
    lines = []
    lines.append("")
    lines.append("<!-- SEO TAGS (auto-injected by seo-inject.py — do not edit manually) -->")

    # Canonical
    if 'rel="canonical"' not in content:
        lines.append(f'<link rel="canonical" href="{canonical_url}" data-seo-injected="true">')

    # Favicon
    if 'rel="icon"' not in content:
        lines.append(f'<link rel="icon" type="image/png" href="{FAVICON_PATH}" data-seo-injected="true">')

    # Open Graph
    if 'property="og:title"' not in content:
        lines.append(f'<meta property="og:title" content="{title}" data-seo-injected="true">')
        lines.append(f'<meta property="og:description" content="{desc}" data-seo-injected="true">')
        lines.append(f'<meta property="og:url" content="{canonical_url}" data-seo-injected="true">')
        lines.append(f'<meta property="og:image" content="{OG_IMAGE}" data-seo-injected="true">')
        lines.append(f'<meta property="og:type" content="website" data-seo-injected="true">')
        lines.append(f'<meta property="og:site_name" content="{SITE_NAME}" data-seo-injected="true">')

    # Twitter Card
    if 'name="twitter:card"' not in content:
        lines.append(f'<meta name="twitter:card" content="summary" data-seo-injected="true">')
        lines.append(f'<meta name="twitter:title" content="{title}" data-seo-injected="true">')
        lines.append(f'<meta name="twitter:description" content="{desc}" data-seo-injected="true">')
        lines.append(f'<meta name="twitter:image" content="{OG_IMAGE}" data-seo-injected="true">')

    # JSON-LD Schemas — only inject if not already present (manually or otherwise)

    # Homepage: Organization schema
    if slug == "" and '"EducationalOrganization"' not in content and '"Organization"' not in content:
        org = {
            "@context": "https://schema.org",
            "@type": "EducationalOrganization",
            "name": "Whetstone Admissions",
            "alternateName": "Whetstone Advisory LLC",
            "url": DOMAIN,
            "logo": OG_IMAGE,
            "description": "Personalized college admissions counseling in New York City. Expert advisors from Harvard, Oxford, and Princeton.",
            "address": {"@type": "PostalAddress", "addressLocality": "New York", "addressRegion": "NY", "addressCountry": "US"},
            "sameAs": [],
            "contactPoint": {"@type": "ContactPoint", "contactType": "admissions consulting", "url": f"{DOMAIN}/contact/"}
        }
        lines.append(f'<script type="application/ld+json" data-seo-injected="true">{json.dumps(org, indent=2)}</script>')

    # Regional pages: LocalBusiness schema
    if slug in REGIONAL_PAGES and '"LocalBusiness"' not in content:
        area_names = {
            "new-york-city-college-admissions-counseling": "New York City",
            "manhattan-college-admissions-counseling": "Manhattan, New York",
            "brooklyn-college-admissions-counseling": "Brooklyn, New York",
            "westchester-college-admissions-counseling": "Westchester County, New York",
            "scarsdale-college-admissions-counseling": "Scarsdale, New York",
        }
        area = area_names.get(slug, "New York")
        lb = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": f"Whetstone Admissions — {area}",
            "description": f"College admissions counseling in {area}. Expert advisors from Harvard, Oxford, and Princeton.",
            "url": f"{DOMAIN}/{slug}/",
            "image": OG_IMAGE,
            "address": {"@type": "PostalAddress", "addressLocality": area.split(",")[0], "addressRegion": "NY", "addressCountry": "US"},
            "parentOrganization": {"@type": "EducationalOrganization", "name": "Whetstone Admissions", "url": DOMAIN}
        }
        lines.append(f'<script type="application/ld+json" data-seo-injected="true">{json.dumps(lb, indent=2)}</script>')

    # Team pages: Person schema
    if slug.startswith("team/") and '"Person"' not in content:
        member_key = slug.replace("team/", "")
        info = TEAM_MEMBERS.get(member_key)
        if info:
            person = {
                "@context": "https://schema.org",
                "@type": "Person",
                "name": info["name"],
                "jobTitle": info.get("jobTitle", "Advisor"),
                "url": f"{DOMAIN}/{slug}/",
                "worksFor": {"@type": "EducationalOrganization", "name": "Whetstone Admissions", "url": DOMAIN}
            }
            if "alumniOf" in info:
                person["alumniOf"] = [{"@type": "CollegeOrUniversity", "name": s} for s in info["alumniOf"]]
            lines.append(f'<script type="application/ld+json" data-seo-injected="true">{json.dumps(person, indent=2)}</script>')

    # FAQPage schema (any page with faq-q elements) — skip if page already has FAQPage
    if '"FAQPage"' not in content:
        faqs = extract_faq_questions(content)
        if faqs:
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": f["a"]}
                    }
                    for f in faqs
                ]
            }
            lines.append(f'<script type="application/ld+json" data-seo-injected="true">{json.dumps(faq_schema, indent=2)}</script>')

    # BreadcrumbList for non-homepage — skip if page already has one
    if slug != "" and '"BreadcrumbList"' not in content:
        parts = slug.split("/")
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN}]
        if parts[0] == "team" and len(parts) > 1:
            items.append({"@type": "ListItem", "position": 2, "name": "Team", "item": f"{DOMAIN}/about/"})
            member = TEAM_MEMBERS.get(parts[1], {})
            name = member.get("name", parts[1].capitalize())
            items.append({"@type": "ListItem", "position": 3, "name": name, "item": f"{DOMAIN}/{slug}/"})
        elif parts[0] == "resources" and len(parts) > 1:
            items.append({"@type": "ListItem", "position": 2, "name": "Resources", "item": f"{DOMAIN}/resources/"})
            items.append({"@type": "ListItem", "position": 3, "name": parts[1].replace("-", " ").title(), "item": f"{DOMAIN}/{slug}/"})
        else:
            display = slug.replace("-", " ").replace("/", " — ").title()
            items.append({"@type": "ListItem", "position": 2, "name": display, "item": f"{DOMAIN}/{slug}/"})
        bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}
        lines.append(f'<script type="application/ld+json" data-seo-injected="true">{json.dumps(bc, indent=2)}</script>')

    lines.append("<!-- /SEO TAGS -->")
    lines.append("")

    return "\n".join(lines)


def inject_page(filepath):
    """Inject SEO tags into a single page using string replacement only."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "</head>" not in content.lower():
        print(f"  SKIP (no </head>): {filepath}")
        return False

    slug = get_page_slug(filepath)
    title = extract_title(content)
    desc = extract_description(content)

    # Step 1: Remove previously injected block (between the comment markers)
    content = re.sub(
        r'\n?<!-- SEO TAGS \(auto-injected.*?<!-- /SEO TAGS -->\n?',
        '',
        content,
        flags=re.DOTALL
    )

    # Step 2: Also remove any individual data-seo-injected tags (from v1 script)
    content = re.sub(r'<[^>]+data-seo-injected="true"[^>]*>.*?</script>\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+data-seo-injected="true"[^>]*/?>\s*', '', content)

    # NOTE: We do NOT remove manually-written JSON-LD schemas.
    # We only remove tags we previously injected (via comment block or data-seo-injected attribute).

    # Step 3: Build and inject the new SEO block before </head>
    # Use the cleaned content for checking what already exists
    seo_block = build_seo_block(slug, title, desc, content)

    # Insert right before </head>
    content = content.replace("</head>", seo_block + "</head>", 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Report what was added
    changes = []
    if 'rel="canonical"' in seo_block: changes.append("canonical")
    if 'rel="icon"' in seo_block: changes.append("favicon")
    if 'og:title' in seo_block: changes.append("og")
    if 'twitter:card' in seo_block: changes.append("twitter")
    if 'EducationalOrganization' in seo_block: changes.append("Organization schema")
    if 'LocalBusiness' in seo_block: changes.append("LocalBusiness schema")
    if '"Person"' in seo_block: changes.append("Person schema")
    if 'FAQPage' in seo_block:
        faq_count = len(extract_faq_questions(content))
        changes.append(f"FAQPage ({faq_count}q)")
    if 'BreadcrumbList' in seo_block: changes.append("BreadcrumbList")

    print(f"  ✓ {slug or 'homepage'}: {', '.join(changes)}")
    return True


def fix_sitemap():
    """Regenerate sitemap.xml with all pages."""
    pages = []
    for root, dirs, files in os.walk(SITE_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "assets" and d != "node_modules"]
        if "index.html" in files:
            slug = os.path.relpath(root, SITE_ROOT).replace("\\", "/")
            if slug == ".":
                slug = ""
            if slug not in SITEMAP_EXCLUDE:
                pages.append(slug)
    if "" not in pages:
        pages.append("")
    pages.sort()

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for slug in pages:
        url = f"{DOMAIN}/" if slug == "" else f"{DOMAIN}/{slug}/"
        priority = SITEMAP_PRIORITIES.get(slug, "0.6")
        if slug in REGIONAL_PAGES: priority = "0.7"
        if slug.startswith("team/"): priority = "0.5"
        if slug.startswith("resources/") and slug != "resources": priority = "0.7"
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    with open(os.path.join(SITE_ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n  ✓ sitemap.xml: {len(pages)} URLs")


def main():
    print("=" * 60)
    print("Whetstone SEO Injection Script v2")
    print("(string insertion only — no HTML re-serialization)")
    print("=" * 60)
    print()

    html_files = []
    for root, dirs, files in os.walk(SITE_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "assets" and d != "node_modules"]
        if "index.html" in files:
            html_files.append(os.path.join(root, "index.html"))
    root_index = os.path.join(SITE_ROOT, "index.html")
    if root_index not in html_files:
        html_files.append(root_index)
    html_files.sort()

    print(f"Found {len(html_files)} pages to process.\n")
    for filepath in html_files:
        inject_page(filepath)

    fix_sitemap()
    print()
    print("=" * 60)
    print("Done. All SEO tags injected.")
    print("=" * 60)


if __name__ == "__main__":
    main()