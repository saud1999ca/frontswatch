"""Daily share card: one 1200x630 PNG summarising where things stand today.

Rendered by screenshotting an HTML card with Chromium, because Arabic needs
real text shaping and the card should look like the rest of the site.
If Chromium is not available the HTML is still written and the PNG is skipped,
so a local build never fails over it.
"""
import json
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))

ST_AR = {'confirmed': 'مؤكد', 'reported': 'غير مؤكد',
         'claimed': 'مُدّعى', 'reference': 'خلفية'}
ACTOR = {'H': ('الحوثيون', '#ef6b64'), 'G': ('الحكومة', '#6f93f5'),
         'C': ('التحالف', '#6f93f5'), 'S': ('الانتقالي', '#3fc7b6'),
         'A': ('القاعدة', '#b58be0'), 'U': ('غير محسوم', '#8d99a2'),
         'X': ('متنازع عليها', '#8d99a2')}
# a governorate split between two forces gets the striped treatment the map uses
STRIPE = ('repeating-linear-gradient(45deg,#8d99a2 0 4px,#2a3640 4px 8px)')
MON_AR = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
          'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
def ar_num(n):
    return str(n)          # the site writes Arabic with Western digits


def ar_date(iso):
    y, m, d = (iso.split('-') + ['', ''])[:3]
    out = MON_AR[int(m) - 1] + ' ' + ar_num(int(y))
    return (ar_num(int(d)) + ' ' + out) if d else out


