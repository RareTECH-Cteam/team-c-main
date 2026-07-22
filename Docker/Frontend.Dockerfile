# syntax=docker/dockerfile:1

# ================================================================
# 依存パッケージ
# ================================================================
FROM node:24-alpine AS dependencies

WORKDIR /app

# nodeユーザーがnode_modulesやViteキャッシュへ書き込めるようにする
RUN chown node:node /app

USER node

# 依存関係を先にコピーしてDockerキャッシュを利用
COPY --chown=node:node frontend/package.json frontend/package-lock.json ./

RUN --mount=type=cache,target=/home/node/.npm,uid=1000,gid=1000 \
    npm ci


# ================================================================
# ローカル開発環境
# ================================================================
FROM dependencies AS development

COPY --chown=node:node frontend/ ./

EXPOSE 5173

CMD [
    "npm",
    "run",
    "dev",
    "--",
    "--host",
    "0.0.0.0",
    "--port",
    "5173",
    "--strictPort"
]


# ================================================================
# React/Vite ビルド
# ================================================================
FROM dependencies AS build

COPY --chown=node:node frontend/ ./

# VITE_*はブラウザへ公開される値のみ使用する
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build


# ================================================================
# 本番配信環境
# ================================================================
FROM nginx:1.30-alpine AS production

RUN rm -rf /usr/share/nginx/html/* \
    && rm -f /etc/nginx/conf.d/default.conf

COPY Docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# Nodeやnode_modulesは含めず、生成物だけコピー
COPY --from=build --chown=nginx:nginx \
    /app/dist/ /usr/share/nginx/html/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1/nginx-health || exit 1