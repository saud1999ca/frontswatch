"""
Generate one static, SEO-focused page per event (site/event/<slug>/index.html)
plus an index page listing all of them (site/events/index.html), from the
same ROWS/SRC in data.js and AR.rows in ar.js that power the main map.

Called from build.py after the main site is built. If Node isn't available,
this prints a warning and does nothing rather than failing the whole build.
"""
import os, re, json, subprocess, datetime, html

BASE = os.path.dirname(os.path.abspath(__file__))
D = 'https://frontswatch.com'

ACT = {'H': ('Houthis', 'الحوثيون'), 'G': ('Government', 'الحكومة'),
       'C': ('Saudi-led coalition', 'التحالف بقيادة السعودية'),
       'S': ('STC', 'المجلس الانتقالي الجنوبي'), 'A': ('AQAP', 'القاعدة في جزيرة العرب'),
       'U': ('Unclear', 'غير معروف')}
CAT = {'control': ('Control change', 'تغيّر السيطرة'), 'politics': ('Political development', 'تطور سياسي'),
       'strike': ('Strike or attack', 'ضربة أو هجوم'), 'clash': ('Ground fighting', 'قتال بري'),
       'humanitarian': ('Humanitarian', 'إنساني')}
STATUS = {'confirmed': ('Confirmed', 'مؤكد'), 'reported': ('Reported', 'غير مؤكد'),
          'claimed': ('Claimed', 'ادعاء'), 'reference': ('Background', 'خلفية')}


def extract():
    """Run data.js and ar.js through Node and pull out ROWS/SRC/AR.rows as JSON."""
    script = r"""
const fs=require('fs');
function load(path, map){
  let t=fs.readFileSync(path,'utf8');
  for(const [from,to] of map) t=t.replace(from,to);
  eval(t);
}
load(process.argv[1], [['const ROWS=','global.ROWS='],['const SNAPS=','global.SNAPS='],['const SRC=','global.SRC='],['const LAST_UPDATED=','global.LAST_UPDATED=']]);
load(process.argv[2], [['const AR=','global.AR=']]);
process.stdout.write(JSON.stringify({rows:ROWS,src:SRC,ar_rows:(AR&&AR.rows)||[]}));
"""
    out = subprocess.run(['node', '-e', script, os.path.join(BASE, 'data.js'), os.path.join(BASE, 'ar.js')],
                          capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def slugify(date, title):
    s = re.sub(r"[^a-z0-9]+", '-', title.lower()).strip('-')
    s = re.sub(r"-{2,}", '-', s)
    return f"{date}-{s}"[:80].rstrip('-')


PAGE_CSS = """
:root{--bg:#edf0f1;--panel:#fafbfb;--ink:#14202b;--muted:#566570;--line:#cbd4d9;--h:#d23f3a;--g:#3b66d4;--s:#1b9a8c;--a:#7d4bb0;--u:#6c7781}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0c1216;--panel:#161e24;--ink:#e7edf0;--muted:#93a1aa;--line:#2a3640;--h:#ef6b64;--g:#6f93f5;--s:#3fc7b6;--a:#b58be0;--u:#8d99a2}}
:root[data-theme="dark"]{--bg:#0c1216;--panel:#161e24;--ink:#e7edf0;--muted:#93a1aa;--line:#2a3640;--h:#ef6b64;--g:#6f93f5;--s:#3fc7b6;--a:#b58be0;--u:#8d99a2}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:'Archivo','Noto Sans Arabic',system-ui,-apple-system,'Segoe UI',sans-serif;font-size:15px;line-height:1.6;margin:0;padding:0}
.wrap{max-width:640px;margin:0 auto;padding:28px 18px 60px}
a{color:var(--g)}
.top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:22px}
.brand{display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px;text-decoration:none;color:var(--ink)}
.brand svg{width:28px;height:19px}
.langbtn{border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:999px;padding:6px 14px;font:inherit;font-size:13px;cursor:pointer}
.badge{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:3px 10px;font-size:12px;color:var(--muted);margin:0 6px 6px 0}
.dot{width:8px;height:8px;border-radius:50%}
h1{font-size:22px;line-height:1.3;margin:10px 0 6px}
.date{font-family:'JetBrains Mono','Noto Sans Arabic',ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.desc{margin:16px 0;font-size:16px}
.src{border:1px solid var(--line);background:var(--panel);border-radius:8px;padding:12px 14px;margin:18px 0;font-size:13px}
.cta{display:inline-block;margin:18px 0;border-radius:999px;background:var(--g);color:#fff;padding:10px 20px;text-decoration:none;font-weight:600;font-size:14px}
footer{margin-top:34px;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}
:root[data-theme="dark"] .cta, :root:not([data-theme="light"]) .cta{color:#0c1216}
"""

LANG_SCRIPT = """function L(){var ar=document.documentElement.lang!=='ar';document.documentElement.lang=ar?'ar':'en';document.querySelectorAll('[lang-en]').forEach(function(e){e.style.display=ar?'none':'block'});document.querySelectorAll('[lang-ar]').forEach(function(e){e.style.display=ar?'block':'none'})}"""

HTML_TMPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_en} — {date} | Frontswatch</title>
<meta name="description" content="{desc_en_attr}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="article">
<meta property="og:title" content="{title_en} — Frontswatch">
<meta property="og:description" content="{desc_en_attr}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{D}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0c1216">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"NewsArticle","headline":{title_en_json},"datePublished":"{date}","description":{desc_en_json},"url":"{url}",{source_json}"publisher":{{"@type":"Organization","name":"Frontswatch"}}}}</script>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="brand" href="/"><svg viewBox="0 0 64 44"><path d="M4 22C14 8 24 3 32 3s18 5 28 19" fill="none" stroke="var(--h)" stroke-width="4.5" stroke-linecap="round"/><path d="M4 22c10 14 20 19 28 19s18-5 28-19" fill="none" stroke="var(--g)" stroke-width="4.5" stroke-linecap="round"/><circle cx="32" cy="22" r="8.5" fill="var(--ink)"/><circle cx="32" cy="22" r="2.8" fill="var(--panel)"/></svg>Frontswatch · راصد</a>
    <button class="langbtn" onclick="L()">{lang_label}</button>
  </div>

  <div lang-en>
    <div class="date">{date}</div>
    <div>{badges_en}</div>
    <h1>{title_en_html}</h1>
    <p class="desc">{desc_en_html}</p>
  </div>
  <div lang-ar dir="rtl" style="display:none">
    <div class="date">{date}</div>
    <div>{badges_ar}</div>
    <h1>{title_ar_html}</h1>
    <p class="desc">{desc_ar_html}</p>
  </div>

  {src_block}

  <a class="cta" href="/">{cta_label}</a>

  <footer>
    <span lang-en>Part of <a href="/">Frontswatch</a>, a daily-updated map and timeline of the war in Yemen. See <a href="/events/">all events</a>.</span>
    <span lang-ar dir="rtl" style="display:none">جزء من <a href="/">راصد</a>، خريطة وخط زمني يتحدث يوميًا لحرب اليمن. شاهد <a href="/events/">جميع الأحداث</a>.</span>
  </footer>
