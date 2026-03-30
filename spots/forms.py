from django import forms
from .models import Spot, SpotImage, Comment


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
