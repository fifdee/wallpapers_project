# Generated by Django 4.1.7 on 2023-03-16 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallpapers', '0006_alter_wallpaper_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wallpaper',
            old_name='description',
            new_name='tags',
        ),
    ]