</div>
<script>{lang_script}</script>
</body>
</html>
"""


def esc(s):
    return html.escape(s or '', quote=True)


def badge_row(cat_en, cat_ar, fac_en, fac_ar, st_en, st_ar, is_ar):
    cat = cat_ar if is_ar else cat_en
    fac = fac_ar if is_ar else fac_en
    st = st_ar if is_ar else st_en
    return f'<span class="badge">{esc(cat)}</span><span class="badge">{esc(fac)}</span><span class="badge">{esc(st)}</span>'


def build(out_site_dir):
    try:
        data = extract()
    except Exception as e:
        print('gen_events: skipped (could not read data via node):', e)
        return []

    rows, src, ar_rows = data['rows'], data['src'], data['ar_rows']
    events_dir = os.path.join(out_site_dir, 'event')
    os.makedirs(events_dir, exist_ok=True)

    seen_slugs = {}
    urls = []
    listing_items = []

    for idx, row in enumerate(rows):
        date, title_en, desc_en = row[0], row[1], row[2]
        category = row[4] if len(row) > 4 else ''
        faction = row[5] if len(row) > 5 else ''
        status = row[6] if len(row) > 6 else ''
        source_key = row[7] if len(row) > 7 else None

        ar_pair = ar_rows[idx] if idx < len(ar_rows) else None
        title_ar = (ar_pair[0] if ar_pair and len(ar_pair) > 0 else '') or title_en
        desc_ar = (ar_pair[1] if ar_pair and len(ar_pair) > 1 else '') or desc_en

        slug = slugify(date, title_en)
        n = seen_slugs.get(slug, 0) + 1
        seen_slugs[slug] = n
        if n > 1:
            slug = f"{slug}-{n}"

        url = f"{D}/event/{slug}/"
        cat_en, cat_ar = CAT.get(category, (category, category))
        fac_en, fac_ar = ACT.get(faction, (faction, faction))
        st_en, st_ar = STATUS.get(status, (status, status))

        src_block = ''
        source_json = ''
        if source_key and source_key in src:
            label, src_url = src[source_key]
            src_block = (f'<div class="src"><span lang-en>Source: <a href="{esc(src_url)}" rel="nofollow noopener" target="_blank">{esc(label)}</a></span>'
                         f'<span lang-ar dir="rtl" style="display:none">المصدر: <a href="{esc(src_url)}" rel="nofollow noopener" target="_blank">{esc(label)}</a></span></div>')
            source_json = f'"isBasedOn":{json.dumps(src_url)},'

        page = HTML_TMPL.format(
            title_en=esc(title_en), date=date, desc_en_attr=esc(desc_en), url=url, D=D,
            title_en_json=json.dumps(title_en), desc_en_json=json.dumps(desc_en), source_json=source_json,
            css=PAGE_CSS, lang_script=LANG_SCRIPT, lang_label='العربية', cta_label='<span lang-en>View on the live map</span><span lang-ar dir="rtl" style="display:none">شاهد على الخريطة الحية</span>',
            badges_en=badge_row(cat_en, cat_ar, fac_en, fac_ar, st_en, st_ar, False),
            badges_ar=badge_row(cat_en, cat_ar, fac_en, fac_ar, st_en, st_ar, True),
            title_en_html=esc(title_en), desc_en_html=esc(desc_en),
            title_ar_html=esc(title_ar), desc_ar_html=esc(desc_ar),
            src_block=src_block,
        )
        page_dir = os.path.join(events_dir, slug)
        os.makedirs(page_dir, exist_ok=True)
        with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(page)

        urls.append(url)
        listing_items.append((date, title_en, title_ar, slug))

    # Listing page, newest first
    listing_items.sort(key=lambda x: x[0], reverse=True)
    rows_html_en = '\n'.join(
        f'<li><a href="/event/{s}/"><span class="date">{d}</span> — {esc(t)}</a></li>' for d, t, _, s in listing_items)
    rows_html_ar = '\n'.join(
        f'<li><a href="/event/{s}/"><span class="date">{d}</span> — {esc(ta)}</a></li>' for d, _, ta, s in listing_items)
    listing = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All events | Frontswatch</title>
<meta name="description" content="Every event in Frontswatch's timeline of the war in Yemen, 2014 to today, each with its own page and sources.">
<link rel="canonical" href="{D}/events/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#0c1216">
<style>{PAGE_CSS}
ul{{list-style:none;padding:0;margin:18px 0}}
li{{padding:9px 0;border-bottom:1px solid var(--line)}}
li a{{text-decoration:none;color:var(--ink)}}
li .date{{color:var(--muted);margin-inline-end:6px}}
</style>
</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="brand" href="/"><svg viewBox="0 0 64 44"><path d="M4 22C14 8 24 3 32 3s18 5 28 19" fill="none" stroke="var(--h)" stroke-width="4.5" stroke-linecap="round"/><path d="M4 22c10 14 20 19 28 19s18-5 28-19" fill="none" stroke="var(--g)" stroke-width="4.5" stroke-linecap="round"/><circle cx="32" cy="22" r="8.5" fill="var(--ink)"/><circle cx="32" cy="22" r="2.8" fill="var(--panel)"/></svg>Frontswatch · راصد</a>
    <button class="langbtn" onclick="L()">العربية</button>
  </div>
  <div lang-en><h1>All events</h1><p class="desc">Every event on the Frontswatch map, newest first.</p><ul>{rows_html_en}</ul></div>
  <div lang-ar dir="rtl" style="display:none"><h1>جميع الأحداث</h1><p class="desc">كل حدث على خريطة راصد، الأحدث أولًا.</p><ul>{rows_html_ar}</ul></div>
  <a class="cta" href="/"><span lang-en>Back to the map</span><span lang-ar dir="rtl" style="display:none">عودة للخريطة</span></a>
</div>
<script>{LANG_SCRIPT}</script>
</body>
</html>
"""
    os.makedirs(os.path.join(out_site_dir, 'events'), exist_ok=True)
    with open(os.path.join(out_site_dir, 'events', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(listing)

    print(f'gen_events: wrote {len(urls)} event pages + 1 listing page')
    return urls + [f'{D}/events/']
