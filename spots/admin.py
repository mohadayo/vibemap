from django.contrib import admin
from .models import Category, Spot, SpotImage, Like, Bookmark, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class SpotImageInline(admin.TabularInline):
    model = SpotImage
    extra = 1


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "area", "created_at")
    list_filter = ("category", "area")
    search_fields = ("title", "description", "area")
    inlines = [SpotImageInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "spot", "text", "created_at")
    list_filter = ("created_at",)
    search_fields = ("text",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "spot", "created_at")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "spot", "created_at")
