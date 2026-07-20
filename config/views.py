"""
config-level views: プロジェクト全体で使う view
- ヘルスチェック (Liveness / Readiness の2種類)
"""
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


# ================================================================
# Liveness Check (/health/)
# ================================================================
@require_GET
@never_cache
def health(request):
    """
    プロセス生存確認 (Liveness Probe)

    用途:
    - ALB Target Group Health Check
    - Docker HEALTHCHECK (Dockerfile)
    - nginx から Django への疎通確認

    設計方針:
    - DB接続チェックは含めない
    - 理由: DB障害で全EC2が unhealthy → ASG が全部作り直し → カスケード障害
    - DB は別途 CloudWatch RDS メトリクスで監視する

    レスポンス:
    - 200 OK: プロセス生存
    - 到達不能なら ALB/Docker が unhealthy 判定
    """
    return JsonResponse({"status": "ok"})


# ================================================================
# Readiness Check (/health/ready/)
# ================================================================
@require_GET
@never_cache
def health_ready(request):
    """
    サービス依存関係を含めた準備完了確認 (Readiness Probe)

    用途:
    - デプロイ後の疎通テスト
    - 障害時の切り分け (「DB が原因か Django が原因か」)

    レスポンス:
    - 200 OK: 全依存関係が健全
    - 503 Service Unavailable: いずれかの依存が失敗
    """
    checks = {"app": "up"}
    overall_ok = True

    # --- DB 接続チェック ---
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["db"] = "up"
    except Exception:
        checks["db"] = "down"
        overall_ok = False
        # ログ側で詳細確認する (structlog / CloudWatch Logs)

    status_code = 200 if overall_ok else 503
    return JsonResponse(
        {"status": "ok" if overall_ok else "degraded", **checks},
        status=status_code,
    )
