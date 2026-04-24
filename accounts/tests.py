from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Profile


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")

    def test_profile_created_on_user_save(self):
        """ユーザー作成時にプロフィールが自動生成される"""
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertIsInstance(self.user.profile, Profile)

    def test_str_without_display_name(self):
        """表示名なしの場合はユーザー名を返す"""
        self.assertEqual(str(self.user.profile), "taro")

    def test_str_with_display_name(self):
        """表示名が設定されている場合はそちらを返す"""
        self.user.profile.display_name = "太郎"
        self.user.profile.save()
        self.assertEqual(str(self.user.profile), "太郎")

    def test_get_display_name(self):
        self.assertEqual(self.user.profile.get_display_name(), "taro")
        self.user.profile.display_name = "太郎"
        self.user.profile.save()
        self.assertEqual(self.user.profile.get_display_name(), "太郎")


class SignUpViewTest(TestCase):
    def test_signup_page_returns_200(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "Str0ngPass!",
                "password2": "Str0ngPass!",
            },
        )
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_invalid_password_shows_errors(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "abc",
                "password2": "abc",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")

    def test_user_profile_returns_200(self):
        url = reverse("accounts:user_profile", kwargs={"username": "taro"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_user_profile_404_for_unknown(self):
        url = reverse("accounts:user_profile", kwargs={"username": "unknown"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_user_profile_pagination(self):
        """プロフィールページのスポット一覧が12件ずつページネーションされる"""
        from spots.models import Category, Spot

        cat = Category.objects.create(name="カフェ", slug="cafe")
        for i in range(15):
            Spot.objects.create(
                author=self.user,
                title=f"スポット{i}",
                description="説明",
                area="渋谷",
                category=cat,
            )
        url = reverse("accounts:user_profile", kwargs={"username": "taro"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["spots"]), 12)

        response2 = self.client.get(url + "?page=2")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.context["spots"]), 3)


class SignUpDuplicateTest(TestCase):
    """重複ユーザー名のサインアップテスト"""

    def test_signup_duplicate_username_shows_error(self):
        """既存ユーザー名でのサインアップはエラーを表示しユーザーが作成されない"""
        User.objects.create_user(username="existing", password="pass1234")
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "existing",
                "email": "new@example.com",
                "password1": "Str0ngPass!",
                "password2": "Str0ngPass!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="existing").count(), 1)

    def test_signup_auto_login(self):
        """サインアップ成功後に自動ログインされホームにリダイレクトされる"""
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "Str0ngPass!",
                "password2": "Str0ngPass!",
            },
        )
        self.assertRedirects(response, reverse("spots:home"))


class ProfileEditViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.client.login(username="taro", password="pass1234")

    def test_profile_edit_requires_login(self):
        self.client.logout()
        url = reverse("accounts:profile_edit")
        response = self.client.get(url)
        self.assertRedirects(response, reverse("accounts:login") + "?next=" + url)

    def test_profile_edit_returns_200_when_logged_in(self):
        url = reverse("accounts:profile_edit")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_edit_post_updates_display_name(self):
        """プロフィール編集POSTで表示名が更新される"""
        url = reverse("accounts:profile_edit")
        response = self.client.post(url, {"display_name": "太郎", "bio": "自己紹介です"})
        self.assertRedirects(
            response,
            reverse("accounts:user_profile", kwargs={"username": "taro"}),
        )
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, "太郎")
        self.assertEqual(self.user.profile.bio, "自己紹介です")

    def test_profile_edit_post_clears_display_name(self):
        """表示名を空にするとユーザー名にフォールバックする"""
        self.user.profile.display_name = "太郎"
        self.user.profile.save()
        url = reverse("accounts:profile_edit")
        self.client.post(url, {"display_name": "", "bio": ""})
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.display_name, "")
        self.assertEqual(self.user.profile.get_display_name(), "taro")


class BookmarkListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.client.login(username="taro", password="pass1234")

    def test_bookmark_list_returns_200(self):
        url = reverse("accounts:bookmark_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_bookmark_list_requires_login(self):
        self.client.logout()
        url = reverse("accounts:bookmark_list")
        response = self.client.get(url)
        self.assertRedirects(response, reverse("accounts:login") + "?next=" + url)


class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="taro", password="pass1234", email="taro@example.com"
        )

    def test_password_reset_page_returns_200(self):
        """パスワードリセットページが表示される"""
        url = reverse("accounts:password_reset")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_password_reset_done_page_returns_200(self):
        """パスワードリセットメール送信完了ページが表示される"""
        url = reverse("accounts:password_reset_done")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_password_reset_complete_page_returns_200(self):
        """パスワードリセット完了ページが表示される"""
        url = reverse("accounts:password_reset_complete")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_password_reset_post_redirects(self):
        """パスワードリセットフォーム送信後にリダイレクトされる"""
        url = reverse("accounts:password_reset")
        response = self.client.post(url, {"email": "taro@example.com"})
        self.assertRedirects(response, "/accounts/password_reset/done/")

    def test_password_reset_confirm_invalid_link(self):
        """無効なトークンでパスワードリセット確認ページにアクセス"""
        url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": "invalid", "token": "invalid-token"},
        )
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


class SecuritySettingsTest(TestCase):
    def test_production_security_settings(self):
        """本番環境のセキュリティ設定が正しく定義されている"""
        import inspect
        import config.settings as raw_settings
        source = inspect.getsource(raw_settings)
        self.assertIn("SECURE_SSL_REDIRECT", source)
        self.assertIn("SECURE_HSTS_SECONDS", source)
        self.assertIn("SESSION_COOKIE_SECURE", source)
        self.assertIn("CSRF_COOKIE_SECURE", source)
        self.assertIn("SECURE_PROXY_SSL_HEADER", source)
