#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Singla Lab site generator.

Reads content from _data/*.json and graphics from _svg/*.svg, and writes plain
static HTML into the repository root. No third-party packages, no network.

    python build.py

Content in the JSON files may contain inline HTML (<em>, <strong>, <a>). Bare
ampersands are escaped automatically, so you can type "A & B" without thinking
about it.
"""

import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, '_data')
SVGD = os.path.join(ROOT, '_svg')

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def load(name):
    with io.open(os.path.join(DATA, name + '.json'), encoding='utf-8') as fh:
        return json.load(fh)


def svg(name):
    with io.open(os.path.join(SVGD, name + '.svg'), encoding='utf-8') as fh:
        return fh.read().strip()


_AMP = re.compile(r'&(?!#?\w+;)')


def a(s):
    """Escape bare ampersands, leaving existing entities and inline HTML alone."""
    if s is None:
        return ''
    return _AMP.sub('&amp;', s)


def attr(s):
    """Escape a string destined for a quoted HTML attribute."""
    if s is None:
        return ''
    return a(s).replace('"', '&quot;')


_LINK = re.compile(r'\[([^\]]+)\]\(([^)\s]+)\)')


def rich(s):
    """Escape, then expand [label](url) into a link. Outbound links open in a
    new tab; mailto and same-site links do not."""
    def repl(m):
        text, href = m.group(1), m.group(2)
        out = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        return '<a href="{0}"{1}>{2}</a>'.format(href, out, text)
    return _LINK.sub(repl, a(s))


def initials(name):
    parts = [p for p in re.split(r'[\s.]+', name.replace('Dr. ', '').replace('Prof. ', '')) if p]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def join(parts):
    return '\n'.join(p for p in parts if p)


ICON = {
    'arrow':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    'mail':   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="M3 7l9 6 9-6"/></svg>',
    'phone':  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6.5 3h3l1.5 4-2 1.5a12 12 0 006.5 6.5L17 13l4 1.5v3a2 2 0 01-2.2 2A17.5 17.5 0 013 5.2 2 2 0 015 3z"/></svg>',
    'pin':    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/></svg>',
    'ext':    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M13 5h6v6M19 5l-9 9M18 14v4a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2h4"/></svg>',
    'menu':   '<svg class="ic-menu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    'x':      '<svg class="ic-x" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
}

SITE = load('site')
BASE = SITE['url'].rstrip('/')

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Inter:wght@300..700&amp;'
    'family=JetBrains+Mono:wght@400..600&amp;'
    'family=Newsreader:ital,wght@0,300..600;1,300..600&amp;'
    'family=Noto+Sans+Devanagari:wght@400..600&amp;display=swap">'
)

FAVICON = (
    '<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">'
    '<link rel="alternate icon" href="assets/img/favicon.svg">'
)


def header(slug):
    links = []
    for item in SITE['nav']:
        cur = ' aria-current="page"' if item['href'] == slug else ''
        links.append('<a href="{0}"{1}>{2}</a>'.format(item['href'], cur, a(item['label'])))
    return """<header class="hdr">
  <div class="wrap hdr-in">
    <a class="brand" href="index.html">
      {logo}
      <span class="brand-txt">
        <span class="brand-name">{name}</span>
        <span class="brand-sub">IIT Roorkee</span>
      </span>
    </a>
    <nav class="nav" id="nav" aria-label="Primary">{links}</nav>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Menu">{menu}{x}</button>
  </div>
</header>""".format(logo=svg('logo'), name=a(SITE['name']), links=''.join(links),
                    menu=ICON['menu'], x=ICON['x'])


def footer():
    c = SITE['contact']
    cols = [
        ('Explore', ['index.html', 'research.html', 'publications.html', 'projects.html', 'gallery.html']),
        ('People',  ['team.html', 'alumni.html', 'teaching.html', 'news.html']),
        ('More',    ['recommended.html', 'contact.html']),
    ]
    label = {i['href']: i['label'] for i in SITE['nav']}
    label['gallery.html'] = 'Gallery'
    colhtml = []
    for title, hrefs in cols:
        items = ''.join('<li><a href="{0}">{1}</a></li>'.format(h, a(label.get(h, h))) for h in hrefs)
        colhtml.append('<div><p class="ftr-h">{0}</p><ul class="ftr-l">{1}</ul></div>'.format(title, items))

    return """<footer class="ftr">
  <div class="wrap">
    <div class="ftr-grid">
      <div>
        <a class="ftr-logo" href="index.html" aria-label="{name} — home">{logofull}</a>
        <p class="sanskrit-line" style="margin-top:1.6rem">{sans}</p>
        <p class="sanskrit-tr">{sanstr}</p>
      </div>
      {cols}
    </div>
    <div class="ftr-bottom">
      <span>&copy; <span data-year>2026</span> {name}. {dept}.</span>
      <span><a href="mailto:{mail}">{mail}</a> &middot; <a href="tel:{tel}">{phone}</a></span>
    </div>
  </div>
</footer>""".format(logofull=svg('logo-full'), name=attr(SITE['name']), cols=''.join(colhtml),
                    sans=SITE['sanskrit']['line'], sanstr=a(SITE['sanskrit']['translation']),
                    dept=a(SITE['institution']), mail=c['email'], tel=c['phone_href'],
                    phone=a(c['phone']))


def page(slug, title, desc, body, body_class='', nav=None):
    """nav lets a sub-page (a course, say) keep its parent lit in the header."""
    full = title if title == SITE['name'] else '{0} — {1}'.format(title, SITE['name'])
    html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{base}/{slug}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{base}/{slug}">
<meta property="og:site_name" content="{name}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBFAF7">
{favicon}
{fonts}
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body{cls}>
<a class="skip" href="#main">Skip to content</a>
{header}
<main id="main">
{body}
</main>
{footer}
<script src="assets/js/site.js" defer></script>
</body>
</html>
"""
    return html.format(title=attr(full), desc=attr(desc), base=BASE, slug=slug,
                       name=attr(SITE['name']), favicon=FAVICON, fonts=FONTS,
                       header=header(nav or slug), body=body, footer=footer(),
                       cls=(' class="' + body_class + '"') if body_class else '')


def write(slug, content):
    with io.open(os.path.join(ROOT, slug), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(content)
    return slug


# --------------------------------------------------------------------------
# shared fragments
# --------------------------------------------------------------------------

def page_head(eyebrow, title, lede=None, extra=''):
    return """<section class="section-tight dotgrid">
  <div class="wrap">
    <p class="eyebrow">{eb}</p>
    <h1 class="h1 measure">{t}</h1>
    {lede}
    {extra}
  </div>
</section>""".format(eb=a(eyebrow), t=a(title),
                     lede='<p class="lede measure" style="margin-top:1.1rem">{0}</p>'.format(a(lede)) if lede else '',
                     extra=extra)


def outbound(p, text):
    """Wrap text in a link to the person's own page, when we have one."""
    if not p.get('link'):
        return text
    return '<a href="{0}" target="_blank" rel="noopener">{1}</a>'.format(attr(p['link']), text)


def person_card(p, alum=False):
    name = p['name']
    display = name + (', ' + p['suffix'] if p.get('suffix') else '')

    photo = p.get('photo')
    if photo:
        img = '<img src="assets/img/people/{0}.jpg" alt="{1}" loading="lazy" width="480" height="480">'.format(
            photo, attr(name))
    else:
        img = '<div class="person-init" aria-hidden="true">{0}</div>'.format(initials(name))

    bits = ['<div class="person">',
            '<div class="person-img">{0}</div>'.format(img),
            '<p class="person-name">{0}</p>'.format(outbound(p, a(display)))]

    # primary line: the role, or the year when there is no role
    role = p.get('role') or (p.get('year') if not p.get('org') else None)
    if role:
        bits.append('<p class="person-role">{0}</p>'.format(a(role)))

    # secondary line: affiliation, then a year if it was not already used
    for key in ('org', 'dept'):
        if p.get(key):
            bits.append('<p class="person-dept">{0}</p>'.format(a(p[key])))
    if p.get('year') and p.get('year') != role:
        bits.append('<p class="person-dept">{0}</p>'.format(a(p['year'])))

    if p.get('note'):
        bits.append('<p class="person-note">{0}</p>'.format(a(p['note'])))
    if p.get('email'):
        bits.append('<a class="person-mail" href="mailto:{0}">{0}</a>'.format(p['email']))
    bits.append('</div>')
    return ''.join(bits)


def cta_band():
    return """<section class="section">
  <div class="wrap">
    <div class="cta-band rv">
      <div>
        <h2 class="h2">Work with us</h2>
        <p class="lede measure-sm" style="margin-top:.6rem">We look for people who want to build, question and grow — not collect credentials.</p>
      </div>
      <a class="btn btn-primary btn-arrow" href="contact.html">See open routes {arrow}</a>
    </div>
  </div>
</section>""".format(arrow=ICON['arrow'])


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def build_home():
    research = load('research')
    pubs = load('publications')
    news = load('news')
    people = load('people')

    stats = ''.join(
        '<div class="stat"><div class="stat-v">{0}</div><div class="stat-l">{1}</div></div>'.format(
            a(s['value']), a(s['label'])) for s in SITE['stats'])

    rows = []
    for area in current_areas(research):
        rows.append("""<a class="rsrch-row" href="research.html#{id}">
  <div class="rsrch-num">{num}</div>
  <div>
    <p class="rsrch-kicker">{kicker}</p>
    <h3 class="rsrch-title">{title}</h3>
    <p class="muted small measure">{summary}</p>
  </div>
  <div class="rsrch-art" aria-hidden="true">{art}</div>
</a>""".format(id=area['id'], num=area['num'], kicker=a(area['kicker']),
               title=a(area['title']), summary=a(area['summary']),
               art=svg('art-' + area['graphic'])))

    recent = [p for p in pubs['publications'] if p['type'] != 'poster'][:5]
    pubhtml = ''.join(pub_item(p, pubs) for p in recent)

    newshtml = ''.join("""<div class="tl-item">
  <p class="tl-date">{date}</p>
  <h3 class="tl-title">{title}</h3>
  <p class="tl-body">{body}</p>
</div>""".format(date=a(n['date']), title=a(n['title']), body=a(n['body']))
        for n in news['items'][:3])

    partners = ''.join('<li>{0}</li>'.format(a(p)) for p in SITE['partners'])
    pi = people['pi']

    body = """<section class="hero dotgrid">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <p class="eyebrow rv">Singla Lab &middot; Biosciences &amp; Bioengineering</p>
        <h1 class="display rv">We look for structure &mdash;<br>in cells, in signals,<br>in <span class="accent">Sanskrit</span>.</h1>
        <p class="lede hero-sub rv">{desc}</p>
        <div class="hero-cta rv">
          <a class="btn btn-primary btn-arrow" href="research.html">Explore the research {arrow}</a>
          <a class="btn" href="contact.html">Join the lab</a>
        </div>
      </div>
      <div class="hero-art rv" aria-hidden="false">{hero}</div>
    </div>
  </div>
</section>

<section>
  <div class="wrap"><div class="stats">{stats}</div></div>
</section>

<section class="section quote-band">
  <div class="wrap">
    <p class="q">&ldquo;{qt}&rdquo;</p>
    <p class="attr">{qa}</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head rv">
      <div>
        <p class="eyebrow">What we work on</p>
        <h2 class="h2 measure">Three threads, one question: how do you get from raw measurement to something you can reason about?</h2>
      </div>
      <a class="btn btn-arrow" href="research.html">All research {arrow}</a>
    </div>
    <div class="rsrch-list rv">{rows}</div>
  </div>
</section>

<section class="section section-alt" id="pi">
  <div class="wrap">
    <div class="pi-card rv">
      <div class="pi-photo"><img src="assets/img/people/{pislug}.jpg" alt="{piname}" loading="lazy" width="480" height="480"></div>
      <div>
        <p class="eyebrow">Principal Investigator</p>
        <h2 class="h2">{piname}, {pisuffix}</h2>
        <p class="muted small" style="margin:.5rem 0 1.3rem">{pirole} &middot; {piaffil}</p>
        <div class="measure">{pibio}</div>
        <div class="hero-cta" style="margin-top:1.6rem">
          <a class="btn btn-sm" href="team.html">Meet the team</a>
          <a class="btn btn-sm" href="mailto:{pimail}">{mailicon} {pimail}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head rv">
      <div>
        <p class="eyebrow">Recent work</p>
        <h2 class="h2">Selected publications</h2>
      </div>
      <a class="btn btn-arrow" href="publications.html">All publications {arrow}</a>
    </div>
    <div class="rv" style="border-top:1px solid var(--rule)">{pubs}</div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="sec-head rv">
      <div>
        <p class="eyebrow">Lab notes</p>
        <h2 class="h2">Latest news</h2>
      </div>
      <a class="btn btn-arrow" href="news.html">All news {arrow}</a>
    </div>
    <div class="tl rv">{news}</div>
  </div>
</section>

<section class="section-tight">
  <div class="wrap">
    <p class="eyebrow rv">Collaborating with</p>
    <ul class="partners rv">{partners}</ul>
  </div>
</section>

{cta}""".format(desc=a(SITE['description']), arrow=ICON['arrow'], hero=svg('hero'),
                stats=stats, qt=a(SITE['quote']['text']), qa=a(SITE['quote']['author']),
                rows=''.join(rows), pubs=pubhtml, news=newshtml, partners=partners,
                cta=cta_band(), pislug=pi['photo'], piname=a(pi['name']),
                pisuffix=a(pi['suffix']), pirole=a(pi['role']), piaffil=a(pi['affil'][0]),
                pibio=''.join('<p>{0}</p>'.format(a(x)) for x in pi['bio'][:2]),
                pimail=pi['email'], mailicon=ICON['mail'])

    return write('index.html', page('index.html', SITE['name'], SITE['description'], body))


def current_areas(r):
    return [x for x in r['areas'] if not x.get('past')]


def past_areas(r):
    return [x for x in r['areas'] if x.get('past')]


def area_block(area):
    if area.get('image'):
        fig = ('<figure class="area-fig">'
               '<img src="assets/img/media/{0}.jpg" alt="{1}" loading="lazy">'
               '<figcaption>{2}</figcaption></figure>').format(
                   area['image'], attr(area['title']), a(area['kicker']))
    else:
        fig = ('<figure class="area-fig"><div class="svg-holder">{0}</div>'
               '<figcaption>{1}</figcaption></figure>').format(
                   svg('art-' + area['graphic']), a(area['kicker']))

    tagcls = ['tag', 'tag-warm', 'tag-teal']
    tags = ''.join('<span class="{0}">{1}</span>'.format(
        tagcls[i % 3], a(t)) for i, t in enumerate(area.get('tags', [])))

    # a past thread carries no number -- it is out of the running order
    eb = '{0} &nbsp;&mdash;&nbsp; {1}'.format(area['num'], a(area['kicker'])) \
        if area.get('num') else a(area['kicker'])

    return """<article class="area rv" id="{id}">
  <div>
    <p class="eyebrow">{eb}</p>
    <h2 class="h2">{title}</h2>
    <p class="lede" style="margin:1rem 0 1.4rem">{summary}</p>
    <div class="measure">{body}</div>
    <div class="tags">{tags}</div>
  </div>
  {fig}
</article>""".format(id=area['id'], eb=eb, title=a(area['title']),
                     summary=a(area['summary']),
                     body=''.join('<p>{0}</p>'.format(a(p)) for p in area['body']),
                     tags=tags, fig=fig)


def build_research():
    r = load('research')
    blocks = ''.join(area_block(x) for x in current_areas(r))
    old = past_areas(r)

    # Closed by default, and a plain <details> so it still opens without JS.
    past = """
<section class="section-tight">
  <div class="wrap">
    <details class="past rv" id="past">
      <summary class="past-tab">
        <span class="past-tab-l">Earlier threads</span>
        <span class="past-tab-n">{n}</span>
        <span class="past-tab-c" aria-hidden="true">{chev}</span>
      </summary>
      <div class="past-body">
        <p class="muted small measure" style="margin-bottom:.5rem">{note}</p>
        {blocks}
      </div>
    </details>
  </div>
</section>""".format(n=len(old), chev=ICON['arrow'], note=a(r['past_intro']),
                     blocks=''.join(area_block(x) for x in old)) if old else ''

    body = page_head('Research', 'What the lab works on', r['intro']) + \
        '<section class="section-tight"><div class="wrap">{0}</div></section>'.format(blocks) + \
        past + cta_band()
    return write('research.html', page('research.html', 'Research',
                                       'Research areas of the Singla Lab: soft X-ray tomography, AI for point-of-care diagnostics and Sanskrit language models, with earlier work in cryo-ET and scientific visualization.', body))


def pub_item(p, meta):
    title = a(p['title'])
    if p.get('link'):
        title = '<a href="{0}" target="_blank" rel="noopener">{1}</a>'.format(p['link'], title)

    venue = '<em>{0}</em>'.format(a(p['venue']))
    if p.get('detail'):
        venue += ', ' + a(p['detail'])

    authors = a(p['authors'])
    for name in meta['highlight_authors']:
        authors = authors.replace(a(name), '<b>{0}</b>'.format(a(name)))

    pills = ['<span class="pill pill-{0}">{1}</span>'.format(p['type'], a(meta['types'][p['type']]))]
    if p.get('topic') and p['topic'] in meta['topics']:
        pills.append('<span class="pill">{0}</span>'.format(a(meta['topics'][p['topic']])))
    if p.get('link'):
        pills.append('<a class="btn btn-ghost btn-sm" href="{0}" target="_blank" rel="noopener">Read {1}</a>'.format(
            p['link'], ICON['ext']))

    hl = '<p class="pub-hl">{0}</p>'.format(a(p['highlight'])) if p.get('highlight') else ''

    return """<article class="pub" data-pub data-type="{type}" data-topic="{topic}">
  <p class="pub-t">{title}</p>
  <p class="pub-a">{authors}</p>
  <p class="pub-v">{venue}</p>
  {hl}
  <div class="pub-meta">{pills}</div>
</article>""".format(type=p['type'], topic=p.get('topic', ''), title=title,
                     authors=authors, venue=venue, hl=hl, pills=''.join(pills))


def build_publications():
    d = load('publications')
    pubs = d['publications']
    order = {'journal': 0, 'conference': 1, 'chapter': 2, 'preprint': 3, 'poster': 4}

    chips = ['<button class="chip" data-group="type" data-value="all" aria-pressed="true">All</button>']
    for key, label in d['types'].items():
        chips.append('<button class="chip" data-group="type" data-value="{0}" aria-pressed="false">{1}</button>'.format(key, a(label)))
    for key, label in d['topics'].items():
        chips.append('<button class="chip" data-group="topic" data-value="{0}" aria-pressed="false">{1}</button>'.format(key, a(label)))

    years = sorted({p['year'] for p in pubs}, reverse=True)
    blocks = []
    for y in years:
        group = sorted([p for p in pubs if p['year'] == y], key=lambda p: order.get(p['type'], 9))
        blocks.append("""<div class="pub-year" data-year-block>
  <div class="pub-year-n">{y}</div>
  <div>{items}</div>
</div>""".format(y=y, items=''.join(pub_item(p, d) for p in group)))

    talks = ''.join("""<div class="tl-item">
  <p class="tl-date">{kind}{detail}</p>
  <h3 class="tl-title">{title}</h3>
  <p class="tl-body">{venue}</p>
</div>""".format(kind=(a(t['kind']) + ' &middot; ') if t.get('kind') else '',
                 detail=a(t.get('detail', str(t['year']))), title=a(t['title']),
                 venue=a(t['venue'])) for t in d['talks'])

    extra = ('<div class="filters" data-filters style="margin-top:2rem">{0}</div>'
             '<p class="small muted"><span data-pub-count>{1}</span> entries shown</p>').format(
                 ''.join(chips), len(pubs))

    body = page_head('Publications', 'Papers, preprints, chapters and posters',
                     'Peer-reviewed articles, preprints, conference papers, book chapters and posters. '
                     'Use the filters to narrow by type or topic.', extra) + \
        '<section class="section-tight"><div class="wrap">{0}</div></section>'.format(''.join(blocks)) + \
        """<section class="section section-alt">
  <div class="wrap">
    <p class="eyebrow rv">Talks, panels &amp; workshops</p>
    <h2 class="h2 rv" style="margin-bottom:2.5rem">Speaking</h2>
    <div class="tl rv">{0}</div>
  </div>
</section>""".format(talks)

    return write('publications.html', page('publications.html', 'Publications',
                                           'Publications from the Singla Lab at IIT Roorkee — journals, preprints, conference papers, book chapters and posters.', body))


def build_projects():
    d = load('projects')
    blocks = []
    for g in d['groups']:
        cards = []
        for p in g['projects']:
            meta = []
            if p.get('partners'):
                meta.append('<p class="proj-p">{0}</p>'.format(a(p['partners'])))
            if p.get('summary'):
                meta.append('<p class="proj-s">{0}</p>'.format(a(p['summary'])))
            cards.append("""<article class="proj rv">
  <div class="proj-top">
    <span class="agency">{agency}</span>
    <span class="role">{role}</span>
    <span class="status {sc}" style="margin-left:auto">{status}</span>
  </div>
  <h3 class="proj-t">{title}</h3>
  {meta}
</article>""".format(agency=a(p['agency']), role=a(p['role']), title=a(p['title']),
                     status=a(g['status']), sc='status-done' if g['status'] == 'Completed' else '',
                     meta=''.join(meta)))
        blocks.append("""<div style="margin-bottom:3rem">
  <p class="eyebrow rv">{title}</p>
  <div class="grid g2">{cards}</div>
</div>""".format(title=a(g['title']), cards=''.join(cards)))

    body = page_head('Projects', 'Sponsored research', d['intro']) + \
        '<section class="section-tight"><div class="wrap">{0}</div></section>'.format(''.join(blocks)) + \
        cta_band()
    return write('projects.html', page('projects.html', 'Sponsored Projects',
                                       'Sponsored research projects led by or involving the Singla Lab — ICMR, SERB-DST, MeitY, MoE-IKS and STARS.', body))


def build_team():
    d = load('people')
    pi = d['pi']

    # The PI's bio and education live on the home page; this page only needs
    # enough to say who he is, then point there.
    groups = []
    for g in d['groups']:
        cls = 'people people-sm' if g.get('compact') else 'people'
        if g.get('compact'):
            items = ''.join('<li>{0} <span>{1}</span></li>'.format(
                outbound(m, a(m['name'])), a(m.get('dept', ''))) for m in g['members'])
            grid = '<ul class="namelist">{0}</ul>'.format(items)
        else:
            grid = '<div class="{0}">{1}</div>'.format(cls, ''.join(person_card(m) for m in g['members']))
        groups.append("""<div style="margin-bottom:3.2rem">
  <div class="sec-head rv" style="margin-bottom:1.5rem">
    <div>
      <p class="eyebrow">{title}</p>
      <p class="muted small measure">{blurb}</p>
    </div>
  </div>
  <div class="rv">{grid}</div>
</div>""".format(title=a(g['title']), blurb=a(g.get('blurb', '')), grid=grid))

    collab = '<div class="people people-sm">{0}</div>'.format(
        ''.join(person_card(c) for c in d['collaborators']))

    body = page_head('Team', 'The people doing the work') + """
<section class="section-tight">
  <div class="wrap">
    <div class="pi-mini rv" style="padding-bottom:2.4rem;border-bottom:1px solid var(--rule)">
      <div class="pi-photo"><img src="assets/img/people/{slug}.jpg" alt="{name}" width="480" height="480"></div>
      <div>
        <p class="eyebrow">Principal Investigator</p>
        <h2 class="h2">{name}, {suffix}</h2>
        <p class="pi-line" style="margin-top:.3rem">{role}</p>
        <p class="pi-line">{affil}</p>
        <a class="person-mail" href="mailto:{mail}">{mail}</a>
        <div class="hero-cta" style="margin-top:1.1rem">
          <a class="btn btn-sm btn-arrow" href="index.html#pi">Full profile {arrow}</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">{groups}</div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="sec-head rv">
      <div>
        <p class="eyebrow">Collaborators</p>
        <h2 class="h2">People we work with</h2>
      </div>
    </div>
    <div class="rv">{collab}</div>
  </div>
</section>

<section class="section-tight">
  <div class="wrap">
    <div class="cta-band rv">
      <div>
        <h2 class="h2">Former members</h2>
        <p class="lede measure-sm" style="margin-top:.6rem">Sixty-plus students, interns and staff have passed through the lab.</p>
      </div>
      <a class="btn btn-primary btn-arrow" href="alumni.html">See alumni {arrow}</a>
    </div>
  </div>
</section>""".format(slug=pi['photo'], name=a(pi['name']), suffix=a(pi['suffix']),
                     role=a(pi['role']), affil='<br>'.join(a(x) for x in pi['affil']),
                     mail=pi['email'],
                     groups=''.join(groups), collab=collab, arrow=ICON['arrow'])

    return write('team.html', page('team.html', 'Team',
                                   'Members of the Singla Lab at IIT Roorkee — doctoral researchers, undergraduate researchers and collaborators.', body))


def build_alumni():
    d = load('alumni')
    blocks = []
    for g in d['groups']:
        if g.get('compact'):
            items = ''.join('<li>{0} <span>{1}{2}</span></li>'.format(
                outbound(m, a(m['name'])), a(m.get('year', '')),
                ' &middot; ' + a(m['dept']) if m.get('dept') else '') for m in g['members'])
            grid = '<ul class="namelist">{0}</ul>'.format(items)
        else:
            grid = '<div class="people people-sm is-alum">{0}</div>'.format(
                ''.join(person_card(m, alum=True) for m in g['members']))
        blocks.append("""<div style="margin-bottom:3.2rem">
  <p class="eyebrow rv">{title} <span class="muted" style="letter-spacing:0;text-transform:none">&mdash; {n}</span></p>
  <div class="rv">{grid}</div>
</div>""".format(title=a(g['title']), n=len(g['members']), grid=grid))

    body = page_head('Alumni', 'Former members',
                     'People who built things here and moved on. Photographs turn colour on hover.') + \
        '<section class="section-tight"><div class="wrap">{0}</div></section>'.format(''.join(blocks)) + \
        cta_band()
    return write('alumni.html', page('alumni.html', 'Alumni',
                                     'Former doctoral, postgraduate, undergraduate and intern members of the Singla Lab at IIT Roorkee.', body))


def build_teaching():
    d = load('teaching')
    pages = {(c['code'], c['term']): course_slug(c) for c in load('courses')['courses']}

    terms = []
    for t in d['terms']:
        courses = []
        for c in t['courses']:
            href = pages.get((c['code'], t['term']))
            row = """<span class="course-c">{code}</span>
  <span class="course-n">{name}</span>
  {note}""".format(code=a(c['code']), name=a(c['name']),
                   note='<span class="course-note">{0}</span>'.format(a(c['note'])) if c.get('note') else '')
            if href:
                courses.append('<a class="course course-link" href="{0}">{1}<span class="course-go">{2}</span></a>'.format(
                    href, row, ICON['arrow']))
            else:
                courses.append('<div class="course">{0}</div>'.format(row))
        terms.append('<div class="term rv"><div class="term-l {0}">{1}</div><div>{2}</div></div>'.format(
            'term-now' if t.get('current') else '', a(t['term']), ''.join(courses)))

    # one block of cards per semester, in the order the courses are listed
    by_term, order = {}, []
    for c in load('courses')['courses']:
        if c['term'] not in by_term:
            by_term[c['term']] = []
            order.append(c['term'])
        by_term[c['term']].append(c)

    def card_group(title, note, cards, now=False):
        return """<div class="crs-group rv">
  <p class="crs-group-t">{title}{note}</p>
  <div class="crs-cards">{cards}</div>
</div>""".format(title=a(title), cards=''.join(cards),
                 note='<span class="crs-group-n{0}">{1}</span>'.format(
                     ' crs-group-now' if now else '', a(note)) if note else '')

    groups = []
    for term in order:
        cards = []
        running = False
        for c in by_term[term]:
            running = running or bool(c.get('current'))
            cards.append("""<a class="crs-card" href="{href}">
  <span class="crs-code">{code}</span>
  <span class="crs-card-n">{name}</span>
  <span class="crs-card-t">{state}</span>
  <span class="crs-card-b">{blurb}</span>
</a>""".format(href=course_slug(c), code=a(c['code']), name=a(c['name']),
               state='Running now' if c.get('current') else 'Completed',
               blurb=a(c['blurb'])))
        groups.append(card_group(term, 'in progress' if running else 'completed', cards, now=running))

    groups.append(card_group('Any time', 'no enrolment, no deadline', ["""<a class="crs-card crs-card-alt" href="self-learning.html">
  <span class="crs-code">&#8734;</span>
  <span class="crs-card-n">Self-learning</span>
  <span class="crs-card-t">Work at your own pace</span>
  <span class="crs-card-b">Notes to work through on your own, shared by the lab and its friends.</span>
</a>"""]))

    body = page_head('Teaching', 'Courses', d['intro']) + """
<section class="section-tight">
  <div class="wrap">
    <p class="eyebrow rv">Course pages</p>
    {groups}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <p class="eyebrow rv">Everything taught, term by term</p>
    <div style="margin-top:1.2rem">{terms}</div>
  </div>
</section>
<section class="section quote-band">
  <div class="wrap">
    <p class="q" style="font-family:'Noto Sans Devanagari',serif;font-style:normal">{sk}</p>
    <p class="attr">{tr}</p>
  </div>
</section>""".format(groups=''.join(groups), terms=''.join(terms),
                     sk=d['quote']['text'], tr=a(d['quote']['translation']))

    return write('teaching.html', page('teaching.html', 'Teaching',
                                       'Courses taught by Jitin Singla at IIT Roorkee in machine learning, deep learning, algorithms and computational biology.', body))


# --------------------------------------------------------------------------
# course pages
# --------------------------------------------------------------------------

def course_slug(c):
    return 'course-{0}.html'.format(c['slug'])


def verse(v):
    if not v:
        return ''
    lines = '<br>'.join(a(l) for l in v['lines'])
    tr = '<p class="verse-tl">{0}</p>'.format(a(v['transliteration'])) if v.get('transliteration') else ''
    return """<div class="verse rv">
  <p class="verse-sa">{lines}</p>
  {tr}
  <p class="verse-en">{en}</p>
</div>""".format(lines=lines, tr=tr, en=a(v['translation']))


def crs_section(sid, label, inner, alt=False):
    return """<section class="section-tight{alt}" id="{sid}">
  <div class="wrap">
    <p class="eyebrow rv">{label}</p>
    {inner}
  </div>
</section>""".format(sid=sid, label=a(label), inner=inner, alt=' section-alt' if alt else '')


def bullets(items, cls='crs-list'):
    return '<ul class="{0} rv">{1}</ul>'.format(
        cls, ''.join('<li>{0}</li>'.format(rich(i)) for i in items))


def schedule_table(s):
    head = ''.join('<th scope="col">{0}</th>'.format(a(c)) for c in s['columns'])
    rows = []
    for r in s['rows']:
        cells = []
        for i, cell in enumerate(r):
            body = rich(cell) if cell else '<span class="tbl-none">&mdash;</span>'
            if i == 0:
                cells.append('<th scope="row">{0}</th>'.format(body))
            else:
                cells.append('<td>{0}</td>'.format(body))
        rows.append('<tr>{0}</tr>'.format(''.join(cells)))
    return """<div class="tbl-wrap rv" tabindex="0" role="region" aria-label="Course schedule">
  <table class="tbl">
    <thead><tr>{head}</tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>""".format(head=head, rows=''.join(rows))


def build_course(c):
    slug = course_slug(c)
    blocks = []
    jump = []

    def add(sid, label, inner, alt=False):
        jump.append('<a href="#{0}">{1}</a>'.format(sid, a(label)))
        blocks.append(crs_section(sid, label, inner, alt))

    # who, when, where
    info = ''.join("""<div class="crs-cell">
  <p class="crs-k">{k}</p>
  <p class="crs-v">{v}</p>
</div>""".format(k=a(i['label']), v=rich(i['value'])) for i in c['info'])
    add('info', 'Course information',
        '<div class="crs-info rv">{0}</div>'.format(info))

    if c.get('announcements'):
        items = ''.join("""<div class="tl-item rv">
  <p class="tl-date">{d}</p>
  <p class="tl-body" style="margin-top:.3rem">{b}</p>
</div>""".format(d=a(n['date']), b=rich(n['body'])) for n in c['announcements'])
        add('news', 'Announcements', '<div class="tl">{0}</div>'.format(items), alt=True)

    aims = ''
    if c.get('intro'):
        aims += '<p class="lede measure rv" style="margin-bottom:1.4rem">{0}</p>'.format(a(c['intro']))
    aims += bullets(c['objectives'], 'crs-list crs-list-lg')
    aims += '<p class="eyebrow rv" style="margin-top:2.6rem">Prerequisites</p>' + bullets(c['prereqs'])
    add('aims', 'Objectives', aims)

    add('content', 'Course content',
        bullets(c['content'], 'crs-list crs-cols'), alt=True)

    add('schedule', 'Schedule', schedule_table(c['schedule']))

    if c.get('assignments'):
        add('work', 'Assignments', bullets(c['assignments']), alt=True)

    refs = []
    for group in c['references']:
        refs.append('<div class="rv"><p class="crs-k">{0}</p>{1}</div>'.format(
            a(group['heading']), bullets(group['items'])))
    add('refs', 'References and resources',
        '<div class="crs-refs">{0}</div>'.format(''.join(refs)))

    ev = ''.join("""<div class="ev-row">
  <span class="ev-w">{w}</span>
  <span class="ev-l">{l}{n}</span>
</div>""".format(w=a(e['weight']), l=a(e['label']),
                 n='<span class="ev-n">{0}</span>'.format(a(e['note'])) if e.get('note') else '')
        for e in c['evaluation'])
    ev = '<div class="ev rv">{0}</div>'.format(ev)
    if c.get('eval_note'):
        ev += '<p class="muted small rv" style="margin-top:1rem">{0}</p>'.format(a(c['eval_note']))
    if c.get('past_papers'):
        ev += '<p class="eyebrow rv" style="margin-top:2.6rem">Question papers</p>'
        ev += bullets(['<strong>{0}</strong> &mdash; {1}'.format(a(p['term']), p['links'])
                       for p in c['past_papers']])
    add('marks', 'Evaluation', ev, alt=True)

    head = """<section class="section-tight dotgrid">
  <div class="wrap">
    <p class="eyebrow"><a href="teaching.html">Teaching</a> &middot; {term}{now}</p>
    <div class="crs-head">
      <span class="crs-code">{code}</span>
      <h1 class="h1">{name}</h1>
    </div>
    <p class="lede measure" style="margin-top:1.1rem">{blurb}</p>
    {verse}
    <nav class="crs-jump rv" aria-label="On this page">{jump}</nav>
  </div>
</section>""".format(term=a(c['term']), code=a(c['code']), name=a(c['name']),
                     now=' &middot; <span class="crs-now">running now</span>' if c.get('current') else '',
                     blurb=a(c['blurb']), verse=verse(c.get('sanskrit')), jump=''.join(jump))

    body = head + '\n'.join(blocks) + """
<section class="section-tight">
  <div class="wrap">
    <a class="btn btn-arrow" href="teaching.html">All courses {arrow}</a>
  </div>
</section>""".format(arrow=ICON['arrow'])

    desc = '{0} {1}, {2} — course page for {3} at IIT Roorkee: schedule, slides, reading and evaluation.'.format(
        c['code'], c['name'], c['term'], SITE['name'])
    return write(slug, page(slug, '{0} {1}'.format(c['code'], c['name']),
                            desc, body, nav='teaching.html'))


def build_self_learning():
    d = load('courses')['self_learning']
    cards = []
    for it in d['items']:
        by = a(it['author'])
        if it.get('author_link'):
            by = '<a href="{0}" target="_blank" rel="noopener">{1}</a>'.format(attr(it['author_link']), by)
        cards.append("""<div class="sl-card rv">
  <p class="eyebrow">{title}</p>
  <h2 class="h2">{label}</h2>
  <p class="muted small" style="margin-top:.5rem">By {by}</p>
  <p class="measure" style="margin-top:1.1rem">{body}</p>
  <div class="hero-cta" style="margin-top:1.5rem">
    <a class="btn btn-primary btn-arrow" href="{file}" target="_blank" rel="noopener">Open the notes {arrow}</a>
  </div>
</div>""".format(title=a(it['title']), label=a(it['label']), by=by, body=a(it['body']),
                 file=attr(it['file']), arrow=ICON['arrow']))

    body = page_head('Teaching', 'Self-learning', d['intro']) + \
        '<section class="section-tight"><div class="wrap">{0}</div></section>'.format(''.join(cards)) + \
        """<section class="section-tight">
  <div class="wrap"><a class="btn btn-arrow" href="teaching.html">All courses {arrow}</a></div>
</section>""".format(arrow=ICON['arrow'])
    return write('self-learning.html',
                 page('self-learning.html', 'Self-learning',
                      'Material to work through on your own: machine learning notes shared by the Singla Lab at IIT Roorkee.',
                      body, nav='teaching.html'))


def build_news():
    d = load('news')
    items = []
    for n in d['items']:
        img = ''
        if n.get('image'):
            img = '<div class="tl-img"><img src="assets/img/media/{0}.jpg" alt="{1}" loading="lazy"></div>'.format(
                n['image'], attr(n['title']))
        items.append("""<div class="tl-item rv">
  <p class="tl-date">{date}{tag}</p>
  <h3 class="tl-title">{title}</h3>
  <p class="tl-body">{body}</p>
  {img}
</div>""".format(date=a(n['date']),
                 tag=' &middot; ' + a(n['tag']) if n.get('tag') else '',
                 title=a(n['title']), body=a(n['body']), img=img))

    body = page_head('News', 'What has been happening') + \
        '<section class="section-tight"><div class="wrap"><div class="tl">{0}</div></div></section>'.format(''.join(items))
    return write('news.html', page('news.html', 'News',
                                   'News and updates from the Singla Lab at IIT Roorkee.', body))


def build_recommended():
    d = load('recommended')
    out = []
    for s in d['sections']:
        lead = '<p class="lede measure" style="margin-bottom:1.6rem">{0}</p>'.format(a(s['lead'])) if s.get('lead') else ''

        if s['kind'] == 'shelves':
            inner = ''.join("""<div class="shelf">
  <p class="shelf-t">{t}</p>
  <ul class="shelf-items">{items}</ul>
</div>""".format(t=a(sh['title']), items=''.join('<li>{0}</li>'.format(a(i['title'])) for i in sh['items']))
                for sh in s['shelves'])
        elif s['kind'] == 'chips':
            inner = '<div class="chipwrap">{0}</div>'.format(
                ''.join('<span>{0}</span>'.format(a(i['title'])) for i in s['items']))
        elif s['kind'] == 'people':
            inner = '<div class="grid g3">{0}</div>'.format(''.join("""<div class="pcard">
  <p class="pcard-m">{meta}</p>
  <p class="pcard-t">{t}</p>
  <p class="pcard-b">{b}</p>
  <p><a class="btn btn-ghost btn-sm" href="{link}" target="_blank" rel="noopener">Read more {ext}</a></p>
</div>""".format(meta=a(i.get('meta', '')), t=a(i['title']), b=a(i.get('body', '')),
                 link=attr(i['link']), ext=ICON['ext']) for i in s['items']))
        else:
            inner = '<div class="linklist">{0}</div>'.format(''.join("""<a class="linkrow" href="{link}" target="_blank" rel="noopener">
  <span><span class="linkrow-t">{t}</span>{m}</span>
  {ext}
</a>""".format(link=attr(i['link']), t=a(i['title']),
               m='<span class="linkrow-m">{0}</span>'.format(a(i['meta'])) if i.get('meta') else '',
               ext=ICON['ext']) for i in s['items']))

        out.append("""<section class="section-tight rv" id="{id}">
  <div class="wrap">
    <p class="eyebrow">{title}</p>
    {lead}
    {inner}
  </div>
</section>""".format(id=s['id'], title=a(s['title']), lead=lead, inner=inner))

    jump = ''.join('<a class="btn btn-sm" href="#{0}">{1}</a>'.format(s['id'], a(s['title'])) for s in d['sections'])
    body = page_head('Reading', 'Recommended', d['intro'],
                     '<div class="hero-cta" style="margin-top:1.5rem">{0}</div>'.format(jump)) + ''.join(out)
    return write('recommended.html', page('recommended.html', 'Recommended',
                                          'Books, channels, people and webpages recommended by Jitin Singla.', body))


def build_gallery():
    d = load('gallery')
    figs = ''.join("""<figure class="{cls} rv">
  <img src="assets/img/media/{img}.jpg" alt="{alt}" loading="lazy">
  <figcaption>
    <p class="gal-t">{t}</p>
    <p class="gal-c">{c}</p>
  </figcaption>
</figure>""".format(cls=' '.join(x for x in [i.get('span', ''), i.get('kind', '')] if x),
                    img=i['image'], alt=attr(i['title']), t=a(i['title']), c=a(i['caption']))
        for i in d['items'])

    body = page_head('Gallery', 'Figures &amp; moments', d['intro']) + \
        '<section class="section-tight"><div class="wrap"><div class="gal">{0}</div></div></section>'.format(figs)
    return write('gallery.html', page('gallery.html', 'Gallery',
                                      'Figures from the lab\'s published work, and photographs from workshops and conferences.', body))


def build_contact():
    d = load('join')
    c = SITE['contact']

    routes = []
    for r in d['routes']:
        subject = ''
        if r.get('subject'):
            subject = '<p class="subject-line">Subject: {0}</p>'.format(a(r['subject']))
        cta = ''
        if r.get('cta'):
            href = 'mailto:{0}'.format(c['email'])
            if r.get('subject'):
                href += '?subject=' + r['subject'].replace(' ', '%20').replace('[', '%5B').replace(']', '%5D')
            cta = '<a class="btn btn-sm btn-primary" href="{0}">{1} {2}</a>'.format(href, a(r['cta']), ICON['arrow'])
        routes.append("""<article class="route route-{st} rv">
  <p class="route-badge">{lbl}</p>
  <h3 class="h3">{title}</h3>
  <p class="muted" style="margin-top:.5rem">{body}</p>
  {subject}
  {cta}
</article>""".format(st=r['status'], lbl=a(r['status_label']), title=a(r['title']),
                     body=a(r['body']), subject=subject, cta=cta))

    rows = [
        ('mail',  'Email',   '<a href="mailto:{0}">{0}</a>'.format(c['email'])),
        ('phone', 'Office',  '<a href="tel:{0}">{1}</a>'.format(c['phone_href'], a(c['phone']))),
        ('pin',   'Address', '{0}<br>{1}<br>{2}<br>{3}'.format(
            a(c['room']), a(c['department']), a(c['institute']), a(c['city']))),
    ]
    contact_rows = ''.join("""<div class="contact-row">
  {icon}
  <div><p class="contact-k">{k}</p><p class="contact-v">{v}</p></div>
</div>""".format(icon=ICON[i], k=k, v=v) for i, k, v in rows)

    body = page_head('Join us', 'Contact &amp; open routes') + """
<section class="section-tight">
  <div class="wrap">
    <div class="join-grid">
      <div>
        <p class="lede serif-em rv" style="font-size:1.4rem;color:var(--ink);border-left:3px solid var(--saffron);padding-left:1.2rem;margin-bottom:2rem">{lede}</p>
        <div class="measure rv" style="margin-bottom:2.5rem">{phil}</div>
        {routes}
      </div>
      <div>
        <div class="contact-box rv">
          <p class="eyebrow eyebrow-plain">Reach the lab</p>
          {rows}
          <p style="margin-top:1.2rem"><a class="btn btn-sm" href="{map}" target="_blank" rel="noopener">Open in Maps {ext}</a></p>
        </div>
      </div>
    </div>
  </div>
</section>""".format(lede=a(d['lede']),
                     phil=''.join('<p>{0}</p>'.format(a(p)) for p in d['philosophy']),
                     routes=''.join(routes), rows=contact_rows,
                     map=attr(c['map']), ext=ICON['ext'])

    return write('contact.html', page('contact.html', 'Join Us',
                                      'Contact details for the Singla Lab at IIT Roorkee and how to apply for PhD, project and internship positions.', body))


def build_404():
    body = """<section class="section dotgrid" style="min-height:56vh;display:grid;place-items:center;text-align:center">
  <div class="wrap">
    <p class="eyebrow eyebrow-plain" style="justify-content:center">Error 404</p>
    <h1 class="display" style="margin-bottom:1rem">Nothing here.</h1>
    <p class="lede measure" style="margin-inline:auto">That page does not exist &mdash; or it moved when the site was rebuilt. Try the research index or the team page.</p>
    <div class="hero-cta" style="justify-content:center;margin-top:2rem">
      <a class="btn btn-primary" href="index.html">Back home</a>
      <a class="btn" href="research.html">Research</a>
      <a class="btn" href="publications.html">Publications</a>
    </div>
  </div>
</section>"""
    return write('404.html', page('404.html', 'Page not found', 'The page you asked for does not exist.', body))


def build_extras():
    written = []

    # favicon — a miniature of the lab mark
    fav = svg('logo')
    with io.open(os.path.join(ROOT, 'assets', 'img', 'favicon.svg'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(fav + '\n')
    written.append('assets/img/favicon.svg')

    pages = ['index.html', 'research.html', 'publications.html', 'projects.html',
             'team.html', 'alumni.html', 'teaching.html', 'news.html',
             'recommended.html', 'gallery.html', 'contact.html']
    pages += [course_slug(c) for c in load('courses')['courses']] + ['self-learning.html']
    urls = ''.join('  <url><loc>{0}/{1}</loc><changefreq>monthly</changefreq></url>\n'.format(
        BASE, '' if p == 'index.html' else p) for p in pages)
    written.append(write('sitemap.xml',
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n'))

    written.append(write('robots.txt',
        'User-agent: *\nAllow: /\n\nSitemap: {0}/sitemap.xml\n'.format(BASE)))

    # tells GitHub Pages to serve the files as-is instead of running Jekyll
    written.append(write('.nojekyll', ''))
    return written


def main():
    if not os.path.isdir(DATA):
        sys.exit('error: _data/ not found next to build.py')

    built = [
        build_home(), build_research(), build_publications(), build_projects(),
        build_team(), build_alumni(), build_teaching(), build_news(),
        build_recommended(), build_gallery(), build_contact(), build_404(),
    ]
    built += [build_course(c) for c in load('courses')['courses']]
    built += [build_self_learning()]
    built += build_extras()

    print('Built {0} files:'.format(len(built)))
    for b in built:
        size = os.path.getsize(os.path.join(ROOT, b)) if os.path.exists(os.path.join(ROOT, b)) else 0
        print('  {0:<28} {1:>8,} bytes'.format(b, size))


if __name__ == '__main__':
    main()
