# syntax=docker/dockerfile:1.7
# ================================================================
# nginx コンテナ(React SPA 配信 + リバースプロキシ + Django静的配信)
# ビルドコマンド (ローカル):
#   docker buildx build --platform linux/arm64 \
#     -f Docker/nginx/Dockerfile -t keigo-nginx:latest --load .
# ================================================================

# ============================================================
# React (Vite) をビルド
# ============================================================
FROM node:24-alpine AS frontend-build

WORKDIR /app

# 依存だけ先にコピーしてキャッシュを効かせる
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# ソースをコピーしてビルド
COPY frontend/ ./

# ブラウザへ公開される API ベースパス
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# /app/dist/ に成果物が出力される
RUN npm run build

# ============================================================
# nginx 本体 (React dist を配信 + リバプロ)
# ============================================================
FROM nginx:1.27-alpine

# デフォルト設定を削除 (自作の default.conf に置き換え)
RUN rm /etc/nginx/conf.d/default.conf

# nginxの設定をコンテナ内にコピー
COPY Docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# React ビルド成果物を nginx の配信ディレクトリへ
COPY --from=frontend-build /app/dist/ /usr/share/nginx/html/

# このコンテナのポート番号
EXPOSE 80
