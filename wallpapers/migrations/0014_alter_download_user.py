# Generated by Django 4.1.7 on 2023-03-22 11:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallpapers', '0013_download_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='download',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]