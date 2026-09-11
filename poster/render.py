#!/usr/bin/env python3
"""events.json から X 用の告知画像（1600×900）を作る。

使い方:
    python3 poster/render.py                      # 次回開催・見出しは自動
    python3 poster/render.py --kicker "今週の土曜です"
    python3 poster/render.py --out /path/bessekai_20261121.png

必要なもの: playwright（chromium）と Pillow。日本語は端末の Noto CJK を使う。
"""
import argparse, sys
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build as B  # noqa: E402  events.json の読み込みロジックを共有する


def pick_next(now=None):
    now = now or datetime.now(B.JST)
    future = [e for e in B.load() if e["end_dt"] > now]
    return future[0] if future else None


def default_kicker(ev, today=None):
    today = today or datetime.now(B.JST).date()
    days = (ev["day"] - today).days
    if days == 0:
        return "本日ひらきます"
    if days == 1:
        return "あすひらきます"
    if days <= 7:
        return "今週ひらきます"
    return "次回の別世界Bar"


def render(ev, kicker, out_path):
    from playwright.sync_api import sync_playwright
    from PIL import Image

    html = (ROOT / "poster/template.html").read_text(encoding="utf-8")
    repl = {
        "KICKER": kicker,
        "YEAR": str(ev["day"].year),
        "MONTH": str(ev["day"].month),
        "DAY": str(ev["day"].day),
        "DOW": ev["dow"],
        "START": ev["start"],
        "DOORS": ev["doors"],
        "VENUE": ev["venue"],
        "VENUE_SUB": f'{ev["venue_area"]}／{ev["venue_access"]}',
        "PRICE": f'{ev["price"]:,}円',
    }
    for k, v in repl.items():
        html = html.replace("{{" + k + "}}", v)
    assert "{{" not in html, "テンプレートに未置換のプレースホルダがあります"

    tmp = Path(out_path).with_suffix(".src.html")
    tmp.write_text(html, encoding="utf-8")
    big = Path(out_path).with_suffix(".2x.png")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=2)
        pg.goto(tmp.resolve().as_uri())
        pg.wait_for_timeout(700)
        pg.screenshot(path=str(big))
        b.close()
    Image.open(big).convert("RGB").resize((1600, 900), Image.LANCZOS).save(out_path, quality=95)
    big.unlink(missing_ok=True)
    tmp.unlink(missing_ok=True)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kicker", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    ev = pick_next()
    if not ev:
        print("次回開催の予定がありません（events.json）")
        return 1
    out = a.out or f'bessekai_{ev["day"].strftime("%Y%m%d")}.png'
    kicker = a.kicker or default_kicker(ev)
    render(ev, kicker, out)
    print(f'{out} | {B.jp(ev)} {ev["start"]}開演 | 見出し: {kicker}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
