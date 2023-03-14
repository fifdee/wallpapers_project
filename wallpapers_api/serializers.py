from django.core.exceptions import ValidationError
from rest_framework import serializers

from wallpapers.models import Wallpaper


class WallpaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallpaper
        fields = '__all__'

    # def validate_content(self, data):
    #     wallpapers = Wallpaper.objects.all()
    #     for wallpaper in wallpapers:
    #         if False:
    #             raise ValidationError(message='...')
    #
    #     return data
