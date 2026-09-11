# 別世界Bar 公式サイト

公開URL: https://kenchin4.github.io/betsusekai_bar/

## 次回の開催日を変えるには

**`events.json` だけを編集して保存（commit）してください。** 他のファイルは触らなくて大丈夫です。

```json
{
  "date": "2027-02-14",
  "announced": "2026-12-01",
  "note": ""
}
```

- `date` … 開催日（必須）
- `announced` … 日程を発表した日。告知タスクが「発表告知」を出す基準になる
- `note` … 一言メモ（ゲスト回など）。RSS・カレンダーの説明文に入る
- 会場・時間・参加費が通常と違う回だけ、その回に `venue` / `doors` / `start` / `end` / `price` を書き足す（省略時は `defaults` の値）
- 過去の開催記録は `archive.html` が本体。`events.json` には次回（と、まだ先の回）だけあれば十分

保存すると GitHub Actions が動き、1〜2分で以下が自動更新されます。

| ファイル | 内容 |
|---|---|
| `index.html` | 告知ページ（日付・カウントダウン・開催要項・JSON-LD） |
| `crew.html` | クルー紹介（「次回」表記） |
| `sitemap.xml` | 検索エンジン向け更新日 |
| `feed.xml` | RSS |
| `bessekai.ics` | カレンダー購読用 |

毎日 0:05（日本時間）にも自動で動き、開催が終わった翌日には「次回の日程 調整中」表示に切り替わります。

## ファイルの役割

| ファイル | 種別 | 説明 |
|---|---|---|
| `events.json` | 手で編集 | 開催日程。ここだけ編集すればよい |
| `site/index.tmpl.html` | 手で編集 | 告知ページの見た目・文面（紙のチラシ／ZINE風デザイン） |
| `site/crew.tmpl.html` | 手で編集 | クルー紹介の見た目・文面 |
| `archive.html` | 手で編集 | 開催記録。Artifact原本から変換して置いている（日付に依存しないので自動生成の対象外） |
| `build.py` | 手で編集 | 生成スクリプト。Python 3.9以上・追加ライブラリ不要 |
| `index.html` `crew.html` `sitemap.xml` `feed.xml` `bessekai.ics` | **自動生成** | 直接編集しても次の生成で消える |
| `og.png` `robots.txt` | 固定 | シェア用画像とクローラ設定 |

## 手元で動かす

```
python3 build.py
```
