#!/usr/bin/env python3
"""Add scroll-reveal animations to all Whetstone pages that don't have them."""

import os
import re
from bs4 import BeautifulSoup

BASE = "/Users/karenyoo/Desktop/Whetstone_git"

# The IntersectionObserver JS snippet to add
OBSERVER_JS = """
  // Scroll-reveal animations
  var revealObserver = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        var el = entry.target;
        el.classList.add('is-visible');
        revealObserver.unobserve(el);
        var delayMs = parseFloat(el.style.transitionDelay) || 0;
        setTimeout(function() {
          el.style.transitionDelay = '';
          el.classList.remove('scroll-reveal');
        }, delayMs + 950);
      }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('.scroll-reveal').forEach(function(el) {
    revealObserver.observe(el);
  });
"""

# Pages to skip (already have animations, or are redirects/minimal)
SKIP_PAGES = [
    "index.html",  # homepage - has its own animation system
    "sat-tutoring/index.html",
    "college-essay-coaching/index.html",
    "college-admissions-counseling/index.html",
    "extracurricular-mentorship/index.html",
    "academic-tutoring/index.html",  # redirect page
    "sat/index.html",  # minimal redirect-like
    "language-learning/index.html",  # minimal
    "resources/index.html",  # minimal
]

# Elements/selectors to animate within content sections
ANIMATE_SELECTORS = [
    ".section-label",
    ".section-title",
    ".section-sub",
    ".two-col-text",
    ".two-col-img",
    ".step-card",
    ".why-card",
    ".review-card",
    ".feature-item",
    ".quote-block",
    ".team-card",
    ".success-card",
    ".faq-item",
    ".story-card",
]

def find_html_files():
    """Find all index.html files in the project."""
    files = []
    for root, dirs, filenames in os.walk(BASE):
        # Skip hidden dirs, node_modules, .tmp, etc.
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
        for f in filenames:
            if f == "index.html":
                rel = os.path.relpath(os.path.join(root, f), BASE)
                files.append(rel)
    return files

def should_skip(rel_path):
    for skip in SKIP_PAGES:
        if rel_path == skip:
            return True
    return False

def add_animations_to_file(filepath):
    """Add scroll-reveal animations to a single HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has scroll-reveal
    if 'scroll-reveal' in content:
        print(f"  SKIP (already has animations): {filepath}")
        return False

    # Skip if it's a redirect page
    if 'http-equiv="refresh"' in content:
        print(f"  SKIP (redirect): {filepath}")
        return False

    # Skip if very minimal page (less than 50 lines)
    if content.count('\n') < 50:
        print(f"  SKIP (minimal page): {filepath}")
        return False

    soup = BeautifulSoup(content, 'html.parser')

    # Find all content sections (not header, footer, hero, or final-cta)
    sections = soup.find_all('section')

    delay_counter = 0
    elements_animated = 0

    for section in sections:
        # Skip header-like and hero sections
        classes = section.get('class', [])
        class_str = ' '.join(classes) if classes else ''

        # Skip hero sections and final CTA
        if 'page-hero' in class_str or 'final-cta' in class_str or 'contact-hero' in class_str:
            continue

        # Reset delay counter for each section
        delay_counter = 0

        # Animate section labels
        for el in section.find_all('p', class_='section-label'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        # Animate section titles (h2)
        for el in section.find_all('h2'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        # Animate section-sub paragraphs
        for el in section.find_all('p', class_='section-sub'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        # Animate two-col elements
        for el in section.find_all('div', class_='two-col-text'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        for el in section.find_all('div', class_='two-col-img'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        # Animate cards (step-card, why-card, review-card, team-card, success-card)
        card_classes = ['step-card', 'why-card', 'review-card', 'team-card', 'success-card', 'story-card']
        for card_class in card_classes:
            for el in section.find_all('div', class_=card_class):
                if 'scroll-reveal' not in (el.get('class') or []):
                    el['class'] = el.get('class', []) + ['scroll-reveal']
                    el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                    delay_counter += 1
                    elements_animated += 1

        # Animate feature items
        for el in section.find_all('div', class_='feature-item'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        # Animate quote blocks
        for el in section.find_all('div', class_='quote-block'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        # Animate FAQ items
        for el in section.find_all('div', class_='faq-item'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

        # Animate standalone review cards with blockquotes (for reviews page)
        for el in section.find_all('div', class_='review-card'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 80}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

    # Also animate profile page elements
    profile_page = soup.find('main', class_='profile-page')
    if profile_page:
        delay_counter = 0
        # Animate profile photo
        for el in profile_page.find_all('div', class_='profile-left'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: 0ms').strip('; ')
                elements_animated += 1

        for el in profile_page.find_all('div', class_='profile-right'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: 160ms').strip('; ')
                elements_animated += 1

    # Also animate team-glass-section team cards
    team_section = soup.find('section', class_='team-glass-section')
    if team_section:
        delay_counter = 0
        for el in team_section.find_all('div', class_='team-card'):
            if 'scroll-reveal' not in (el.get('class') or []):
                el['class'] = el.get('class', []) + ['scroll-reveal']
                el['style'] = (el.get('style', '') + f'; transition-delay: {delay_counter * 100}ms').strip('; ')
                delay_counter += 1
                elements_animated += 1

    if elements_animated == 0:
        print(f"  SKIP (no elements to animate): {filepath}")
        return False

    # Add the observer JS before the closing </body> tag
    # Find the last <script> tag and add observer code to it
    scripts = soup.find_all('script')
    if scripts:
        last_script = scripts[-1]
        # Check if it's the hamburger/scroll script
        if last_script.string and ('hamburger' in last_script.string or 'scroll' in last_script.string):
            last_script.string = last_script.string.rstrip() + '\n' + OBSERVER_JS
        else:
            # Add a new script tag
            new_script = soup.new_tag('script')
            new_script.string = OBSERVER_JS
            body = soup.find('body')
            if body:
                body.append(new_script)

    # Write back
    output = str(soup)
    # Fix self-closing tags that BS4 might mess up
    # BeautifulSoup might change the formatting, so let's use a more careful approach

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))

    print(f"  DONE ({elements_animated} elements): {filepath}")
    return True

def main():
    files = find_html_files()
    print(f"Found {len(files)} HTML files\n")

    modified = 0
    for rel_path in sorted(files):
        if should_skip(rel_path):
            print(f"  SKIP (in skip list): {rel_path}")
            continue

        full_path = os.path.join(BASE, rel_path)
        if add_animations_to_file(full_path):
            modified += 1

    print(f"\nModified {modified} files")

if __name__ == '__main__':
    main()
