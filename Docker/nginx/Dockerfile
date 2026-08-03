# syntax=docker/dockerfile:1.7
# ================================================================
# nginx コンテナ(React SPA 配信 + リバースプロキシ + Django静的配信)
# ビルドコマンド (ローカル):
#   docker buildx build --platform linux/arm64 \
#     -f Docker/nginx/Dockerfile -t keigo-nginx:latest --load .
# ================================================================

# ============================================================
# nginx 本体 (React dist を配信 + リバプロ)
# ============================================================
FROM nginx:1.27-alpine

# デフォルト設定を削除 (自作の default.conf に置き換え)
RUN rm /etc/nginx/conf.d/default.conf

# nginxの設定をコンテナ内にコピー
COPY Docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# このコンテナのポート番号
EXPOSE 80
