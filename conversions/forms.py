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
            "target" :  forms.RadioSelect(),
            # sceneをラジオボタンで表示
            "scene": forms.RadioSelect(),
        }

    def clean_input_text(self):
        """入力文章の検証"""

        # Djangoによる基本チェックの後入力値を取得
        input_text = self.cleaned_data["input_text"]

        # 文頭・文末の余計な空白を削除
        input_text = input_text.strip()

        if not input_text:
            raise forms.ValidationError(
                "変換する文章を入力してください。"
            )

        if len(input_text) > 500: 
            raise forms.ValidationError(
                "変換する文章は500文字以内で入力してください。"
            )

        # チェック後の値をフォームへ返す
        return input_text

# 共通フォームの継承
#   ゲスト用のtarget全部表示してバリデーションで使用不可にしたコードタイプ
class GuestConversionRequestForm(BaseConversionRequestForm):
    """ゲストユーザー用フォーム"""

    # 共通フォームのMetaの情報を引き継ぎ
    class Meta(BaseConversionRequestForm.Meta):

        fields = [
            # 親フォームの中身を引き継ぎ
            *BaseConversionRequestForm.Meta.fields,
        ]

    #共通のwidgetsにsceneの設定を追加
        widgets = {
            # 親の辞書を引き継ぐ
            **BaseConversionRequestForm.Meta.widgets,
        }

    def clean_target(self):
        """targetの選択の検証"""

        target = self.cleaned_data["target"]

        if not target.is_guest_available:

            raise forms.ValidationError("ゲストではこの機能は使用できません。")
        
        return target
    
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