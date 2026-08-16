# Singla Lab — website

Source for **https://www.jitinsingla.in** — the site of the Singla Lab,
Department of Biosciences and Bioengineering, IIT Roorkee. GitHub serves it from
`singla-lab.github.io`, which redirects to the custom domain.

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
| `_data/teaching.json` | The term-by-term course list on Teaching |
| `_data/courses.json` | Full course pages, and the self-learning page |
| `_data/news.json` | News timeline |
| `_data/recommended.json` | Books, channels, people, links, music |
| `_data/gallery.json` | Gallery figures and captions |
| `_data/join.json` | Join-us routes and lab philosophy |

Text fields accept inline HTML — `<em>`, `<strong>`, `<a href="…">`. Bare
ampersands are escaped for you, so `Biosciences & Bioengineering` is fine as-is.

In `_data/courses.json` you can also write links as `[label](url)`, which is
shorter than an anchor tag and reads better inside a table cell. Anything
starting `http` opens in a new tab; `mailto:` links do not.

### Common edits

**Add a lab member** — add an entry to the right group in `_data/people.json`:

```json
{ "name": "Ravi Kumar", "role": "Ph.D. Student", "dept": "CSE Department",
  "email": "ravi_k@cs.iitr.ac.in", "photo": "ravi-kumar" }
```

Omit `"photo"` and the card shows tidy initials instead — no broken image.

Add `"link": "https://…"` and the name becomes a link to that person's own page —
a faculty profile, a lab site, a LinkedIn profile. It opens in a new tab. Works
in both the photo cards and the compact name lists.

**Add the photo** — drop any size or shape of image in and let the script crop it:

```powershell
.\tools\add-photo.ps1 -Source "C:\path\to\Ravi.jpg" -Slug ravi-kumar
```

It writes a 480×480 JPEG to `assets/img/people/ravi-kumar.jpg`. If the crop cuts
off a face, pass `-TopBias 0.05` (crop higher) or `-TopBias 0.4` (lower). When
the subject is small in a wide frame, give an explicit square instead:
`-CropSide 360 -CropX 70 -CropY 60`, in source pixels.

Portraits are displayed as circles, so keep the face near the middle — the
corners of the square get clipped.

**Move someone to alumni** — cut their entry from `people.json` and paste it into
the matching group in `alumni.json`. Alumni portraits render in greyscale and
turn to colour on hover; the photo file does not need changing.

**Change a course card's picture** — set `"art"` on the course in
`_data/courses.json` to one of the motifs in `_svg/`: `ml` (a decision
boundary through two classes), `dl` (a fully connected network), `conv` (a
kernel and its feature maps). Omit it and you get `ml`. The self-paced card
uses `crs-self.svg`. These are hand-written SVG in the same token colours as
the rest of the site, so they follow the theme — draw a new one at 320×180 and
name it `crs-<key>.svg`.

**Add a course page** — append an object to `courses` in `_data/courses.json`.
`slug` decides the filename (`"bec351-2027"` → `course-bec351-2027.html`), and
`code` + `term` must match the entry in `_data/teaching.json` for the term list
to link to it. Everything else is optional: leave out `announcements`,
`assignments`, `past_papers` or `sanskrit` and those sections simply do not
render. Schedule rows are arrays lining up with `schedule.columns`; an empty
string becomes an em dash.

**Start a new run of an existing course** — copy the previous year's object,
change `slug`, `term` and `schedule.rows`, move `"current": true` across, and
add the old exam papers to the new page's `past_papers`.

**Retire a research thread** — add `"past": true` to its entry in
`_data/research.json` and delete its `"num"`. It disappears from the home page
and moves into the *Earlier threads* panel at the foot of Research, which is
closed until a reader opens it. Renumber the remaining threads `01`, `02`, … and
update `intro` so the count still reads true. Bringing one back is the reverse.

**Add a publication** — add an object to the `publications` array in
`_data/publications.json`. `type` is one of `journal`, `conference`, `preprint`,
`chapter`, `poster`; `topic` must be a key from the `topics` map at the bottom of
the file. Ordering is automatic — newest year first, journals before preprints.
Add `"link"` for a DOI or arXiv URL and a *Read* button appears.

**Add a news item** — prepend to `items` in `_data/news.json`. The first entry
gets the highlighted marker on the timeline.

**Add a video to Recommended** — save the thumbnail, then add the entry:

```powershell
.\tools\add-thumb.ps1 -VideoId oZ72uTWla5Q
```

That writes a 640×360 JPEG to `assets/img/media/yt/`, cropping to 16:9 if the
only size YouTube offers is the letterboxed one. Then add to a `"kind":
"videos"` section in `_data/recommended.json`:

```json
{ "yt": "oZ72uTWla5Q", "title": "Shankara", "meta": "Rishab Rikhiram Sharma" }
```

The build makes the watch URL from `yt`, so there is no link to keep in sync.
Thumbnails are copied into the repository rather than hot-linked from
`i.ytimg.com` — otherwise the page would report every reader to Google before
they clicked anything.

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

