# ============================================================
# 環境構築: builder
# ============================================================
FROM python:3.12-slim AS builder

# 起動時のデフォルト設定
# 不要な.pycを作らない, ログを即出力, pipキャッシュ削除, pip確認通信を停止
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# セキュリティパッチを最新化
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# ============================================================
# 実行環境: runtime
# ============================================================
FROM python:3.12-slim AS runtime

# 起動時のデフォルト設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings

# Debianのパッケージ更新 / netcatを追加 / インストール用キャッシュを削除
# netcat: DB 接続待機のための通信テストツール
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Djangoをroot権限で動かさない、一般ユーザーでアプリを動かす(セキュリティ)
RUN groupadd --system --gid 1000 appgroup && \
    useradd --system --uid 1000 --gid appgroup --no-create-home appuser

# HOME を明示 (boto3 が ~/.aws/credentials を探す時のパス基点)
ENV HOME=/home/appuser

WORKDIR /app

# builderから仮想環境をコピー
COPY --from=builder /opt/venv /opt/venv

# アプリコード全体をコピー
COPY --chown=appuser:appgroup . .

# entrypoint.sh に実行権限付与
RUN chmod +x /app/Docker/entrypoint.sh

# Djangoが使うフォルダを作成し、appuserが書き込めるようにする
RUN mkdir -p /app/staticfiles && \
    chown -R appuser:appgroup /app/staticfiles

# ここから以下はappuserで実行する
USER appuser

# このコンテナのポート番号
EXPOSE 8000

# コンテナヘルスチェック (DjangoへのHTTP確認)
# Django URL: /health/
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request, sys; \
        sys.exit(0) if urllib.request.urlopen('http://localhost:8000/health/').status == 200 else sys.exit(1)" \
    || exit 1

ENTRYPOINT ["sh", "/app/Docker/entrypoint.sh"]
CMD ["gunicorn", "config.asgi:application", "--config", "/app/Docker/gunicorn.conf.py"]
