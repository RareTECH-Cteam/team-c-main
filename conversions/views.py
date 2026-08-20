from django.db import transaction
from django.shortcuts import render # djangoフレームワークのrender関数を呼び出す
from .forms import ConversionRequestForm, GuestConversionRequestForm
#conversion/forms.pyからConversionRequestFormとGuestConversionRequestFormを読み込み
from .models import ConversionTarget, ConversionResult
from .services.gemini_service import (
    GeminiServiceError,
    convert_text,
)

# Create your views here.

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

    #変数の定義
    result = None
    input_text = None

    #フォームが送信された場合
    if request.method == "POST":
        #ユーザーの入力した送信データをフォームへ渡す（POSTの処理）
        form = form_class(request.POST)

        #forms.pyに定義されたルールで入力内容を検証
        if form.is_valid():

            #バリデーションを通過したデータの取得
            input_text = form.cleaned_data["input_text"] #バリデーション通過した入力文章の取得
            target = form.cleaned_data["target"] #バリデーションを通過した選択された変換対象を取得
            scene = form.cleaned_data["scene"] #選択されたsceneを取得

            #Geminiへ渡す文字列に変換
            target_name = target.name           #models.pyでの定義より選択されたtargetの名前を文字列としてtarget_nameに持たせている
            scene_name = scene.name if scene else None   #models.pyの定義より選択されたsceneを持たせNoneも許容するようにしている

            #Geminiでの変換後の値を受け取っている
            try:
                result = convert_text(
                    input_text,
                    target_name,
                    scene_name
                )
            except GeminiServiceError:
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
                            conversion_request=conversion_request,
                            output_text=result,
                        )


    else:
        #GETの処理
        form = form_class()

    #returnでHTMLに埋め込んでブラウザに返すための辞書型の指定
    context = {
        "input_text": input_text,
        "output_text": result,
        "form": form,
        "is_guest": is_guest,
        "locked_targets": locked_targets
    }

    #レスポンス
    return render(request, "conversions/conversion.html", context) #contextをHTMLに埋め込みブラウザに返している

# def result_detail(request, pk):
#     """指定された変換結果を表示する処理"""

#     #URLから受け取ったpkに一致する変換結果を取得
#     result = get_object_or_404(ConversionResult, pk=pk)

#     #ConversionResultに紐づいている変換リクエストを取得
#     conversion_request = result.conversion_request
#     context = {
#         "input_text": conversion_request.input_text,
#         "output_text": result.output_text,
#         "target": conversion_request.target,
#         "scene": conversion_request.scene,
#     }

#     return render(
#         request,
#         "conversions/conversion-result.html",
#         context
#     )