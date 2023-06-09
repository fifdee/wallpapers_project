from django.urls import include, path
from rest_framework import routers

from wallpapers_api.views import WallpapersApiViewSet, DownloadsApiViewSet

router = routers.DefaultRouter()
router.register('wallpapers', WallpapersApiViewSet)
router.register('downloads', DownloadsApiViewSet)


urlpatterns = [
    path('', include(router.urls)),
]