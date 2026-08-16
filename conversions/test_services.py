# 実際のAPI通信をしなくても確認できるtest.py

from django.core.exceptions import ImproperlyConfigured # Djangoの設定内容不備エラー用
from django.test import SimpleTestCase, override_settings # テスト用機能を作るためのもの
from unittest.mock import Mock,patch # 「モック」という偽物のGeminiクライアント
from google.genai import errors

from conversions.services.gemini_service import ( # 自分らで作ったサービス
    GeminiServiceError,
    build_conversion_prompt,
    convert_text,
    create_gemini_client,
)


class BuildConversionPromptTests(SimpleTestCase):
    """Geminiへ送るプロンプト生成のテスト"""

    def test_build_prompt_with_scene(self):
        """場面指定ありのプロンプトを生成できる"""

        prompt = build_conversion_prompt(
            input_text="明日までに確認してください",
            target_name="上司向け",
            scene_name="依頼",
        )

        self.assertIn("明日までに確認してください", prompt)
        self.assertIn("上司向け", prompt)
        self.assertIn("依頼", prompt)

    def test_build_prompt_without_scene(self):
        """場面指定なしのプロンプトを生成できる"""

        prompt = build_conversion_prompt(
            input_text="明日までに確認してください",
            target_name="上司向け",
        )

        self.assertIn("場面：指定なし", prompt)


class CreateGeminiClientTests(SimpleTestCase):
    """Geminiクライアント生成のテスト"""

    @override_settings(GEMINI_API_KEY="") # このテスト中だけ、APIキーを空にする
    def test_raise_error_when_api_key_is_empty(self):
        """APIキーが空の場合は設定エラーになる"""

        with self.assertRaises(ImproperlyConfigured): # 囲んだ処理で、このエラーが発生すればテスト成功
            create_gemini_client()


class ConvertTextTests(SimpleTestCase):
    """敬語変換実行処理のテスト"""

    # convert_text()が使うcreate_gemini_client()を、テスト中だけ偽物に差し替える
    @patch(
        "conversions.services.gemini_service.create_gemini_client"
    )
    def test_raise_error_when_response_is_empty(
    self,
    mock_create_client,
):
        """Geminiの応答が空の場合は変換エラーになる"""

        mock_client = mock_create_client.return_value
        mock_response = mock_client.models.generate_content.return_value
        mock_response.text = " \n"

        with self.assertRaises(GeminiServiceError):
            convert_text(
                input_text="確認してください",
                target_name="上司向け",
                scene_name="依頼",
            )

    # convert_text()が使うcreate_gemini_client()を、テスト中だけ偽物に差し替える
    @patch(
        "conversions.services.gemini_service.create_gemini_client"
    )
    def test_return_converted_text(self, mock_create_client):
        """Geminiの応答から変換結果を返せる"""

        mock_client = mock_create_client.return_value
        mock_response = mock_client.models.generate_content.return_value
        mock_response.text = "  ご確認をお願いいたします。\n"

        result = convert_text(
            input_text="確認してください",
            target_name="上司向け",
            scene_name="依頼",
        )

        self.assertEqual(result, "ご確認をお願いいたします。")


    @patch(
    "conversions.services.gemini_service.create_gemini_client"
    )
    def test_raise_service_error_when_gemini_api_fails(
        self,
        mock_create_client,
    ):
        """Gemini APIのエラーをサービス用例外へ変換できる"""

        mock_client = mock_create_client.return_value

        mock_api_response = Mock()
        mock_api_response.body_segments = [
            {
                "error": {
                    "message": "テスト用APIエラー",
                    "status": "INTERNAL",
                }
            }
        ]
        mock_api_response.text = "テスト用APIエラー"

        api_error = errors.ServerError(
            500,
            mock_api_response,
        )

        mock_client.models.generate_content.side_effect = api_error # 偽物のgenerate_content()が呼ばれたら、値を返さずにこのエラーを発生させる

        with self.assertRaises(GeminiServiceError):
            convert_text(
                input_text="確認してください",
                target_name="上司向け",
                scene_name="依頼",
            )