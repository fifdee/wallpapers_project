# Generated by Django 4.1.7 on 2023-03-14 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallpapers', '0004_wallpaper_is_landscape'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallpaper',
            name='is_premium',
            field=models.BooleanField(default=False),
        ),
    ]
