import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Spot, SpotImage, Like, Bookmark, Category
from .forms import SpotForm, CommentForm

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

logger = logging.getLogger("spots")


def home(request):
    spots = Spot.objects.select_related("author", "category").prefetch_related("images")[:20]
    categories = Category.objects.all()
    return render(request, "spots/home.html", {"spots": spots, "categories": categories})


def _validate_image(f):
    """Return an error message if the file is not a valid image, else None."""
    if f.content_type not in ALLOWED_IMAGE_TYPES:
        return f"'{f.name}' は対応していないファイル形式です。JPEG/PNG/GIF/WebPのみ対応しています。"
    if f.size > MAX_IMAGE_SIZE:
        return f"'{f.name}' のファイルサイズが上限(10MB)を超えています。"
    return None


@login_required
def spot_create(request):
    if request.method == "POST":
        form = SpotForm(request.POST)
        files = request.FILES.getlist("images")
        if form.is_valid() and files:
            # Validate all uploaded images before saving anything
            for f in files:
                error = _validate_image(f)
                if error:
                    logger.warning("Image validation failed in spot_create: %s", error)
                    messages.error(request, error)
                    return render(request, "spots/spot_create.html", {"form": form})

            try:
                with transaction.atomic():
                    spot = form.save(commit=False)
                    spot.author = request.user
                    spot.save()
                    for i, f in enumerate(files):
                        SpotImage.objects.create(spot=spot, image=f, order=i)
            except Exception:
                logger.exception("Failed to create spot for user=%s", request.user)
                messages.error(request, "スポットの作成中にエラーが発生しました。もう一度お試しください。")
                return render(request, "spots/spot_create.html", {"form": form})

            logger.info("Spot created: id=%d title='%s' by user=%s", spot.pk, spot.title, request.user)
            return redirect("spots:spot_detail", pk=spot.pk)
    else:
        form = SpotForm()
    return render(request, "spots/spot_create.html", {"form": form})


def spot_detail(request, pk):
    spot = get_object_or_404(
        Spot.objects.select_related("author", "category").prefetch_related("images", "comments__user"),
        pk=pk,
    )
    is_liked = False
    is_bookmarked = False
    if request.user.is_authenticated:
        is_liked = spot.likes.filter(user=request.user).exists()
        is_bookmarked = spot.bookmarks.filter(user=request.user).exists()

    comment_form = CommentForm()
    if request.method == "POST" and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.spot = spot
            comment.save()
            logger.info("Comment added on spot=%d by user=%s", pk, request.user)
            return redirect("spots:spot_detail", pk=pk)

    return render(
        request,
        "spots/spot_detail.html",
        {
            "spot": spot,
            "is_liked": is_liked,
            "is_bookmarked": is_bookmarked,
            "comment_form": comment_form,
        },
    )


@login_required
def spot_edit(request, pk):
    spot = get_object_or_404(Spot, pk=pk, author=request.user)
    if request.method == "POST":
        form = SpotForm(request.POST, instance=spot)
        files = request.FILES.getlist("images")
        if form.is_valid():
            form.save()
            if files:
                spot.images.all().delete()
                for i, f in enumerate(files):
                    SpotImage.objects.create(spot=spot, image=f, order=i)
            logger.info("Spot edited: id=%d by user=%s", spot.pk, request.user)
            return redirect("spots:spot_detail", pk=spot.pk)
    else:
        form = SpotForm(instance=spot)
    return render(request, "spots/spot_edit.html", {"form": form, "spot": spot})


@login_required
def spot_delete(request, pk):
    spot = get_object_or_404(Spot, pk=pk, author=request.user)
    if request.method == "POST":
        logger.info("Spot deleted: id=%d title='%s' by user=%s", spot.pk, spot.title, request.user)
        spot.delete()
        return redirect("spots:home")
    return render(request, "spots/spot_delete.html", {"spot": spot})


@login_required
def spot_like(request, pk):
    spot = get_object_or_404(Spot, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, spot=spot)
    if not created:
        like.delete()
    logger.info("Spot %s: id=%d by user=%s", "liked" if created else "unliked", pk, request.user)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"liked": created, "count": spot.like_count})
    return redirect("spots:spot_detail", pk=pk)


@login_required
def spot_bookmark(request, pk):
    spot = get_object_or_404(Spot, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, spot=spot)
    if not created:
        bookmark.delete()
    logger.info("Spot %s: id=%d by user=%s", "bookmarked" if created else "unbookmarked", pk, request.user)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"bookmarked": created})
    return redirect("spots:spot_detail", pk=pk)


def spot_search(request):
    q = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")
    area = request.GET.get("area", "")

    spots = Spot.objects.select_related("author", "category").prefetch_related("images")

    if q:
        spots = spots.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category_slug:
        spots = spots.filter(category__slug=category_slug)
    if area:
        spots = spots.filter(area__icontains=area)

    logger.info("Search: q='%s' category='%s' area='%s'", q, category_slug, area)
    categories = Category.objects.all()
    return render(
        request,
        "spots/search.html",
        {"spots": spots[:40], "categories": categories, "q": q, "category_slug": category_slug, "area": area},
    )
