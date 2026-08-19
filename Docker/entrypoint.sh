#!/bin/sh
# ================================================================
# Django コンテナ起動時の初期化スクリプト
# DB接続待機 → migrate → (prodのみ)collectstatic → CMD実行
# ================================================================

# スクリプト内のコマンドが1つでも失敗したら、その時点でスクリプトを終了する
set -e

# --- DB 接続待機 ---
# コンテナ起動時、DB がまだ受付可能でないと migrate が失敗する
# 最大30秒待つ
# 本番 = Parameter Store の database_url からホスト/ポートを抽出
# ローカル = 環境変数 DATABASE_URL から抽出

if [ "${ENV}" = "production" ]; then
    echo "[entrypoint] Parameter Store から database_url を取得"
    DB_URL=$(python -c "import boto3, os; print(boto3.client('ssm', region_name=os.environ.get('AWS_REGION', 'ap-northeast-1')).get_parameter(Name='/keigo/dev/database_url', WithDecryption=True)['Parameter']['Value'])" 2>/dev/null) || DB_URL=""
else
    # ローカルは environment の DATABASE_URL を使う
    DB_URL="${DATABASE_URL}"
fi

# postgres://user:pass@HOST:PORT/dbname から HOST と PORT を抽出
DB_HOST=$(echo "${DB_URL}" | sed -E 's|^[^@]+@([^:/]+):([0-9]+)/.*$|\1|') # @ の後ろ、: の前がホスト。: の後ろ、/ の前がポート。
DB_PORT=$(echo "${DB_URL}" | sed -E 's|^[^@]+@([^:/]+):([0-9]+)/.*$|\2|')

# 抽出失敗時のフォールバック（安全側）
DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-5432}"

echo "[entrypoint] ${DB_HOST}:${DB_PORT} のDBに接続開始"

# コンテナ起動時にDBを起動、確認が取れるまで待つ(netcatで接続確認)
i=0
while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
    i=$((i+1))
    if [ $i -ge 30 ]; then
        echo "[entrypoint] DB接続失敗"
        exit 1
    fi
    sleep 1
done
echo "[entrypoint] DB接続確認OK"

# --- Django マイグレーション ---
echo "[entrypoint] マイグレーション開始"
python manage.py migrate --noinput

# --- 複数箇所にある静的ファイルを、1つの配信用ディレクトリに集約する(本番用:prod) ---
if [ "${ENV}" != "local" ]; then
    echo "[entrypoint] 静的ファイルを収集します"
    python manage.py collectstatic --noinput --clear
fi

# --- CMD 実行 ---
echo "[entrypoint] Starting: $*"
exec "$@"
