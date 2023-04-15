from django.urls import path
from .views import WallpapersListView, WallpaperDetailView, DownloadCreateView, WallpapersNotApprovedListView, \
    wallpaper_approve, wallpaper_approve_premium, wallpaper_reject

urlpatterns = [
    path('', WallpapersListView.as_view(), name='wallpapers_list_view'),
    path('notapproved/', WallpapersNotApprovedListView.as_view(), name='wallpapers_not_approved_list_view'),
    path('details/<slug:slug>', WallpaperDetailView.as_view(), name='wallpaper_detail_view'),
    path('download/', DownloadCreateView.as_view(), name='wallpaper_download_view'),

    path('approve/', wallpaper_approve, name='wallpaper_approve'),
    path('approve_premium/', wallpaper_approve_premium, name='wallpaper_approve_premium'),
    path('reject/', wallpaper_reject, name='wallpaper_reject'),
]