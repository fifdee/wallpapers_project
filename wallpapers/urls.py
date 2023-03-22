from django.urls import path
from .views import WallpapersListView, WallpaperDetailView, DownloadCreateView

urlpatterns = [
    path('', WallpapersListView.as_view(), name='wallpapers_list_view'),
    path('details/<slug:slug>', WallpaperDetailView.as_view(), name='wallpaper_detail_view'),
    path('download/', DownloadCreateView.as_view(), name='wallpaper_download_view')
]