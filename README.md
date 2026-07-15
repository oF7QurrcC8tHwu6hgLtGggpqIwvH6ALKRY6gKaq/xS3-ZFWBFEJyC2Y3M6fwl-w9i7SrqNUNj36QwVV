# LootBar 荒野行動マーケット 自動取得パイプライン

毎週自動でLootBarの荒野行動マーケットデータを取得し、Excelを作成して
メールで送信します（GitHub Actions上で無料実行）。

## できること

- 一覧API + 価格トレンドAPIから全商品データを取得（欠落チェック付き）
- 商品名・ジャンルを日本語化（辞書ベース。原文も別列に保持）
- 為替レートを毎回自動取得してUSD→JPY換算
- 実行結果を `data/history/YYYY-MM-DD.csv` として自動蓄積（履歴が残る）
- 前回実行との比較で、平均価格が±15%以上動いた商品を検出
- 最新結果をExcel化し、変動サマリー付きでメール送信

---

## セットアップ手順

### 1. GitHubリポジトリを作成

1. https://github.com にログイン（アカウントが無ければ無料登録）
2. 右上の「+」→「New repository」
3. リポジトリ名を入力（例: `lootbar-scraper`）。Public/Privateどちらでも可（Privateを推奨）
4. 「Create repository」をクリック

### 2. このフォルダの中身をアップロード

作成したリポジトリの画面で「uploading an existing file」から、このフォルダの中身
（`.github/`, `scripts/`, `data/`, `output/`, `requirements.txt`）を
**フォルダ構成を保ったまま**アップロードしてください。

GitHubの画面からのドラッグ＆ドロップではフォルダ構造が保たれないことがあるため、
慣れていれば以下のコマンドでの登録を推奨します（PowerShellで、フォルダの中身がある場所で実行）：

```powershell
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/【あなたのユーザー名】/lootbar-scraper.git
git push -u origin main
```

### 3. メール送信用のSecretsを設定

リポジトリの `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
から、以下の5つを登録してください。

| Secret名 | 値の例 | 備考 |
|---|---|---|
| `SMTP_HOST` | `smtp.gmail.com` | Gmailの場合 |
| `SMTP_PORT` | `587` | |
| `SMTP_USER` | `your_address@gmail.com` | 送信元メールアドレス |
| `SMTP_PASSWORD` | (アプリパスワード16桁) | **通常のログインパスワードは使えません** |
| `MAIL_TO` | `送信先アドレス@example.com` | 受信したいメールアドレス。複数人に送る場合はカンマ区切りで `a@example.com,b@example.com` のように指定可能（BCC相当で配送されるため、受信者同士は互いのアドレスが見えません） |

**Gmailを使う場合の注意（重要）**

Googleアカウントの通常パスワードではSMTP認証が拒否されます。代わりに
「アプリパスワード」を発行してください。

1. Googleアカウントで2段階認証を有効にする（未設定の場合）
2. https://myaccount.google.com/apppasswords にアクセス
3. アプリ名を適当に入力（例: lootbar-scraper）して生成される16桁の文字列を
   `SMTP_PASSWORD` に設定

Gmail以外（Outlook、独自ドメインのメール等）でも、SMTPホスト・ポート・認証情報が
分かれば同様に設定できます。

### 4. 動作確認（手動実行）

1. リポジトリの `Actions` タブを開く
2. 左側の `LootBar Market Scrape` をクリック
3. 右側の `Run workflow` ボタンで手動実行
4. 実行完了後、`data/history/` に本日の日付のCSVができていること、
   受信メールにExcelが添付されていることを確認してください

初回は「前回データ」が無いため、価格変動の通知は出ません（2回目以降から機能します）。

---

## カスタマイズ

### 実行頻度を変える

現在の設定は**毎日20:00(JST)に1回**です。`.github/workflows/scrape.yml` の
以下の部分を編集すれば変更できます（UTC基準です）。

```yaml
schedule:
  - cron: "0 11 * * *"   # 毎日 20:00 JST
```

例:
- 毎週月曜9時(JST): `"0 0 * * 1"`
- 毎月1日9時(JST): `"0 0 1 * *"`

※ LootBarの価格トレンドデータは日次更新のため、1日に2回以上実行しても
　基本的に得られる情報は増えません（サイトへの負荷だけが増えるため非推奨です）。

### 価格変動の通知しきい値を変える

`scripts/pipeline.py` の以下の値を編集してください。

```python
PRICE_CHANGE_ALERT_THRESHOLD = 0.15  # 0.15 = 15%
```

### 商品名の翻訳辞書を追加・修正する

`scripts/translate_dict.py` の `FAMILY_MAP_ORDERED` / `EDITION_MAP_ORDERED` /
`SPECIAL_MAP` に語彙を追加してください。新商品が出ると辞書に無い語彙が
残ることがありますが、その場合は備考欄に「翻訳辞書に未対応語彙あり」と
自動で記録されるので、そこだけ確認して辞書に追記すれば運用上問題ありません。

---

## 注意事項

- 本スクリプトはLootBar非公開APIを利用しています。サイト側の仕様変更で
  動かなくなる可能性があります（その場合はエラーメールは飛ばず、Actionsの
  実行ログにエラーが出ます。`Actions`タブで定期的に成功しているか確認してください）
- サーバー負荷に配慮し、商品ごとに0.5〜1秒の間隔でリクエストしています
- 商品名の日本語訳はLootBar公式のものではなく独自の意訳です
