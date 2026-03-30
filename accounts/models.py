from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField("表示名", max_length=50, blank=True)
    bio = models.TextField("自己紹介", max_length=300, blank=True)
    avatar = models.ImageField("アイコン", upload_to="avatars/", blank=True)

    class Meta:
        verbose_name = "プロフィール"
        verbose_name_plural = "プロフィール"

    def __str__(self):
        return self.display_name or self.user.username

    def get_display_name(self):
        return self.display_name or self.user.username


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
