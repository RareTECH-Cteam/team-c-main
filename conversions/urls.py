from django.urls import path #djangoフレームワークからpath関数を持ってくる
from . import views #同じ階層のファイルからviews.pyの名前を持つファイルを読み込む

app_name = "conversions" #このURLグループをconversionsって名前にするよ

urlpatterns = [ #このアプリで使うURLパターンを決めようか
    path("convert/",views.convert,name="convert"), # convert/のURLにはviewsファイルのconvert_api関数を実行する

 # よく見たら今はまだ使っていない
    # path("results/<int:pk>/",views.result_detail,name="result-detail"),
    # # results/数字/のURLには数字をpkにぶち込みviewsファイルのresult_detail_api関数を実行する
]