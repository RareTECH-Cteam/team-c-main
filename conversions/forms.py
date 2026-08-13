from django import forms # Djangoのフォーム機能の読み込み
from .models import ConversionRequest, ConversionTarget # conversionsアプリのmodels.pyからモデルの読み込み

class BaseConversionRequestForm(forms.ModelForm): # conversionRequestモデルをもとに作成
    """ゲスト・ログインユーザーの共通のフォーム"""

    class Meta:
        # ConversionRequestモデルを使用することを指定
        model = ConversionRequest

        # ゲストとログインユーザーの共通の項目のモデルフィールドを指定
        fields = [
            "input_text",   # 変換したい文章を入力
            "target",       # 変換のタイプの指定
        ]

        # fieldsのウィジェットの指定HTML上での表示方法
        widgets = {
            # input_textを複数行のテキスト入力エリアとして表示
            "input_text": forms.Textarea(
                attrs={
                    # 未入力時に入力欄の中へ表示する案内文
                    "placeholder": "変換したい文章を入力してください",

                    # テキストエリアの初期表示を約6行分の高さにする
                    "rows": 6, 
                }
            ),
            # targetをラジオボタンとして表示
            "target" :  forms.RadioSelect()
        }

# 共通フォームの継承
class GuestConversionRequestForm(BaseConversionRequestForm):
    """ゲスト用変換フォーム"""
    # 親フォームと同じ内容
    def __init__(self, *args, **kwargs):
        # 親クラスの初期化処理を実行
        # input_textとtargetのフォームフィールドを生成する
        super().__init__(*args, **kwargs)

    # ゲスト利用時は可能な変換相手のみ表示
        # ゲストフォームのtargetフィールドが使用するデータを変更する
        self.fields["target"].queryset = (

            # conversionTargetテーブルから条件一致のデータを取得
            ConversionTarget.objects.filter(

                # is_guest_availableがTrueのデータに絞る
                is_guest_available=True
            )
        )

# 共通フォームの継承
class ConversionRequestForm(BaseConversionRequestForm):
    """ログインユーザー用フォーム"""

    # 共通フォームのMetaの情報を引き継ぎ
    class Meta(BaseConversionRequestForm.Meta):

        fields = [
            # 親フォームの中身を引き継ぎ
            *BaseConversionRequestForm.Meta.fields,

            #sceneを追加
            "scene",
        ]

    #共通のwidgetsにsceneの設定を追加
        widgets = {
            # 親の辞書を引き継ぐ
            **BaseConversionRequestForm.Meta.widgets,

            # sceneをラジオボタンで表示
            "scene": forms.RadioSelect(),
        }