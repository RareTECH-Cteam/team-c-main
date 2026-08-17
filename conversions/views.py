from django.shortcuts import render #djangoフレームワークのrender関数を呼び出す
from .forms import ConversionRequestForm, GuestConversionRequestForm 
#conversion/forms.pyからConversionRequestFormとGuestConversionRequestFormを読み込み
from .models import ConversionTarget
from .gemini_service import convert_text

# Create your views here.

def convert_api(request): #/api/convertにアクセスが来たときに呼び出す
    """敬語変換フォームを受け取る処理"""

    #ロック対象の変換タイプを空で初期化
    locked_targets = ConversionTarget.objects.none()

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
        locked_targets = ConversionTarget.objects.filter(is_guest_available=False)

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
            result = convert_text(
                    input_text,
                    target_name,
                    scene_name
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
    