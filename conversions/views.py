import json # JSONリクエストをpythonの辞書に変換

from django.db import transaction
from django.http import JsonResponse # JavaScriptへJsonを返す
from django.shortcuts import render # djangoフレームワークのrender関数を呼び出す
from django.template.loader import render_to_string # テンプレートをHTML文字列へ変換
from django.utils import timezone

from .forms import ConversionRequestForm, GuestConversionRequestForm
#conversion/forms.pyからConversionRequestFormとGuestConversionRequestFormを読み込み
from .models import ConversionTarget, ConversionResult, GuestSession
from .services.gemini_service import (
    GeminiServiceError,
    convert_text,
)

# Create your views here.

def _json_error(code, message, status):
    """変換APIのエラーレスポンスを作成する"""
    return JsonResponse(
        {
            "ok": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
        status=status,
    )


def _first_form_error(form):
    """フォームから最初のエラーメッセージを取得する"""
    for errors in form.errors.values():
        if errors:
            return str(errors[0])

    return "入力内容を確認してください。"


def convert(request): #/api/convertにアクセスが来たときに呼び出す
    """敬語変換フォームを受け取る処理"""

    #ロック対象の変換タイプを空で初期化
    locked_targets = ConversionTarget.objects.none().values(
        "name",
        "code",
        "is_guest_available"
    )

    #ログインしているかで使用するフォームを分ける

    #ログイン済みかゲストかの判断
    if request.user.is_authenticated:

        #ConversionRequestFormに変更
        form_class = ConversionRequestForm

        #is_guestがFalseの時
        is_guest = False
    else:
        #GuestConversionRequestFormに変更
        form_class = GuestConversionRequestForm

        #is_guestがTrueの時
        is_guest = True
        #ゲストが利用できない変換対象のみ取得
        locked_targets = ConversionTarget.objects.filter(
            is_guest_available=False
        ).values(
            "name",
            "code",
            "is_guest_available"
        )
        guest_session_id = request.session.get("guest_session_id")
        if guest_session_id:
            guest_session = GuestSession.objects.get(id=guest_session_id)

        else:
            guest_session = GuestSession.objects.create()
            request.session["guest_session_id"] = guest_session.id

    #変数の定義
    converted_text = None
    input_text = None
    reason = None
    guest_limit_exceeded = None

    if request.method == "POST":
        # JSON送信か通常フォーム送信かを判定
        is_json_request = request.content_type == "application/json"

        if is_json_request:
            try:
                payload = json.loads(request.body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return _json_error(
                    "INVALID_JSON",
                    "送信内容を読み取れませんでした。",
                    400,
                )

            if not isinstance(payload, dict):
                return _json_error(
                    "INVALID_JSON",
                    "送信内容を読み取れませんでした。",
                    400,
                )
        else:
            # 既存テスト・通常フォーム送信との互換用
            payload = request.POST

        # 受け取ったデータをフォームへ渡す
        form = form_class(payload)

        #forms.pyに定義されたルールで入力内容を検証
        if not form.is_valid():

            if is_json_request:
                target_id = payload.get("target")

                # 存在するがゲスト利用不可の変換タイプ
                if is_guest:
                    try:
                        is_locked_target = ConversionTarget.objects.filter(
                            pk=target_id,
                            is_guest_available=False,
                        ).exists()
                    except (TypeError, ValueError):
                        is_locked_target = False

                    if is_locked_target:
                        return _json_error(
                            "AUTH_REQUIRED",
                            "この変換タイプを利用するにはログインが必要です。",
                            403,
                        )

                return _json_error(
                    "VALIDATION_ERROR",
                    _first_form_error(form),
                    400,
                )
        else:
            # バリデーションを通過したデータの取得
            input_text = form.cleaned_data["input_text"]
            target = form.cleaned_data["target"] #バリデーションを通過した選択された変換対象を取得
            scene = form.cleaned_data["scene"] #選択されたsceneを取得

            #Geminiへ渡す文字列に変換
            target_name = target.name           #models.pyでの定義より選択されたtargetの名前を文字列としてtarget_nameに持たせている
            scene_name = scene.name if scene else None   #models.pyの定義より選択されたsceneを持たせNoneも許容するようにしている

            if is_guest:
                if guest_session.count_date != timezone.localdate():
                    guest_session.count_date = timezone.localdate()
                    guest_session.conversion_count = 0
                    guest_session.save()

                if guest_session.conversion_count >= 3:
                    return _json_error(
                        "GUEST_LIMIT_EXCEEDED",
                        "Cチーム赤字確定やーこれ以上はやめてくれーーーー",
                        429,
                    )

            #Geminiでの変換後の値を受け取っている
            try:
                conversion_result = convert_text(
                    input_text,
                    target_name,
                    scene_name
                )

                converted_text = conversion_result["converted_text"]
                reason = conversion_result["reason"]

            except GeminiServiceError:
                if is_json_request:
                    return _json_error( # Jsonの場合のエラー
                        "CONVERSION_FAILED",
                        "変換処理に失敗しました。時間をおいて再度お試しください。",
                        502,
                    )

                form.add_error(
                    None,
                    "変換処理に失敗しました。時間をおいて再度お試しください。",
                )

            else:
                if request.user.is_authenticated: # ゲストの場合はifへ入らないため、Gemini変換と画面表示だけ行い、DB件数は増えない。
                    with transaction.atomic():
                        conversion_request = form.save(commit=False) # DB保存せずConversionRequestを作成
                        conversion_request.user = request.user # ログイン中のユーザーを紐づけ
                        conversion_request.save() # ConversionRequestをDB保存

                        ConversionResult.objects.create( # 変換結果を保存
                            conversion_request=conversion_request, # view内の変数名
                            output_text=converted_text, # DBフィールド名
                        )
                else:
                    guest_session.conversion_count += 1
                    guest_session.save()

                if is_json_request: # ゲスト・ログインユーザー共通で画面へ結果を返す
                    result_html = render_to_string(
                        "conversions/_conversion_result.html",
                        {
                            "input_text": input_text,
                            "converted_text": converted_text,
                            "reason": reason,
                            "target_label": target_name,
                            "scene_label": scene_name,
                        },
                        request=request,
                    )

                    return JsonResponse(
                        {
                            "ok": True,
                            "view": {
                                "name": "result",
                                "title": "変換結果 | コトバディ",
                                "html": result_html,
                            },
                        }
                    )


    else:
        #GETの処理
        form = form_class()

    #returnでHTMLに埋め込んでブラウザに返すための辞書型の指定
    context = {
        "input_text": input_text,
        "output_text": converted_text,
        "reason": reason,
        "form": form,
        "is_guest": is_guest,
        "locked_targets": locked_targets,
        "guest_limit_exceeded": guest_limit_exceeded,
    }

    #レスポンス
    return render(request, "conversions/conversion.html", context) #contextをHTMLに埋め込みブラウザに返している