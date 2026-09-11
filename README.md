# 別世界Bar 公式サイト

公開URL: https://kenchin4.github.io/betsusekai_bar/

## 次回の開催日を変えるには

**`events.json` だけを編集して保存（commit）してください。** それ以外のファイルは触らなくて大丈夫です。

```json
{
  "date": "2026-11-21",
  "announced": "2026-09-05",
  "note": ""
}
```

- `date` … 開催日（必須）
- `announced` … 日程を発表した日。告知タスクが「発表告知」を出す基準になる
- `note` … 一言メモ（ゲスト回など）。RSS・カレンダーの説明文に入る
- 会場・時間・参加費が通常と違う回だけ、`venue` / `doors` / `start` / `end` / `price` を追加する（省略時は `defaults` の値）

保存すると GitHub Actions が動き、1〜2分で以下が自動更新されます。

| ファイル | 内容 |
|---|---|
| `index.html` | 告知ページ（カウントダウン・開催情報・JSON-LD） |
| `crew.html` | クルー紹介（「次回」表記） |
| `sitemap.xml` | 検索エンジン向け更新日 |
| `feed.xml` | RSS |
| `bessekai.ics` | カレンダー購読用 |

毎日 0:05（日本時間）にも自動で動き、開催が終わった翌日には「次回準備中」表示に切り替わります。

## 手元で動かす

```
python3 build.py
```

Python 3.9 以上・追加ライブラリ不要。生成物は上の表の5ファイル。

## 触ってはいけないファイル

`index.html` / `crew.html` / `sitemap.xml` / `feed.xml` / `bessekai.ics` は自動生成なので、直接編集しても次の生成で消えます。
文面やデザインを変えたいときは `site/index.tmpl.html` / `site/crew.tmpl.html` を編集してください。
