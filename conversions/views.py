#from django.shortcuts import render #djangoフレームワークのrender関数を呼び出す(非同期処理のため使わない)
from django.http import JsonResponse #Json形式で返せるためのおまじない
from .forms import ConversionRequestForm, GuestConversionRequestForm 
#conversion/forms.pyからConversionRequestFormとGuestConversionRequestFormを読み込み

# Create your views here.

def convert_api(request): #/api/convertにアクセスが来たときに呼び出す
    """敬語変換フォームを受け取る処理"""

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

    #アクセス方法（以下による）
    #POST・・送信されたデータを渡す
    #GET・・Noneを渡してからのフォームを作成
    form = form_class(request.POST or None)

    #レスポンス
    return JsonResponse({"message": "convert api ok", "is_guest": is_guest,})

def result_detail_api(request,pk): #/api/results/数字/にアクセスが来たとき
    return JsonResponse({"result_id":pk}) #pkに数字を入れてJson形式で返す