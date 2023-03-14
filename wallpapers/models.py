from django.contrib.auth.models import AbstractUser
from django.contrib.sitemaps import ping_google
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.timezone import now

from wallpapers.utils import unique_slugify, compress_image_return_with_thumbnail


class User(AbstractUser):
    temporary = models.BooleanField(default=True)


class Wallpaper(models.Model):
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(default='', blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(max_length=200)
    thumbnail = models.ImageField(blank=True, max_length=200)
    downloads_count = models.IntegerField(default=0)
    approved = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=now)
    is_landscape = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    slug = models.SlugField(null=False, unique=True, blank=True)

    def __str__(self):
        if len(self.title) > 50:
            return self.title[:50] + '[...]'
        else:
            return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.image, self.thumbnail = compress_image_return_with_thumbnail(self.image)
            if self.thumbnail.height > self.thumbnail.width:
                self.is_landscape = False

        if not self.title:
            self.title = str(self.image.name).replace('fifdee_', '').replace('_', ' ').replace('.jpg', '')

        if not self.slug:
            unique_slugify(self, self.title)
        try:
            ...
            # ping_google()
        except Exception:
            # Bare 'except' because we could get a variety
            # of HTTP-related exceptions.
            pass

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('wallpaper_details', args=[self.slug])

    class Meta:
        ordering = ['-date_added']


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    title = models.CharField(max_length=100)
    description = models.TextField(default='')

    def __str__(self):
        return self.title
