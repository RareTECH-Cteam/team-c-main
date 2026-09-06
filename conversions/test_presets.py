import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import (
    ConversionPreset,
    ConversionScene,
    ConversionTarget,
)


class ConversionPresetViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """プリセットテストで共通して使用するデータを作成"""
        cls.user = get_user_model().objects.create_user(
            email="preset@example.com",
            password="test-password",
            name="プリセットユーザー",
        )

        cls.other_user = get_user_model().objects.create_user(
            email="other@example.com",
            password="test-password",
            name="別ユーザー",
        )

        cls.target = ConversionTarget.objects.create(
            name="プリセット用変換タイプ",
            code="preset-target",
            is_guest_available=True,
        )

        cls.scene = ConversionScene.objects.create(
            name="プリセット用場面",
            code="preset-scene",
        )

    def setUp(self):
        """各テスト開始時にログインする"""
        self.client.force_login(self.user)

    def _payload(self, name="上司への確認"):
        """登録リクエストで使用するJSONデータを作成"""
        return {
            "name": name,
            "input_text": "進捗をご確認ください。",
            "target": self.target.pk,
            "scene": self.scene.pk,
        }

    def test_unauthenticated_user_cannot_get_presets(self):
        """未ログインユーザーはプリセット一覧を取得できない"""
        self.client.logout()

        response = self.client.get(
            reverse("conversions:preset-list-create")
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"]["code"],
            "AUTH_REQUIRED",
        )

    def test_authenticated_user_can_create_preset(self):
        """ログインユーザーがプリセットを登録できる"""
        response = self.client.post(
            reverse("conversions:preset-list-create"),
            data=json.dumps(self._payload()),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ConversionPreset.objects.count(), 1)

        preset = ConversionPreset.objects.get()

        self.assertEqual(preset.user, self.user)
        self.assertEqual(preset.name, "上司への確認")
        self.assertEqual(
            preset.input_text,
            "進捗をご確認ください。",
        )
        self.assertEqual(preset.target, self.target)
        self.assertEqual(preset.scene, self.scene)

        response_data = response.json()
        self.assertTrue(response_data["ok"])
        self.assertEqual(
            response_data["preset"]["id"],
            preset.pk,
        )

    def test_list_returns_only_logged_in_users_presets(self):
        """一覧にはログインユーザー本人のプリセットだけを返す"""
        own_preset = ConversionPreset.objects.create(
            user=self.user,
            name="自分のプリセット",
            input_text="確認してください。",
            target=self.target,
            scene=self.scene,
        )

        ConversionPreset.objects.create(
            user=self.other_user,
            name="他人のプリセット",
            input_text="報告してください。",
            target=self.target,
            scene=self.scene,
        )

        response = self.client.get(
            reverse("conversions:preset-list-create")
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        preset_ids = [
            preset["id"]
            for preset in response_data["presets"]
        ]

        self.assertEqual(preset_ids, [own_preset.pk])

    def test_authenticated_user_can_get_own_preset(self):
        """自分のプリセットを1件取得できる"""
        preset = ConversionPreset.objects.create(
            user=self.user,
            name="取得用プリセット",
            input_text="確認してください。",
            target=self.target,
            scene=self.scene,
        )

        response = self.client.get(
            reverse(
                "conversions:preset-detail",
                args=[preset.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data["ok"])
        self.assertEqual(
            response_data["preset"]["id"],
            preset.pk,
        )
        self.assertEqual(
            response_data["preset"]["input_text"],
            "確認してください。",
        )
        self.assertEqual(
            response_data["preset"]["target"]["id"],
            self.target.pk,
        )
        self.assertEqual(
            response_data["preset"]["scene"]["id"],
            self.scene.pk,
        )

    def test_user_cannot_get_other_users_preset(self):
        """他人のプリセットは取得できない"""
        other_preset = ConversionPreset.objects.create(
            user=self.other_user,
            name="他人の取得禁止プリセット",
            input_text="報告してください。",
            target=self.target,
            scene=self.scene,
        )

        response = self.client.get(
            reverse(
                "conversions:preset-detail",
                args=[other_preset.pk],
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "PRESET_NOT_FOUND",
        )

    def test_authenticated_user_can_delete_own_preset(self):
        """自分のプリセットを削除できる"""
        preset = ConversionPreset.objects.create(
            user=self.user,
            name="削除用プリセット",
            input_text="確認してください。",
            target=self.target,
            scene=self.scene,
        )

        response = self.client.delete(
            reverse(
                "conversions:preset-detail",
                args=[preset.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["deleted_id"],
            preset.pk,
        )
        self.assertFalse(
            ConversionPreset.objects.filter(
                pk=preset.pk
            ).exists()
        )

    def test_user_cannot_delete_other_users_preset(self):
        """他人のプリセットは削除できない"""
        other_preset = ConversionPreset.objects.create(
            user=self.other_user,
            name="他人の削除禁止プリセット",
            input_text="報告してください。",
            target=self.target,
            scene=self.scene,
        )

        response = self.client.delete(
            reverse(
                "conversions:preset-detail",
                args=[other_preset.pk],
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            ConversionPreset.objects.filter(
                pk=other_preset.pk
            ).exists()
        )

    def test_duplicate_name_is_rejected_for_same_user(self):
        """同じユーザーは同名プリセットを登録できない"""
        ConversionPreset.objects.create(
            user=self.user,
            name="重複プリセット",
            input_text="最初の文章です。",
            target=self.target,
            scene=self.scene,
        )

        response = self.client.post(
            reverse("conversions:preset-list-create"),
            data=json.dumps(
                self._payload(name="重複プリセット")
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "VALIDATION_ERROR",
        )
        self.assertEqual(
            ConversionPreset.objects.filter(
                user=self.user,
                name="重複プリセット",
            ).count(),
            1,
        )

    def test_scene_can_be_omitted(self):
        """場面未指定でもプリセットを登録できる"""
        payload = self._payload(
            name="場面未指定プリセット"
        )
        payload["scene"] = None

        response = self.client.post(
            reverse("conversions:preset-list-create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)

        preset = ConversionPreset.objects.get(
            name="場面未指定プリセット"
        )

        self.assertIsNone(preset.scene)
        self.assertIsNone(
            response.json()["preset"]["scene"]
        )

    def test_input_text_longer_than_500_characters_is_rejected(self):
        """501文字以上の文章は登録できない"""
        payload = self._payload(
            name="文字数超過プリセット"
        )
        payload["input_text"] = "あ" * 501

        response = self.client.post(
            reverse("conversions:preset-list-create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "VALIDATION_ERROR",
        )
        self.assertFalse(
            ConversionPreset.objects.filter(
                name="文字数超過プリセット"
            ).exists()
        )