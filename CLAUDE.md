# Frontswatch (راصد) — repo layout

This repo is the whole project for frontswatch.com, a map/timeline tracker
of the war in Yemen.

- `src/` — editable source. This is what you change.
  - `app.src.html` — the entire app: markup, CSS, JS (SVG map, timeline, UI).
  - `data.js` — all events (`ROWS`) and governorate-control snapshots (`SNAPS`).
  - `ar.js` — Arabic translations (`AR.rows`, `AR.ui`, etc.), positionally
    parallel to `data.js`.
  - `geo.js` — governorate/district geometry. Rarely needs changes.
  - `pwa/` — icons, manifest, service worker, OG image.
  - `i18n/*.py` — Arabic string source dictionaries (used only when
    regenerating `ar.js` from scratch; day-to-day edits go directly in
    `ar.js`).
  - `build.py` — generates `../site/` from the files above. Run it with
    `python3 build.py` from inside `src/`.
- Design versions: branches `v1.0` (original layout) and `v2.0` (bottom
  sheet + time bar + tab bar) are kept. v3.0 is the feed design: map pinned
  on top, a chronological feed of days below (`#feed`, built by
  `buildFeed`). Scrolling is the time control: `spy()` sets `st.sel` to the
  day crossing a reading line a third of the way down the feed. Tapping a
  card calls `focusEvent(id,false)` (map pans to it); tapping a marker calls
  `focusEvent(id,true)` (feed scrolls to the card). One filter row
  (`#filters`); everything else is in the `#menu` dialog. Above 900px it is
  map + feed column. The interface accent is amber (`--acc`) so it never
  reads as a faction colour. New UI strings go in `AR.ui`.
- `site/` — generated output. **Never hand-edit.** This is the exact
  folder Cloudflare Pages deploys (Pages build output directory = `site`).

## Adding a new event

1. Add an entry to `ROWS` in `src/data.js`:
   `['YYYY-MM-DD', 'English title', 'English one-line description', [lat,lon], category, faction_code, status, source_key, icon_type]`
   - `category`: one of the existing categories already used in ROWS
     (e.g. `control`, `strike`, `politics`) — reuse an existing one, don't invent new ones without checking how `app.src.html` renders categories.
   - `faction_code`: single/double letter control code already used in
     `SNAPS`/`ROWS` (e.g. `H` Houthi, `G` government/Hadi, `S` STC,
     `A` AQAP, `C` coalition — check existing rows for the exact set).
   - `status`: `confirmed` | `reported` | `claimed` | `reference` — be
     honest about source quality; this is shown to readers.
   - `source_key`: a key in `SRC`. If the source isn't already there, add
     it: `key: ['Readable label, outlet, date', 'https://full-url']`.
2. Add the matching Arabic pair to `AR.rows` in `src/ar.js` **at the same
   array index** as the English row in `ROWS`. If you only add English for
   now, insert an empty `["",""]` placeholder at that index so positions
   stay aligned — never skip the index or shift later rows.
3. If a governorate's control changed, add a snapshot to `SNAPS` (see
   existing entries for the shape) and update its Arabic counterpart if
   one exists.
4. Update `LAST_UPDATED` near the top of `data.js` to today's date.
5. From `src/`, run `python3 build.py`.
6. Commit **both** `src/` and the regenerated `site/` and push to `main`.
   Cloudflare Pages auto-deploys `site/` within ~30–60 seconds.

## Sourcing standards (matches the site's published Methodology page)

Primary sources, in this order: official Saudi and coalition statements
(Saudi Press Agency, spa.gov.sa — coalition spokesman, GACA, ministries,
civil defence); Al Arabiya, Asharq, Al Jazeera, Anadolu; ACLED, the Long
War Journal, ISW/Critical Threats; Security Council Report; Wikipedia as an
index to underlying reporting, not as the source itself.

**Attacks on Saudi Arabia (owner's editorial rule, disclosed on the
Methodology page):** a missile, drone or other attack on Saudi territory or
a Saudi vessel goes in only if a Saudi official body has announced it, and
it is worded the way that body worded it (e.g. "the coalition says it
intercepted…"), with `status: confirmed` and the official statement as the
source. If Saudi authorities have not announced it — a Houthi claim, or a
media report that contradicts the official account (e.g. "it hit its
target" when the coalition says it was intercepted) — leave it out
entirely. Don't add the contradicting version as a second sentence either.

Every row must carry a
real, working source URL. Don't fabricate a source or a coordinate — if
unsure of the exact location, use the governorate capital's coordinates
and say so in the description, or mark the row `reported`/`claimed`
instead of `confirmed`.
