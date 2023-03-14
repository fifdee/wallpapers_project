from django.contrib import admin

from wallpapers.models import Category, Wallpaper

# Register your models here.
admin.site.register(Category)
admin.site.register(Wallpaper)