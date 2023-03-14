from django.urls import include, path
from rest_framework import routers

from wallpapers_api.views import WallpapersApiViewSet

router = routers.DefaultRouter()
router.register('wallpapers', WallpapersApiViewSet)


urlpatterns = [
    path('', include(router.urls)),
]