### Custom domain

The site answers on `www.jitinsingla.in`. That domain used to point at a Google
Site; it was moved here in August 2026.

`"url"` in `_data/site.json` is the single place the domain is written down.
`build.py` uses it for the canonical tags, `sitemap.xml`, `robots.txt` **and**
for the root `CNAME` file, which is the file GitHub Pages reads to decide which
host to answer on. Change that one string, rebuild, and everything follows. Set
it back to a `github.io` address and the `CNAME` file is simply not emitted —
though note that a stale one already committed would have to be deleted by hand.

The zone at the registrar holds:

| Type | Name | Value |
|---|---|---|
| CNAME | `www` | `singla-lab.github.io.` |
| A | `@` | `185.199.108.153`, `.109.153`, `.110.153`, `.111.153` |
| AAAA | `@` | `2606:50c0:8000::153`, `:8001::153`, `:8002::153`, `:8003::153` |

The apex records exist so `jitinsingla.in` redirects to the `www` host rather
than failing. Everything else in that zone — five `MX`, the SPF and DKIM `TXT`
records, two `gv-*.dv.googlehosted.com` verification `CNAME`s — belongs to
Google Workspace email and must be left alone.

---

## Design notes

- **Two themes, one token block.** Light is terracotta paper (`--paper:
  #F9EBDE`) with a deep indigo primary opposite it; dark keeps the ground warm
  (`#17120E`) and lifts the blues and greens rather than darkening them.

  Nothing in the stylesheet below `:root` names a colour directly — a theme is
  a matter of redefining tokens. Two habits keep that true: every colour comes
  from a token, and any pair that must stay legible together is defined as a
  pair (`--indigo` with `--on-primary`, `--band` with `--on-band`). If you add
  a rule, reach for a token; if none fits, add one to *both* blocks.

  Both themes clear WCAG AA on every text pair. Light: ink 15.2:1, `--ink-2`
  8.4:1, `--ink-3` 5.2:1, link 4.9:1, saffron 4.8:1, teal 4.9:1. Dark: ink
  16.2:1, `--ink-3` 7.1:1, link 10.7:1. `--ink-4` is deliberately below that
  bar and is for rules, bullets and icons — never for text.

- **The theme switch** sits in the header at every width. A three-line script
  in `<head>` reads `localStorage.theme`, falls back to the system preference
  and stamps `data-theme` on `<html>` before first paint, so there is no flash
  and the stylesheet needs no `prefers-color-scheme` block. Without JavaScript
  the site stays light. While no explicit choice is stored, `site.js` keeps
  following the system if it changes.

- **The SVG art follows the theme** because it is inlined rather than loaded
  as `<img>` — the `fill` and `stroke` attributes hold `var(--token)`.
  `_svg/logo.svg` is the exception: `build.py` also writes it out as the
  favicon, and a standalone SVG has no `:root` to read from, so it keeps
  literal colours and the inline copy is recoloured through its `lg-*`
  classes.
- **Type**: Newsreader (display serif), Inter (text), JetBrains Mono (labels and
  numbers), Tiro Devanagari Hindi for every Sanskrit line (`--f-sa`). Loaded from
  Google Fonts with full system fallbacks, so the site still reads correctly if
  the fonts fail to load.
- **The home-page quote is set on one line** — `.q` is `white-space: nowrap` and
  its size follows the viewport. A much longer quote will therefore render small
  rather than wrap; shorten the text or drop the `nowrap` if that happens.
- **Graphics** in `_svg/` are hand-written SVG, not exports — edit them in a text
  editor. `hero.svg` is a stylised tomographic slice; the `art-*.svg` files
  illustrate each research area.
- **Animation** is subtle and always disabled under `prefers-reduced-motion`.
- **The four numbers on the home page are counted, not typed.** Each entry in
  `stats` in `_data/site.json` carries a `"count"` naming what to tally —
  `publications`, `doctoral`, `alumni` or `projects` — and `build.py` counts it
  from the corresponding JSON file at build time. Add a paper or a grant and the
  front page follows on the next build. A literal `"value"` still works if you
  ever need a number that isn't in the data.

  The publications figure counts journal and conference papers only — that is
  the `"types"` list on that entry. Widen it to include `"chapter"` or
  `"preprint"`, or drop the key entirely to count everything on the
  publications page. The page itself always lists all of it either way.
- **Cache busting**: the stylesheet and script are linked with a `?v=` content
  hash, regenerated on every build. GitHub Pages serves them with a ten-minute
  cache and no fingerprint of its own, so without this a returning reader can
  sit on the old design after a deploy. If a design change ever seems not to
  have landed, check the hash in the page source before blaming the deploy.
- Total repository weight is around 3.5 MB, so the site loads fast on a poor
  connection.

## Accessibility

Skip link, semantic landmarks, `aria-current` on the active nav item, keyboard
operable menu with Escape to close, visible focus rings, alt text on every
photograph and `role="img"` with labels on the decorative SVGs.
