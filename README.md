# Singla Lab — website

Source for **https://singla-lab.github.io** — the site of the Singla Lab,
Department of Biosciences and Bioengineering, IIT Roorkee.

Plain static HTML. No framework, no npm, no build server. GitHub Pages serves
the files in this repository exactly as they are.

---

## How it works

Content lives in JSON. A small Python script renders it into static HTML pages
which are committed alongside the sources.

```
_data/*.json      ← the content you edit
_svg/*.svg        ← hand-drawn graphics (logo, hero, research illustrations)
build.py          ← renders _data + _svg into the .html files in the root
*.html            ← generated output — committed, and what GitHub Pages serves
assets/css        ← the design system, one file
assets/js         ← progressive enhancement only; every page works without it
assets/img/people ← 480×480 portraits
assets/img/media  ← figures and photographs
tools/            ← helper scripts
```

Editing the HTML directly works too, but the next `build.py` run overwrites it.
**Edit the JSON.**

---

## Making a change

1. Edit the relevant file in `_data/`.
2. Run the build:

   ```bash
   python build.py
   ```

3. Commit both the JSON and the regenerated HTML, then push. GitHub Pages
   redeploys within a minute or so.

Requires Python 3.6 or newer. Nothing else — no pip install.

### Which file holds what

| File | Page |
| --- | --- |
| `_data/site.json` | Site name, navigation, contact block, footer, home-page stats |
| `_data/people.json` | PI bio, current members, collaborators |
| `_data/alumni.json` | Former members, interns |
| `_data/publications.json` | Papers, preprints, posters, talks |
| `_data/projects.json` | Sponsored projects |
| `_data/research.json` | Research areas |
| `_data/teaching.json` | Courses by term |
| `_data/news.json` | News timeline |
| `_data/recommended.json` | Books, channels, people, links, music |
| `_data/gallery.json` | Gallery figures and captions |
| `_data/join.json` | Join-us routes and lab philosophy |

Text fields accept inline HTML — `<em>`, `<strong>`, `<a href="…">`. Bare
ampersands are escaped for you, so `Biosciences & Bioengineering` is fine as-is.

### Common edits

**Add a lab member** — add an entry to the right group in `_data/people.json`:

```json
{ "name": "Ravi Kumar", "role": "Ph.D. Student", "dept": "CSE Department",
  "email": "ravi_k@cs.iitr.ac.in", "photo": "ravi-kumar" }
```

Omit `"photo"` and the card shows tidy initials instead — no broken image.

**Add the photo** — drop any size or shape of image in and let the script crop it:

```powershell
.\tools\add-photo.ps1 -Source "C:\path\to\Ravi.jpg" -Slug ravi-kumar
```

It writes a 480×480 JPEG to `assets/img/people/ravi-kumar.jpg`. If the crop cuts
off a face, pass `-TopBias 0.05` (crop higher) or `-TopBias 0.4` (lower).

**Move someone to alumni** — cut their entry from `people.json` and paste it into
the matching group in `alumni.json`. Alumni portraits render in greyscale and
turn to colour on hover; the photo file does not need changing.

**Add a publication** — add an object to the `publications` array in
`_data/publications.json`. `type` is one of `journal`, `conference`, `preprint`,
`chapter`, `poster`; `topic` must be a key from the `topics` map at the bottom of
the file. Ordering is automatic — newest year first, journals before preprints.
Add `"link"` for a DOI or arXiv URL and a *Read* button appears.

**Add a news item** — prepend to `items` in `_data/news.json`. The first entry
gets the highlighted marker on the timeline.

---

## Deploying

The site is a **user/organisation Pages site**: the repository is named
`singla-lab.github.io`, so GitHub serves the default branch at the root domain.

```bash
git add -A
git commit -m "Update team page"
git push
```

Settings → Pages should read: **Source: Deploy from a branch · Branch: `main` / `(root)`**.

`.nojekyll` is present, which tells Pages to skip Jekyll and publish the files
verbatim. Do not delete it.

### Custom domain (later)

To serve this at `www.jitinsingla.in`:

1. Add a file named `CNAME` in the repository root containing one line:
   `www.jitinsingla.in`
2. At the DNS registrar, point `www` at `singla-lab.github.io` with a CNAME
   record. For the apex `jitinsingla.in`, add four A records to
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
3. In Settings → Pages, enter the domain and tick **Enforce HTTPS** once the
   certificate is issued.
4. Update `"url"` in `_data/site.json` and rebuild, so canonical links and the
   sitemap point at the new domain.

---

## Design notes

- **Light, editorial-scientific.** Warm off-white paper, one deep indigo
  primary, one burnt-saffron accent, teal for biological objects.
- **Type**: Newsreader (display serif), Inter (text), JetBrains Mono (labels and
  numbers), Noto Sans Devanagari. Loaded from Google Fonts with full system
  fallbacks, so the site still reads correctly if the fonts fail to load.
- **Graphics** in `_svg/` are hand-written SVG, not exports — edit them in a text
  editor. `hero.svg` is a stylised tomographic slice; the `art-*.svg` files
  illustrate each research area.
- **Animation** is subtle and always disabled under `prefers-reduced-motion`.
- Total repository weight is around 3.5 MB, so the site loads fast on a poor
  connection.

## Accessibility

Skip link, semantic landmarks, `aria-current` on the active nav item, keyboard
operable menu with Escape to close, visible focus rings, alt text on every
photograph and `role="img"` with labels on the decorative SVGs.
