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
