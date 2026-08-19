"""
Django settings for Keigo project.

【このファイルの位置付け】
インフラ担当が用意した「Django が Docker 環境で正常起動するための最小構成。
バックエンド担当が以下を追加:
- INSTALLED_APPS に記載
- REST_FRAMEWORK 設定
- Cognito 認証クラス
- 業務ロジック用の定数

【インフラで設定した内容】
- .env / docker-compose の environment から下記の変数を読み込める:
    DJANGO_SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, LOG_LEVEL, ENV
- collectstatic の出力先は /app/staticfiles (nginx が :readOnly で参照)
- ALB → nginx → Django の間で X-Forwarded-Proto ヘッダを解釈
- DATABASE_URL 経由で PostgreSQL / MySQL どちらでも接続できる
"""
from pathlib import Path

import environ
import os
import boto3
import urllib.request

# ================================================================
# パス
# BASE_DIR = manage.py がある階層 (リポジトリルート)
#   settings.py の位置: <BASE_DIR>/config/settings.py
#   → .parent で config/、もう一段 .parent で BASE_DIR
# ================================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ================================================================
# 環境変数読み込み (django-environ)
# .env はローカル開発のみ、本番 (EC2) では environment 経由
# ================================================================
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    LOG_LEVEL=(str, "INFO"),
)

env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)


# ================================================================
# 必須設定
#   ローカル : .env / environment から読む
#   本番     : ENV=production のとき Parameter Store から取得
# ================================================================
if os.environ.get("ENV", "local") == "production":
    ssm = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))
    resp = ssm.get_parameters_by_path(Path="/keigo/dev/", WithDecryption=True)
    _params = {p["Name"].split("/")[-1]: p["Value"] for p in resp["Parameters"]}

    SECRET_KEY = _params["django_secret_key"]
    DATABASES = {"default": env.db_url_config(_params["database_url"])}
    GEMINI_API_KEY = _params["gemini_api_key"]
    DEBUG = False

    ALLOWED_HOSTS = [
        "kotobadi.com",
        "www.kotobadi.com",
        "localhost",     # Docker HEALTHCHECK 用
        "127.0.0.1",
    ]

    # --- ALB ヘルスチェック用: EC2 自身のプライベート IP を IMDSv2(インスタンスメタデータ) で取得して追加 ---
    # ALB は Host ヘッダに EC2 のプライベート IP を入れて /health/ を叩くため、EC2 が入れ替わると IP が変わるので、起動時に動的取得する。

    def _get_ec2_private_ip():
        try:
            # IMDSv2: トークンを取得
            token_req = urllib.request.Request(
                "http://169.254.169.254/latest/api/token",
                method="PUT",
                headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
            )
            token = urllib.request.urlopen(token_req, timeout=1).read().decode()

            # トークンを付けてプライベート IP を取得 (GET)
            ip_req = urllib.request.Request(
                "http://169.254.169.254/latest/meta-data/local-ipv4",
                headers={"X-aws-ec2-metadata-token": token},
            )
            return urllib.request.urlopen(ip_req, timeout=1).read().decode()
        except Exception:
            # ローカルや取得失敗時は None（ALLOWED_HOSTS に追加しない）
            return None

    _private_ip = _get_ec2_private_ip()
    if _private_ip:
        ALLOWED_HOSTS.append(_private_ip)
else:
    # ローカル開発用(envから取得)
    SECRET_KEY = env("DJANGO_SECRET_KEY")
    DATABASES = {"default": env.db_url("DATABASE_URL")}
    GEMINI_API_KEY = env("GEMINI_API_KEY")
    DEBUG = env("DEBUG")
    ALLOWED_HOSTS = env("ALLOWED_HOSTS")


# ================================================================
# アプリケーション定義
# ================================================================
# Djangoが管理するアプリ一覧(Django起動時に有効化)
INSTALLED_APPS = [
    "django.contrib.admin", #管理画面
    "django.contrib.auth", #ユーザー認証
    "django.contrib.contenttypes", #モデル種類管理
    "django.contrib.sessions", #セッション管理
    "django.contrib.messages", #一時メッセージ
    "django.contrib.staticfiles", #CSS/JSなど静的ファイル管理
    # ↓ バックエンドで追加
    # "rest_framework", Rest APIを作るため
    # "corsheaders", Reactなど別ドメインなどからAPIを呼ぶためのもの
    # "django_filters", # APIの検索絞り込み機能
    # "drf_spectacular", # 作成したAPIの仕様書やブラウザ上で試せるSwagger UIを自動生成
    # ↓自作アプリ
    "accounts", # ログイン、新規登録、ユーザー情報の管理するアプリ
    "conversions", # 敬語変換に関する処理やデータの管理するアプリ
]

AUTH_USER_MODEL = "accounts.User" # 標準Userではなく作成したUserモデルを使用する

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", #セキュリティ関連のHTTPヘッダー設定
    "django.contrib.sessions.middleware.SessionMiddleware", #セッション管理
    "django.middleware.common.CommonMiddleware", #共通的なHTTP処理
    "django.middleware.csrf.CsrfViewMiddleware", #CSRF攻撃対策
    "django.contrib.auth.middleware.AuthenticationMiddleware", #ログインユーザー情報の追加用
    "django.contrib.messages.middleware.MessageMiddleware", #一時メッセージ機能
    "django.middleware.clickjacking.XFrameOptionsMiddleware", #クリックジャッキング対策
]

# DjangoのURLルーティング定義の場所
ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates", #Django標準のテンプレートエンジン
        "DIRS": [BASE_DIR / "templates"], #共通テンプレートの場所
        "APP_DIRS": True, #各Djangoアプリ内のtemplatesフォルダも探す
        # テンプレートへ自動的に渡す情報の指定
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

#WSGIサーバーがDjangoアプリを起動するときの標準インターフェース
WSGI_APPLICATION = "config.wsgi.application"


# ================================================================
# パスワードバリデーター (Django 標準)
# ================================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ================================================================
# 国際化 / 地域化 (日本語アプリ)
# ================================================================
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True


# ================================================================
# 静的ファイル
# nginx が /app/staticfiles を read-only volume で配信するため、
# collectstatic の出力先を固定
# ================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# ================================================================
# デフォルト主キー型
# ================================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ================================================================
# ALB / リバースプロキシ対応
# nginx が X-Forwarded-Proto ヘッダを付けるので Django に伝える
# → HTTPS 判定が正しく行われる (secure cookies, HSTS 等)
# ================================================================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ================================================================
# ログ出力設定
# ================================================================
LOGGING = {
    "version": 1, #dictConfig形式
    "disable_existing_loggers": False, #既存のログ設定を無効化しない
    # ログの表示形式
    "formatters": {
        "simple": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    # ログの出力先
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    # 基本設定
    "root": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL"),
    },
}
