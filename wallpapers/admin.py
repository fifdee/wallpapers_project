from django.contrib import admin

from wallpapers.models import Category, Wallpaper, Download, User

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Wallpaper)
admin.site.register(Download)