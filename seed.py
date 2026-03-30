"""初期カテゴリデータを投入するスクリプト"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from spots.models import Category

categories = [
    ("カフェ", "cafe"),
    ("ラーメン", "ramen"),
    ("古着屋", "vintage"),
    ("サウナ", "sauna"),
    ("夜景", "nightview"),
    ("公園", "park"),
    ("居酒屋", "izakaya"),
    ("パン屋", "bakery"),
    ("雑貨屋", "zakka"),
    ("その他", "other"),
]

for name, slug in categories:
    Category.objects.get_or_create(name=name, slug=slug)
    print(f"  {name} ({slug})")

print("カテゴリの登録が完了しました！")
