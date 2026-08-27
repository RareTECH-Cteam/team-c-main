#!/bin/sh
# ================================================================
# Django コンテナ起動時の初期化スクリプト
# DB接続待機 → migrate → collectstatic → CMD実行
# ================================================================

# スクリプト内のコマンドが1つでも失敗したら、その時点でスクリプトを終了する
set -e

# --- DB 接続待機 ---
# コンテナ起動時、DB がまだ受付可能でないと migrate が失敗する
# 最大30秒待つ
#DB_HOST="${DB_HOST:-db}"
#DB_PORT="${DB_PORT:-5432}"

# echo "[entrypoint] ${DB_HOST}:${DB_PORT} のDBに接続開始"
# # コンテナ起動時にDBを起動、確認が取れるまで待つ(netcatで接続確認)
# i=0
# while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
#     i=$((i+1))
#     if [ $i -ge 30 ]; then
#         echo "[entrypoint] DB接続失敗"
#         exit 1
#     fi
#     sleep 1
# done
# echo "[entrypoint] DB接続確認OK"

# --- Django マイグレーション ---
echo "[entrypoint] マイグレーション開始"
python manage.py migrate --noinput

# --- 複数箇所にある静的ファイルを、Nginx配信用ディレクトリに集約する ---
# ローカルでもNginxはSTATIC_ROOTだけを配信するため、環境を問わず毎回収集する。
echo "[entrypoint] 静的ファイルを収集します"
python manage.py collectstatic --noinput --clear

# --- CMD 実行 ---
echo "[entrypoint] Starting: $*"
exec "$@"
