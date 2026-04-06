from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField("カテゴリ名", max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"

    def __str__(self):
        return self.name


class Spot(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spots")
    title = models.CharField("タイトル", max_length=100)
    description = models.TextField("説明")
    area = models.CharField("エリア", max_length=100)
    address = models.CharField("住所", max_length=200, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="spots", verbose_name="カテゴリ"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "スポット"
        verbose_name_plural = "スポット"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def first_image(self):
        img = self.images.first()
        return img.image if img else None

    @property
    def like_count(self):
        return self.likes.count()


class SpotImage(models.Model):
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("画像", upload_to="spots/")
    order = models.PositiveIntegerField("表示順", default=0)

    class Meta:
        verbose_name = "スポット画像"
        verbose_name_plural = "スポット画像"
        ordering = ["order"]

    def __str__(self):
        return f"{self.spot.title} - 画像{self.order}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "いいね"
        verbose_name_plural = "いいね"
        unique_together = ("user", "spot")

    def __str__(self):
        return f"{self.user.username} → {self.spot.title}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "保存"
        verbose_name_plural = "保存"
        unique_together = ("user", "spot")

    def __str__(self):
        return f"{self.user.username} → {self.spot.title}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField("コメント", max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "コメント"
        verbose_name_plural = "コメント"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}"
