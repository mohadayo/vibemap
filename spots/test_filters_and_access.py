from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Category, Spot


class SpotSearchFilterTest(TestCase):
    """検索フィルタリングのテスト"""

    def setUp(self):
        self.user = User.objects.create_user(username="taro", password="pass1234")
        self.cafe = Category.objects.create(name="カフェ", slug="cafe")
        self.park = Category.objects.create(name="公園", slug="park")
        self.spot1 = Spot.objects.create(
            author=self.user,
            title="渋谷カフェ",
            description="おしゃれなカフェ",
            area="渋谷",
            category=self.cafe,
        )
        self.spot2 = Spot.objects.create(
            author=self.user,
            title="新宿公園",
            description="広い公園",
            area="新宿",
            category=self.park,
        )
        self.spot3 = Spot.objects.create(
            author=self.user,
            title="下北沢カフェ",
            description="隠れ家カフェ",
            area="下北沢",
            category=self.cafe,
        )

    def test_filter_by_category_only(self):
        """カテゴリ単体でフィルタリングできる"""
        url = reverse("spots:spot_search") + "?category=cafe"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        spots = response.context["spots"]
        self.assertEqual(len(spots), 2)
        titles = {s.title for s in spots}
        self.assertIn("渋谷カフェ", titles)
        self.assertIn("下北沢カフェ", titles)

    def test_filter_by_area_only(self):
        """エリア単体でフィルタリングできる"""
        url = reverse("spots:spot_search") + "?area=渋谷"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        spots = response.context["spots"]
        self.assertEqual(len(spots), 1)
        self.assertEqual(spots[0].title, "渋谷カフェ")

    def test_filter_combined_keyword_category_area(self):
        """キーワード・カテゴリ・エリアの複合フィルタが動作する"""
        url = reverse("spots:spot_search") + "?q=カフェ&category=cafe&area=下北沢"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        spots = response.context["spots"]
        self.assertEqual(len(spots), 1)
        self.assertEqual(spots[0].title, "下北沢カフェ")

    def test_filter_returns_empty(self):
        """該当なしのフィルタで空の結果が返る"""
        url = reverse("spots:spot_search") + "?q=存在しない&category=park&area=北海道"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        spots = response.context["spots"]
        self.assertEqual(len(spots), 0)


class AccessControlTest(TestCase):
    """アクセス制御のエッジケーステスト"""

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

    def test_unauthenticated_like_redirects_to_login(self):
        """未ログインユーザーのいいね操作はログインページにリダイレクトされる"""
        url = reverse("spots:spot_like", kwargs={"pk": self.spot.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response["Location"])

    def test_unauthenticated_bookmark_redirects_to_login(self):
        """未ログインユーザーのブックマーク操作はログインページにリダイレクトされる"""
        url = reverse("spots:spot_bookmark", kwargs={"pk": self.spot.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response["Location"])

    def test_unauthenticated_comment_not_created(self):
        """未ログインユーザーのコメント投稿ではコメントが作成されない"""
        url = reverse("spots:spot_detail", kwargs={"pk": self.spot.pk})
        self.client.post(url, {"text": "未ログインコメント"})
        from .models import Comment
        self.assertEqual(Comment.objects.filter(spot=self.spot).count(), 0)

    def test_like_nonexistent_spot_returns_404(self):
        """存在しないスポットへのいいねは404を返す"""
        self.client.login(username="taro", password="pass1234")
        url = reverse("spots:spot_like", kwargs={"pk": 99999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_bookmark_nonexistent_spot_returns_404(self):
        """存在しないスポットへのブックマークは404を返す"""
        self.client.login(username="taro", password="pass1234")
        url = reverse("spots:spot_bookmark", kwargs={"pk": 99999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_create_redirects_to_login(self):
        """未ログインユーザーのスポット作成はログインページにリダイレクトされる"""
        url = reverse("spots:spot_create")
        response = self.client.post(url, {
            "title": "テスト",
            "description": "説明",
            "area": "渋谷",
            "category": self.category.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response["Location"])

    def test_unauthenticated_delete_redirects_to_login(self):
        """未ログインユーザーのスポット削除はログインページにリダイレクトされる"""
        url = reverse("spots:spot_delete", kwargs={"pk": self.spot.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response["Location"])
        self.assertTrue(Spot.objects.filter(pk=self.spot.pk).exists())
