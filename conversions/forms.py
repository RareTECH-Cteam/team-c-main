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
            "scene",        #sceneを追加
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

                    # 最大入力文字数を500文字に設定
                    "maxlength": 500,
                }
            ),
            # targetをラジオボタンとして表示
            "target": forms.RadioSelect(),
            # sceneをラジオボタンで表示
            "scene": forms.RadioSelect(),
        }

        error_messages = {
            "input_text": {
            "required": "変換する文章を入力してください。",
            },
        }

        def clean_input_text(self):
            input_text = self.cleaned_data["input_text"].strip()

            if len(input_text) > 500:
                raise forms.ValidationError(
                    "変換する文章は500文字以内で入力してください。"
                )

            return input_text

# 共通フォームの継承
# ゲストには利用可能なtargetだけを選択肢として表示
class GuestConversionRequestForm(BaseConversionRequestForm):
    """ゲストユーザー用フォーム"""
# 親フォームと同じ内容
    def __init__(self, *args, **kwargs):    #ゲストフォームのインスタンス作成時に実行される初期化メソッド
    #self・・作成しているフォーム自身　*args・・順番で判断する位置引数をまとめて受け取る　**kwargs・・名前で判断する引数をまとめて受け取り
    
        super().__init__(*args, **kwargs) #親フォームの初期化とModelFormの処理の実行

    #ゲスト利用時は可能な変換相手のみ表示
        self.fields["target"].queryset = (   #self.fields・・現在のフォームにあるフィールドをまとめた辞書　self.fields["target"]・・辞書の中からtargetを取り出す　.queryset・・targetの選択肢として使用するDBデータ
            ConversionTarget.objects.filter( #conversionTargetテーブルから条件一致のデータを取得
                is_guest_available=True #is_guest_availableがTrueのデータに絞る
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
        ]

        widgets = {
            # 親の辞書を引き継ぐ
            **BaseConversionRequestForm.Meta.widgets,
        }