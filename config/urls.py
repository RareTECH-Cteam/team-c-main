"""
プロジェクト全体のURL設定

参考: https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

from .views import health, health_ready


urlpatterns = [
    # --- 管理画面 ---
    path("admin/", admin.site.urls),

    # --- ヘルスチェック ---
    # ALB / Docker HEALTHCHECK 用 (シンプル、DB 依存なし)
    path("health/", health, name="health"),
    # 依存関係含めた確認用
    path("health/ready/", health_ready, name="health-ready"),

    # --- API ルーティング ---
    # API はすべて "api/" 配下に実装すること (nginx が /api/ を Django にプロキシするため)
    # include を有効化する前に、対応する urls.py を作成すること(未作成のまま include すると ModuleNotFoundError で起動失敗する)
    path("api/",include("conversions.urls")), # apiから始まるURLをconversionsに任せるよ！
]
