from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Category, Spot, Like, Bookmark, Comment


class CategoryModelTest(TestCase):
    def test_str(self):
        cat = Category.objects.create(name="カフェ", slug="cafe")
        self.assertEqual(str(cat), "カフェ")


class SpotModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.category = Category.objects.create(name="カフェ", slug="cafe")
        self.spot = Spot.objects.create(
            author=self.user,
            title="おしゃれカフェ",
            description="静かでいい感じ",
            area="渋谷",
            category=self.category,
        )

    def test_str(self):
        self.assertEqual(str(self.spot), "おしゃれカフェ")

    def test_like_count(self):
        self.assertEqual(self.spot.like_count, 0)
        Like.objects.create(user=self.user, spot=self.spot)
        self.assertEqual(self.spot.like_count, 1)

    def test_first_image_is_none_when_no_images(self):
        self.assertIsNone(self.spot.first_image)


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.category = Category.objects.create(name="カフェ", slug="cafe")
        self.spot = Spot.objects.create(
            author=self.user,
            title="スポット",
            description="説明",
            area="新宿",
            category=self.category,
        )

    def test_str(self):
        like = Like.objects.create(user=self.user, spot=self.spot)
        self.assertEqual(str(like), "taro → スポット")

    def test_unique_together(self):
        Like.objects.create(user=self.user, spot=self.spot)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user, spot=self.spot)


class BookmarkModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.category = Category.objects.create(name="カフェ", slug="cafe")
        self.spot = Spot.objects.create(
            author=self.user,
            title="スポット",
            description="説明",
            area="新宿",
            category=self.category,
        )

    def test_str(self):
        bookmark = Bookmark.objects.create(user=self.user, spot=self.spot)
        self.assertEqual(str(bookmark), "taro → スポット")


class HomeViewTest(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse("spots:home"))
        self.assertEqual(response.status_code, 200)


class SpotDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.category = Category.objects.create(name="カフェ", slug="cafe")
        self.spot = Spot.objects.create(
            author=self.user,
            title="テストスポット",
            description="説明",
            area="渋谷",
            category=self.category,
        )

    def test_detail_returns_200(self):
        url = reverse("spots:spot_detail", kwargs={"pk": self.spot.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "テストスポット")

    def test_detail_returns_404_for_unknown(self):
        url = reverse("spots:spot_detail", kwargs={"pk": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class SpotSearchViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.category = Category.objects.create(name="カフェ", slug="cafe")
        self.spot = Spot.objects.create(
            author=self.user,
            title="隠れ家カフェ",
            description="静かなカフェです",
            area="下北沢",
            category=self.category,
        )

    def test_search_by_keyword(self):
        url = reverse("spots:spot_search") + "?q=隠れ家"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "隠れ家カフェ")

    def test_search_no_results(self):
        url = reverse("spots:spot_search") + "?q=存在しないキーワード"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SpotLikeViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.category = Category.objects.create(name="カフェ", slug="cafe")
        self.spot = Spot.objects.create(
            author=self.user,
            title="スポット",
            description="説明",
            area="新宿",
            category=self.category,
        )
        self.client.login(username="taro", password="pass1234")

    def test_like_and_unlike(self):
        url = reverse("spots:spot_like", kwargs={"pk": self.spot.pk})
        # いいね
        self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.spot.likes.count(), 1)
        # いいね解除
        self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.spot.likes.count(), 0)


class SpotBookmarkViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.category = Category.objects.create(name="カフェ", slug="cafe")
        self.spot = Spot.objects.create(
            author=self.user,
            title="スポット",
            description="説明",
            area="新宿",
            category=self.category,
        )
        self.client.login(username="taro", password="pass1234")

    def test_bookmark_response_includes_count(self):
        url = reverse("spots:spot_bookmark", kwargs={"pk": self.spot.pk})
        import json
        response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("bookmarked", data)
        self.assertIn("count", data)
