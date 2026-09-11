#!/usr/bin/env python3
"""events.json から公開ページ・RSS・iCal を生成する。標準ライブラリのみ。

使い方:  python3 build.py            (リポジトリのルートで実行)
入力:    events.json, site/index.tmpl.html, site/crew.tmpl.html
出力:    index.html, crew.html, sitemap.xml, feed.xml, bessekai.ics
※ archive.html は日付に依存しないので、このスクリプトでは生成しない。
"""
import json, subprocess
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "https://kenchin4.github.io/betsusekai_bar/"
JST = timezone(timedelta(hours=9))
DOW = "月火水木金土日"


def load():
    data = json.loads((ROOT / "events.json").read_text(encoding="utf-8"))
    d = data.get("defaults", {})
    evs = []
    for e in data["events"]:
        ev = dict(d)
        ev.update({k: v for k, v in e.items() if v not in (None, "")})
        day = date.fromisoformat(ev["date"])

        def at(hm):
            h, m = map(int, hm.split(":"))
            return datetime(day.year, day.month, day.day, h, m, tzinfo=JST)

        ev["day"] = day
        ev["doors_dt"], ev["start_dt"], ev["end_dt"] = at(ev["doors"]), at(ev["start"]), at(ev["end"])
        ev["dow"] = DOW[day.weekday()]
        ev["announced_day"] = date.fromisoformat(ev["announced"]) if ev.get("announced") else None
        evs.append(ev)
    evs.sort(key=lambda e: e["day"])
    return evs


def jp(ev):
    return f"{ev['day'].year}年{ev['day'].month}月{ev['day'].day}日（{ev['dow']}）"


def price(ev):
    return f"{ev['price']:,}円"


def iso(dt):
    return dt.isoformat()


def git_date(*paths):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *paths],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        return date.fromisoformat(out) if out else None
    except Exception:
        return None


