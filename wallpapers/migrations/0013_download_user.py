# Generated by Django 4.1.7 on 2023-03-21 14:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallpapers', '0012_remove_download_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='download',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