def extract():
    """Pull the data the card needs out of the JS files, using node."""
    script = r"""
const fs=require('fs');
function load(p,map){let t=fs.readFileSync(p,'utf8');for(const[a,b]of map)t=t.replace(a,b);eval(t)}
load(process.argv[1],[['const ROWS=','global.ROWS='],['const SNAPS=','global.SNAPS='],
                      ['const SRC=','global.SRC='],['const LAST_UPDATED=','global.LAST_UPDATED=']]);
load(process.argv[2],[['const AR=','global.AR=']]);
load(process.argv[3],[['const GOV=','global.GOV='],['const ROADS=','global.ROADS='],['const DIST=','global.DIST=']]);
const ids=GOV.features.map(f=>f.properties.id);
const ctrl={};ids.forEach(k=>ctrl[k]='G');
SNAPS.forEach(s=>Object.assign(ctrl,s.set));
process.stdout.write(JSON.stringify({
  rows:ROWS, ar:(AR&&AR.rows)||[], updated:LAST_UPDATED, control:ctrl
}));
"""
    out = subprocess.run(
        ['node', '-e', script,
         os.path.join(BASE, 'data.js'),
         os.path.join(BASE, 'ar.js'),
         os.path.join(BASE, 'geo.js')],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


CARD = """<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700&family=Noto+Sans+Arabic:wght@400;500;600;700&display=swap">
<style>
*{{box-sizing:border-box;margin:0}}
body{{width:1200px;height:630px;overflow:hidden;background:#0c1216;color:#e7edf0;
  font-family:'Noto Sans Arabic',sans-serif;display:flex;flex-direction:column;
  padding:46px 54px 40px;gap:0}}
.top{{display:flex;align-items:center;justify-content:space-between}}
.brand{{display:flex;align-items:center;gap:14px}}
.brand svg{{width:62px;height:43px}}
.brand .nm{{font-size:40px;font-weight:700;letter-spacing:-.01em;line-height:1}}
.brand .tag{{font-size:16px;color:#93a1aa;margin-top:5px}}
.date{{text-align:left;direction:rtl}}
.date .d{{font-size:27px;font-weight:600;line-height:1.2}}
.date .l{{font-size:15px;color:#93a1aa;margin-top:3px}}

.ctrl{{margin-top:30px}}
.ctrl h2{{font-size:15px;color:#93a1aa;font-weight:600;margin-bottom:9px}}
.bar{{display:flex;height:17px;border-radius:999px;overflow:hidden;gap:2px}}
.bar i{{display:block}}
.keys{{display:flex;gap:22px;margin-top:11px;flex-wrap:wrap}}
.key{{display:flex;align-items:center;gap:7px;font-size:17px;color:#cdd7dd}}
.key b{{font-weight:700;color:#e7edf0}}
.key .sw{{width:12px;height:12px;border-radius:3px;display:block}}

.evs{{margin-top:28px;flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;gap:11px}}
.evs h2{{font-size:15px;color:#93a1aa;font-weight:600;margin-bottom:2px}}
.ev{{flex:none;display:flex;align-items:baseline;gap:13px;background:#161e24;border:1px solid #2a3640;
  border-radius:11px;padding:13px 17px}}
.ev .t{{font-size:21px;font-weight:600;line-height:1.35;flex:1;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.ev .b{{font-size:13px;padding:3px 11px;border-radius:999px;border:1px solid;white-space:nowrap}}
.ev .dt{{font-size:14px;color:#93a1aa;white-space:nowrap;font-variant-numeric:tabular-nums}}

.foot{{flex:none;display:flex;align-items:center;justify-content:space-between;
  border-top:1px solid #2a3640;padding-top:16px;margin-top:4px}}
.foot .u{{font-family:'Archivo',sans-serif;font-size:23px;font-weight:700;letter-spacing:-.01em;direction:ltr}}
.foot .c{{font-size:16px;color:#93a1aa}}
</style></head><body>
  <div class="top">
    <div class="brand">
      <svg viewBox="0 0 64 44" aria-hidden="true">
        <path d="M4 22C14 8 24 3 32 3s18 5 28 19" fill="none" stroke="#ef6b64" stroke-width="4.5" stroke-linecap="round"/>
        <path d="M4 22c10 14 20 19 28 19s18-5 28-19" fill="none" stroke="#6f93f5" stroke-width="4.5" stroke-linecap="round"/>
        <circle cx="32" cy="22" r="8.5" fill="#e7edf0"/><circle cx="32" cy="22" r="2.8" fill="#0c1216"/>
      </svg>
      <div><div class="nm">راصد</div><div class="tag">متابعة يومية لحرب اليمن</div></div>
    </div>
    <div class="date"><div class="d">{date}</div><div class="l">{updated_label}</div></div>
  </div>

  <div class="ctrl">
    <h2>السيطرة على المحافظات</h2>
    <div class="bar">{bars}</div>
    <div class="keys">{keys}</div>
  </div>

  <div class="evs">
    <h2>{ev_heading}</h2>
    {events}
  </div>

  <div class="foot">
    <div class="u">frontswatch.com</div>
    <div class="c">{total} حدثًا، كل واحد بمصدره</div>
  </div>
</body></html>
"""


def build(out_site_dir):
    d = extract()
    rows, ar, control = d['rows'], d['ar'], d['control']

    # who holds how many governorates right now
    counts = {}
    for code in control.values():
        key = code if len(code or '') == 1 else 'X'   # two letters = split between forces
        counts[key] = counts.get(key, 0) + 1
    order = [k for k in ('H', 'G', 'S', 'A', 'U', 'X') if counts.get(k)]

    def fill(k):
        return STRIPE if k == 'X' else ACTOR[k][1]

    bars = ''.join(
        f'<i style="flex:{counts[k]};background:{fill(k)}"></i>' for k in order)
    keys = ''.join(
        f'<span class="key"><i class="sw" style="background:{fill(k)}"></i>'
        f'{ACTOR[k][0]} <b>{ar_num(counts[k])}</b></span>' for k in order)

    # the newest events, by date
    idx = sorted(range(len(rows)), key=lambda i: (rows[i][0], i), reverse=True)[:4]
    cards = []
    for i in idx:
        r = rows[i]
        title = (ar[i][0] if i < len(ar) and ar[i] and ar[i][0] else r[1])
        colour = ACTOR.get(r[5], ACTOR['U'])[1]
        cards.append(
            f'<div class="ev"><span class="b" style="color:{colour};border-color:{colour}">'
            f'{ST_AR.get(r[6], r[6])}</span>'
            f'<span class="t">{esc(title)}</span>'
            f'<span class="dt">{ar_date(r[0])}</span></div>')

    html = CARD.format(
        date=ar_date(d['updated']),
        updated_label='آخر تحديث',
        bars=bars, keys=keys,
        ev_heading='أحدث ما رُصد',
        events='\n    '.join(cards),
        total=ar_num(len(rows)),
    )

    card_dir = os.path.join(out_site_dir, 'card')
    os.makedirs(card_dir, exist_ok=True)
    html_path = os.path.join(card_dir, 'index.html')
    with open(html_path, 'w') as f:
        f.write(html)

    png_path = os.path.join(out_site_dir, 'daily.png')
    if shoot(html_path, png_path):
        print('gen_card: wrote daily.png + /card/')
        return True
    print('gen_card: wrote /card/ (no browser available, daily.png not refreshed)')
    return False


def shoot(html_path, png_path):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    exe = '/opt/pw-browsers/chromium'
    try:
        with sync_playwright() as pw:
            kw = {'executable_path': exe} if os.path.exists(exe) else {}
            b = pw.chromium.launch(**kw)
            pg = b.new_page(viewport={'width': 1200, 'height': 630},
                            device_scale_factor=1)
            pg.goto('file://' + html_path)
            try:
                pg.wait_for_function(
                    '() => document.fonts.ready.then('
                    '  () => document.fonts.check(\'700 40px "Noto Sans Arabic"\'))',
                    timeout=20000)
            except Exception:
                print('gen_card: the web font did not load; '
                      'the card falls back to a system Arabic face')
            pg.wait_for_timeout(250)
            pg.screenshot(path=png_path)
            b.close()
        return True
    except Exception as e:                      # a missing browser must not break the build
        print('gen_card: screenshot skipped (%s)' % e)
        return False
