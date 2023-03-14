from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import authentication

from wallpapers.models import Wallpaper
from .serializers import WallpaperSerializer


class WallpapersApiViewSet(ModelViewSet):
    queryset = Wallpaper.objects.all()
    serializer_class = WallpaperSerializer
    # authentication_classes = [authentication.RemoteUserAuthentication]
    permission_classes = [HasAPIKey | IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