def build(now=None):
    now = now or datetime.now(JST)
    today = now.date()
    evs = load()
    future = [e for e in evs if e["end_dt"] > now]
    nxt = future[0] if future else None
    past = [e for e in evs if e["end_dt"] <= now]

    # ---------- index.html ----------
    t = (ROOT / "site/index.tmpl.html").read_text(encoding="utf-8")
    if nxt:
        jsonld = json.dumps({
            "@context": "https://schema.org", "@type": "Event", "name": "別世界Bar",
            "description": "珍スポット・団地・廃墟——各ジャンルのマニアがマニアックなプレゼンをする、大阪・四貫島PORTのトークイベント。",
            "startDate": iso(nxt["start_dt"]), "endDate": iso(nxt["end_dt"]), "doorTime": iso(nxt["doors_dt"]),
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "url": BASE, "image": [BASE + "og.png"],
            "location": {"@type": "Place", "name": nxt["venue"],
                         "address": {"@type": "PostalAddress", "addressLocality": nxt["venue_area"],
                                     "addressRegion": "大阪府", "addressCountry": "JP"}},
            "offers": {"@type": "Offer", "price": str(nxt["price"]), "priceCurrency": "JPY",
                       "availability": "https://schema.org/InStock", "url": BASE,
                       "validFrom": iso(datetime.combine(nxt["announced_day"] or today, datetime.min.time(), JST))},
            "organizer": {"@type": "Organization", "name": "別世界Bar", "url": BASE},
        }, ensure_ascii=False, indent=2)
        jsonld = '<script type="application/ld+json">\n' + jsonld + '\n</script>\n'
        hero = (f'      <h1 class="date">\n'
                f'        <span class="year">{nxt["day"].year}年</span>\n'
                f'        {nxt["day"].month}<small>月</small>{nxt["day"].day}<small>日</small>'
                f'<span class="dow">{nxt["dow"]}</span>\n'
                f'      </h1>\n'
                f'      <p class="when"><span>{nxt["start"]} 開演</span><span>{nxt["doors"]} 開場</span>'
                f'<span>{nxt["venue"]}（{nxt["venue_short_area"]}）</span></p>')
        spec_dt = (f'<b>{jp(nxt)}{nxt["start"]} 開演</b>'
                   f'<small>{nxt["doors"]} 開場。終了は{nxt["end"]}ごろ。</small>')
        spec_price = f'{price(nxt)}（＋1ドリンク）<small>当日受付でお支払いください。</small>'
        stamp_price = f'{price(nxt)}＋1ドリンク'
        venue, venue_addr = nxt["venue"], nxt["venue_addr"]
        crew_next = (f'次回 {jp(nxt)}{nxt["start"]} 開演'
                     f'<small>{nxt["doors"]} 開場／{nxt["venue"]}／{price(nxt)}＋1ドリンク</small>')
        js = {"DOORS_OPEN": iso(nxt["doors_dt"]), "SHOW_START": iso(nxt["start_dt"]), "SHOW_END": iso(nxt["end_dt"])}
    else:
        d = json.loads((ROOT / "events.json").read_text(encoding="utf-8")).get("defaults", {})
        jsonld = ""
        hero = ('      <h1 class="date tbd"><span class="year">次回の日程</span>調整中</h1>\n'
                f'      <p class="when"><span>{d["venue"]}（{d["venue_short_area"]}）</span></p>')
        spec_dt = '<b>次回の日程は調整中です</b><small>決まり次第このページでお知らせします。</small>'
        spec_price = f'{d["price"]:,}円（＋1ドリンク）<small>当日受付でお支払いください。</small>'
        stamp_price = f'{d["price"]:,}円＋1ドリンク'
        venue, venue_addr = d["venue"], d["venue_addr"]
        crew_next = '次回 日程調整中<small>決まり次第おしらせします</small>'
        js = {"DOORS_OPEN": "", "SHOW_START": "", "SHOW_END": ""}

    t = (t.replace("{{JSONLD}}", jsonld)
          .replace("{{HERO}}", hero)
          .replace("{{SPEC_DATETIME}}", spec_dt)
          .replace("{{SPEC_VENUE}}", f'{venue}<small>{venue_addr}</small>')
          .replace("{{SPEC_PRICE}}", spec_price)
          .replace("{{STAMP_PRICE}}", stamp_price))
    for k, v in js.items():
        t = t.replace("{{" + k + "}}", v)
    assert "{{" not in t, "index: 未置換のプレースホルダがあります"
    (ROOT / "index.html").write_text(t, encoding="utf-8")

    # ---------- crew.html ----------
    c = (ROOT / "site/crew.tmpl.html").read_text(encoding="utf-8").replace("{{CREW_NEXT}}", crew_next)
    assert "{{" not in c, "crew: 未置換のプレースホルダがあります"
    (ROOT / "crew.html").write_text(c, encoding="utf-8")

    # ---------- sitemap.xml ----------
    src_date = git_date("events.json", "site", "build.py") or today
    flip = max([e["end_dt"].date() for e in past], default=src_date)
    lastmod = max(src_date, min(flip, today))
    archive_mod = git_date("archive.html") or today
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, freq, pri in [(BASE, lastmod, "weekly", "1.0"),
                                (BASE + "crew.html", lastmod, "monthly", "0.8"),
                                (BASE + "archive.html", archive_mod, "monthly", "0.8")]:
        sm += ["  <url>", f"    <loc>{loc}</loc>", f"    <lastmod>{mod}</lastmod>",
               f"    <changefreq>{freq}</changefreq>", f"    <priority>{pri}</priority>", "  </url>"]
    sm.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

    # ---------- feed.xml (RSS 2.0) ----------
    def rfc822(dt):
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0900")

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    items = []
    for e in sorted(evs, key=lambda e: e["day"], reverse=True):
        pub = datetime.combine(e["announced_day"] or e["day"], datetime.min.time(), JST)
        title = f"別世界Bar 次回は{jp(e)}{e['start']}開演・{e['venue']}"
        desc = (f"{jp(e)} {e['doors']}開場／{e['start']}開演、{e['venue']}（{e['venue_area']}・{e['venue_access']}）、"
                f"参加費{price(e)}（＋1ドリンク）。予約不要・途中入退場OK。")
        if e.get("note"):
            desc += " " + e["note"]
        items.append(f"""    <item>
      <title>{esc(title)}</title>
      <link>{BASE}</link>
      <guid isPermaLink="false">betsusekai-bar-{e['day']}</guid>
      <pubDate>{rfc822(pub)}</pubDate>
      <description>{esc(desc)}</description>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>別世界Bar 開催情報</title>
    <link>{BASE}</link>
    <atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>
    <description>珍スポット×団地×廃墟のトークイベント「別世界Bar」（大阪・四貫島PORT）の次回開催情報</description>
    <language>ja</language>
    <lastBuildDate>{rfc822(datetime.combine(lastmod, datetime.min.time(), JST))}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")

    # ---------- bessekai.ics ----------
    def ics_dt(dt):
        return dt.strftime("%Y%m%dT%H%M%S")

    def ics_esc(s):
        return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//betsusekai bar//events//JA", "CALSCALE:GREGORIAN",
             "METHOD:PUBLISH", "X-WR-CALNAME:別世界Bar", "X-WR-TIMEZONE:Asia/Tokyo",
             "REFRESH-INTERVAL;VALUE=DURATION:P1D",
             "BEGIN:VTIMEZONE", "TZID:Asia/Tokyo", "BEGIN:STANDARD", "DTSTART:19700101T000000",
             "TZOFFSETFROM:+0900", "TZOFFSETTO:+0900", "TZNAME:JST", "END:STANDARD", "END:VTIMEZONE"]
    for e in evs:
        stamp = datetime.combine(e["announced_day"] or e["day"], datetime.min.time(), JST).astimezone(timezone.utc)
        desc = (f"{e['doors']}開場／{e['start']}開演。参加費{price(e)}（＋1ドリンク）・予約不要・途中入退場OK。"
                f"\n{e['venue_access']}\n{BASE}")
        if e.get("note"):
            desc = e["note"] + "\n" + desc
        lines += ["BEGIN:VEVENT", f"UID:betsusekai-bar-{e['day']}@kenchin4.github.io",
                  f"DTSTAMP:{stamp.strftime('%Y%m%dT%H%M%SZ')}",
                  f"DTSTART;TZID=Asia/Tokyo:{ics_dt(e['doors_dt'])}",
                  f"DTEND;TZID=Asia/Tokyo:{ics_dt(e['end_dt'])}",
                  "SUMMARY:別世界Bar", f"LOCATION:{ics_esc(e['venue'] + '（' + e['venue_area'] + '）')}",
                  f"DESCRIPTION:{ics_esc(desc)}", f"URL:{BASE}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    (ROOT / "bessekai.ics").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")

    print("next:", jp(nxt) if nxt else "(未定)", "| events:", len(evs), "| lastmod:", lastmod)
    return nxt


if __name__ == "__main__":
    build()
