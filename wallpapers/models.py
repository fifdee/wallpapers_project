from urllib.request import urlopen

from django.contrib.auth.models import AbstractUser
from django.contrib.sitemaps import ping_google
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.timezone import now

from wallpapers.utils import unique_slugify, compress_image_return_with_thumbnail, get_image_tags, \
    title_from_filename, get_description_from_keywords


class User(AbstractUser):
    temporary = models.BooleanField(default=True)


class Wallpaper(models.Model):
    title = models.TextField(blank=True)
    tags = models.TextField(default='', blank=True)
    description = models.TextField(default='', blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(max_length=200)
    thumbnail = models.ImageField(blank=True, max_length=200)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=now)
    is_landscape = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True, max_length=150)

    def __str__(self):
        if len(self.title) > 150:
            return self.title[:150] + '[...]'
        else:
            return self.title

    def save(self, *args, **kwargs):
        if not self.id:
            self.image, self.thumbnail = compress_image_return_with_thumbnail(self.image)
            if self.thumbnail.height > self.thumbnail.width:
                self.is_landscape = False

        if not self.title:
            title_name = title_from_filename(self.image.name, self.is_landscape)
            self.title = title_name

        return super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        # single instance delete only, doesn't work for queryset deleting (e.g. in admin)
        self.image.delete()
        self.thumbnail.delete()

        super(Wallpaper, self).delete()

    def get_absolute_url(self):
        return reverse('wallpaper_detail_view', args=[self.slug])

    class Meta:
        ordering = ['-date_added']


def post_caption_wallpaper(sender, instance, created, **kwargs):
    if created:
        keywords = instance.title

        print(f'Image url: {instance.image.url}')
        r = get_image_tags(instance.image.url)
        print(r)
        if r:
            keywords = keywords + ', ' + ', '.join(r)
            instance.tags = ', '.join(r) + ', ' + instance.tags
            instance.title = instance.title + ' ( tags: ' + instance.tags + ' )'

        description = get_description_from_keywords(keywords)
        if description:
            instance.description = description

        unique_slugify(instance, instance.title)
        instance.save()

        try:
            ...
            ping_google()

            # Ping search engines
            slug = instance.slug
            urlopen(f'https://www.bing.com/indexnow?url=https://wallpapers.v45.org/{slug}/&key'
                    '=5119ecb8d7bc4cad8c91f00fcd257863')
        except Exception:
            # Bare 'except' because we could get a variety
            # of HTTP-related exceptions.
            pass


post_save.connect(post_caption_wallpaper, sender=Wallpaper)


class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories'

    title = models.CharField(max_length=100)
    description = models.TextField(default='')

    def __str__(self):
        return self.title


class Download(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    wallpaper = models.ForeignKey('Wallpaper', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.wallpaper) + ' | ' + str(self.time)
