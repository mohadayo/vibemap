from django import forms
from django.core.exceptions import ValidationError
from .models import Spot, SpotImage, Comment

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image_file(f):
    """画像ファイルの拡張子・MIMEタイプ・サイズをバリデーションする"""
    if f.content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            f"対応していない画像形式です（{f.content_type}）。"
            "JPEG, PNG, WebP, GIF のみ対応しています。"
        )
    if f.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f"画像サイズが上限（5MB）を超えています（{f.size / (1024 * 1024):.1f}MB）。"
        )


class SpotForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ("title", "description", "area", "address", "category")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "スポット名"}),
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 5, "placeholder": "このスポットの魅力を教えてください"}
            ),
            "area": forms.TextInput(attrs={"class": "form-control", "placeholder": "例: 渋谷、下北沢"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "住所（任意）"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }


class SpotImageForm(forms.ModelForm):
    class Meta:
        model = SpotImage
        fields = ("image",)
        widgets = {
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "コメントを書く...",
                }
            ),
        }
