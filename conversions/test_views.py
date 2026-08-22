# viewsの自動テスト
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from .services.gemini_service import GeminiServiceError

from .models import (
    ConversionRequest,
    ConversionResult,
    ConversionTarget,
)


class ConvertViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Viewテストで共通して使用するデータを作成"""
        cls.guest_target = ConversionTarget.objects.create(
            name="テスト用ゲスト変換",
            code="test-guest-target",
            is_guest_available=True,
        )

        cls.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test-password",
            name="テストユーザー",
        )
 # test1: ゲスト変換時はDBに保存しない
    @patch(
        "conversions.views.render",
        return_value=HttpResponse(status=200),
    )
    @patch(
        "conversions.views.convert_text",
        return_value="承知いたしました。",
    )
    def test_guest_conversion_does_not_save_history(
        self,
        mock_convert_text,
        mock_render,
    ):
        """ゲストの変換内容がDBへ保存されないことを確認"""
        response = self.client.post(
            reverse("conversions:convert"),
            data={
                "input_text": "わかりました。",
                "target": self.guest_target.pk,
                "scene": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        # Viewがrenderへ渡したcontextを取得
        context = mock_render.call_args.args[2]

        self.assertEqual(
            context["output_text"],
            "承知いたしました。",
        )

        # ゲストの変換履歴は保存されない
        self.assertEqual(
            ConversionRequest.objects.count(),
            0,
        )
        self.assertEqual(
            ConversionResult.objects.count(),
            0,
        )

        # Gemini用サービスが正しい引数で1回呼ばれた
        mock_convert_text.assert_called_once_with(
            "わかりました。",
            self.guest_target.name,
            None,
        )
 # test2: ログインで変換すると履歴がDBに残る
    @patch(
        "conversions.views.render",
        return_value=HttpResponse(status=200),
    )
    @patch(
        "conversions.views.convert_text",
        return_value="承知いたしました。",
    )
    def test_authenticated_conversion_saves_history(
        self,
        mock_convert_text,
        mock_render,
    ):
        """ログインユーザーの変換履歴がDBへ保存されることを確認"""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("conversions:convert"),
            data={
                "input_text": "わかりました。",
                "target": self.guest_target.pk,
                "scene": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConversionRequest.objects.count(), 1)
        self.assertEqual(ConversionResult.objects.count(), 1)

        conversion_request = ConversionRequest.objects.get()
        conversion_result = ConversionResult.objects.get()

        self.assertEqual(
            conversion_request.user,
            self.user,
        )
        self.assertEqual(
            conversion_request.input_text,
            "わかりました。",
        )
        self.assertEqual(
            conversion_request.target,
            self.guest_target,
        )
        self.assertIsNone(conversion_request.scene)

        self.assertEqual(
            conversion_result.conversion_request,
            conversion_request,
        )
        self.assertEqual(
            conversion_result.output_text,
            "承知いたしました。",
        )

        mock_convert_text.assert_called_once_with(
            "わかりました。",
            self.guest_target.name,
            None,
        )
 # test3: Gemini失敗時はエラー表示してDB保存しない
    @patch(
        "conversions.views.render",
        return_value=HttpResponse(status=200),
    )
    @patch(
        "conversions.views.convert_text",
        side_effect=GeminiServiceError(
            "Gemini APIとの通信に失敗しました。"
        ),
    )
    def test_gemini_error_does_not_save_history(
        self,
        mock_convert_text,
        mock_render,
    ):
        """Gemini失敗時に不完全な履歴を保存しないことを確認"""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("conversions:convert"),
            data={
                "input_text": "わかりました。",
                "target": self.guest_target.pk,
                "scene": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConversionRequest.objects.count(), 0)
        self.assertEqual(ConversionResult.objects.count(), 0)

        context = mock_render.call_args.args[2]

        self.assertIsNone(context["output_text"])
        self.assertIn(
            "変換処理に失敗しました。時間をおいて再度お試しください。",
            context["form"].non_field_errors(),
        )

        mock_convert_text.assert_called_once_with(
            "わかりました。",
            self.guest_target.name,
            None,
        )
 # test4: 入力エラーはGeminiすら呼ばない
    @patch(
        "conversions.views.render",
        return_value=HttpResponse(status=200),
    )
    @patch("conversions.views.convert_text")
    def test_invalid_input_does_not_call_gemini_or_save(
        self,
        mock_convert_text,
        mock_render,
    ):
        """入力不備時にGeminiを呼ばず履歴も保存しないことを確認"""
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("conversions:convert"),
            data={
                "input_text": "",
                "target": self.guest_target.pk,
                "scene": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        mock_convert_text.assert_not_called()

        self.assertEqual(ConversionRequest.objects.count(), 0)
        self.assertEqual(ConversionResult.objects.count(), 0)

        context = mock_render.call_args.args[2]

        self.assertIn(
            "変換する文章を入力してください。",
            context["form"].errors["input_text"],
        )
 # test5: トランザクション処理が働いてRequestだけを残さない
    @patch(
        "conversions.views.ConversionResult.objects.create",
        side_effect=RuntimeError("結果の保存に失敗しました。"),
    )
    @patch(
        "conversions.views.convert_text",
        return_value="承知いたしました。",
    )
    def test_result_save_failure_rolls_back_request(
        self,
        mock_convert_text,
        mock_result_create,
    ):
        """Result保存失敗時にRequestもロールバックされることを確認"""
        self.client.force_login(self.user)

        with self.assertRaises(RuntimeError):
            self.client.post(
                reverse("conversions:convert"),
                data={
                    "input_text": "わかりました。",
                    "target": self.guest_target.pk,
                    "scene": "",
                },
            )

        self.assertEqual(ConversionRequest.objects.count(), 0)
        self.assertEqual(ConversionResult.objects.count(), 0)

        mock_convert_text.assert_called_once_with(
            "わかりました。",
            self.guest_target.name,
            None,
        )
        mock_result_create.assert_called_once()
# 5件目のテストはわざとエラーを出すよ
# [docker compose exec api python manage.py test conversions.test_views]を実行すると「RuntimeError: 結果の保存に失敗しました。」って出るよ
# でも、最後の方で「OK」が出てるはずだよ！　出てるならテストは成功だよ