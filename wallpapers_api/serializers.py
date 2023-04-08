from django.core.exceptions import ValidationError
from rest_framework import serializers

from wallpapers.models import Wallpaper, Download


class WallpaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallpaper
        fields = ['pk', 'title', 'tags', 'category', 'image', 'thumbnail']


class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Download
        fields = ['wallpaper']