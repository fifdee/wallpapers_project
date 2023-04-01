from django.contrib.sitemaps import Sitemap
from .models import Wallpaper


class WallpaperSitemap(Sitemap):
    changefreq = "hourly"
    priority = 1

    def items(self):
        return Wallpaper.objects.filter(approved=True)

    def lastmod(self, obj):
        return obj.date_added
