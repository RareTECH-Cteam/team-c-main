# 環境構築手順書

1. 前提要件

| ツール | 必須バージョン | 確認方法 |
|---|---|---|
| Docker Desktop | 最新 | `docker --version` |
| Docker Compose | **v2 以上** | `docker compose version` |
| Python | 3.12 | `python3 --version` |

Docker Desktop を起動しておくこと。

**docker-Compose v2 必須**: 
ターミナルから docker compose version 入力で v2.x.x を返せば OK。

---

2. 初回セットアップ

### Step 1: リポジトリを clone
```bash
git clone <リポジトリURL> keigo
cd keigo
```

### Step 2: Python 仮想環境と依存 install
```bash
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 2-1: Django プロジェクト初期化
```bash
python manage.py startapp accounts
python manage.py startapp conversions
```

### Step 3: `.env` を作成
```bash
cp .env.example .env
```
`.env` を開き、.env.exampleからコピー

### Step4: React環境構築
```bash
cd frontend
npm ci
npm run dev
```
`npm ci`でpackage-lock.jsonを参照してパッケージをインストールし、環境構築を行います。  
`npm run dev`で自身をホストとするローカルサーバを立てます。  
Dockerを基本的に使用することになると思うのでこちらはあまり気にする必要はないです。  

※npm ciを実行する前にディレクトリ移動を忘れないでください  
※Docker compose up --buildを行う場合には以上のコードを実行する必要はありません。Dockerfile内にDocker上で実行するようにコードを記載してあります。

### Step 5: Docker 起動
```bash
docker compose up -d --build
```

### Step 6: コンテナ状態確認
```bash
docker compose ps
```

**期待される出力**:
```
NAME           STATUS
keigo-nginx    Started 
keigo-api      Healthy 
keigo-db       Healthy 
keigo-frontend Running
```

### Step 7: 動作確認
```bash
# ヘルスチェック
curl http://localhost/health/           # → {"status": "ok"}
curl http://localhost/health/ready/     # → {"status": "ok", "app": "up", "db": "up"}
curl http://localhost/nginx-health      # → ok
```

### Step 8: Django Admin 用の superuser 作成
```bash
docker compose exec api python manage.py createsuperuser
```

対話的にユーザー名 / メール / パスワード入力。

ブラウザで <http://localhost/admin/> を開き、作成したアカウントでログイン → 管理画面が表示されれば完成。

---

## 日常的なコマンド

### 起動 / 停止

```bash
docker compose up -d                     # 起動 (バックグラウンド)
docker compose down                      # 停止
docker compose down -v                   # データも削除 (初期化)
docker compose restart api               # 特定サービスだけ再起動
```

### ログ確認

```bash
docker compose logs -f                   # 全サービス、リアルタイム
docker compose logs -f api               # api だけ
docker compose logs api --tail 100       # 直近100行
```

### コンテナ内での作業

```bash
# シェルに入る
docker compose exec api bash
docker compose exec db bash

# Django 管理コマンド (よく使う)
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py migrate
docker compose exec api python manage.py collectstatic --noinput
docker compose exec api python manage.py createsuperuser
docker compose exec api python manage.py shell

# DB 直接接続
docker compose exec db psql -U keigo_admin -d keigo
```

### コード編集

- `.:/app` で volume mount しているので、**ホストでコード編集 → runserver が自動リロード**
- 依存パッケージ追加時 (`requirements.txt` 変更) は再ビルド必要:

```bash
docker compose up -d --build api
```
---

## 環境リセット (完全に作り直したい時)

```bash
# 1. コンテナ・ボリューム・ネットワーク削除
docker compose down -v

# 2. このプロジェクトのイメージを削除
# --rmi local で compose がビルドしたイメージをまとめて削除
docker compose down --rmi local -v

# 3. 再構築
docker compose up -d --build
```

**注意**: DB データも消えます。開発用データを保持したい場合は事前に dump を取る:
```bash
docker compose exec db pg_dump -U keigo_admin keigo > backup.sql
```
