# VibeMap

若者向けおすすめスポット共有Webアプリケーション

カフェ、ラーメン屋、古着屋、サウナ、夜景スポットなどのお気に入りの場所を写真付きで投稿・共有できるサービスです。

## 技術スタック

- Python 3.11+
- Django 5.2
- SQLite
- Bootstrap 5
- Pillow（画像処理）

## セットアップ手順

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. データベースのマイグレーション

```bash
python manage.py migrate
```

### 3. 初期カテゴリデータの投入

```bash
python seed.py
```

### 4. 管理者ユーザーの作成

```bash
python manage.py createsuperuser
```

### 5. 開発サーバーの起動

```bash
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/ にアクセスしてください。

## 機能一覧

- ユーザー登録 / ログイン / ログアウト
- プロフィール作成・編集（表示名・自己紹介・アイコン画像）
- スポット投稿（タイトル・説明・エリア・住所・カテゴリ・写真）
- 投稿一覧（カード型レイアウト）
- 投稿詳細（画像ギャラリー・コメント）
- いいね機能
- 保存（ブックマーク）機能
- コメント機能
- カテゴリ検索 / エリア検索 / キーワード検索
- マイページ（自分の投稿一覧）
- 保存済みスポット一覧
- Django管理画面（/admin/）

## ディレクトリ構成

```
vibemap/
├── manage.py          # Django管理コマンド
├── requirements.txt   # 依存パッケージ
├── seed.py            # 初期データ投入スクリプト
├── config/            # プロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/          # 認証・プロフィール
│   ├── models.py      # Profile モデル
│   ├── views.py       # 登録・ログイン・マイページ
│   ├── forms.py       # SignUpForm, ProfileForm
│   ├── urls.py
│   └── admin.py
├── spots/             # スポット関連
│   ├── models.py      # Spot, SpotImage, Like, Bookmark, Comment
│   ├── views.py       # 一覧・詳細・作成・検索・いいね・保存
│   ├── forms.py       # SpotForm, CommentForm
│   ├── urls.py
│   └── admin.py
├── templates/         # HTMLテンプレート
│   ├── base.html
│   ├── accounts/
│   └── spots/
├── static/            # 静的ファイル
│   └── css/style.css
└── media/             # アップロード画像（gitignore済み）
```
