import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignUpForm, ProfileForm

logger = logging.getLogger("accounts")


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info("New user signed up: %s", user.username)
            return redirect("spots:home")
        else:
            logger.warning("Signup form invalid: %s", form.errors)
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            logger.info("Profile updated for user=%s", request.user.username)
            return redirect("accounts:user_profile", username=request.user.username)
        else:
            logger.warning("Profile edit form invalid for user=%s: %s", request.user.username, form.errors)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/profile_edit.html", {"form": form})


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    spots = user.spots.all()
    return render(request, "accounts/user_profile.html", {"profile_user": user, "spots": spots})


@login_required
def bookmark_list(request):
    bookmarks = request.user.bookmarks.select_related("spot__category", "spot__author").all()
    return render(request, "accounts/bookmark_list.html", {"bookmarks": bookmarks})
