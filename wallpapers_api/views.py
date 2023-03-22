from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import authentication, status

from wallpapers.models import Wallpaper, Download
from .serializers import WallpaperSerializer, DownloadSerializer


class WallpapersApiViewSet(ModelViewSet):
    queryset = Wallpaper.objects.all()
    serializer_class = WallpaperSerializer
    permission_classes = [HasAPIKey | IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


# BELOW: PYTHON SNIPPET TO MAKE A POST REQUEST TO CREATE DOWNLOAD INSTANCE
# USE SUCH POST REQUEST WHEN CLICKING DOWNLOAD BUTTON IN APP

# import requests
# url = 'http://127.0.0.1:8000/api/downloads/'
# with requests.Session() as s:
#     r = s.post(url, data={'pk': 92}, headers={
#         'Authorization': 'Api-Key xxxxxxx',
#     })

class DownloadsApiViewSet(ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    permission_classes = [HasAPIKey | IsAuthenticated]

    def create(self, request, *args, **kwargs):
        wallpaper_pk = request.data['pk']
        serializer = self.get_serializer(data={'wallpaper': wallpaper_pk})

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
