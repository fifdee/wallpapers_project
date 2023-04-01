import datetime

from allauth.account.views import PasswordResetView
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import View, DetailView
from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector

from wallpapers.forms import UserConvertForm, SearchForm
from wallpapers.models import Wallpaper, Category, Download, User
from wallpapers.my_mixins import CheckIfUserConverted
from wallpapers.utils import get_value


class WallpapersListView(CheckIfUserConverted, View):
    def get(self, *args, **kwargs):
        print(self.request.user_agent)

        wps = Wallpaper.objects.filter(is_landscape=False, approved=True)

        page = get_value(self.request, 'page', 1)
        query = get_value(self.request, 'query', '')
        category = get_value(self.request, 'category', 'all')
        sort = get_value(self.request, 'sort', 'newest')

        if query != '':
            vector = SearchVector('title')
            search_query = SearchQuery(query)
            wps = wps.annotate(rank=SearchRank(vector, search_query)).filter(rank__gte=0.05).order_by('-rank')

        if category != 'all':
            wps = wps.filter(category__title=category)

        if sort == 'newest':
            wps = wps.order_by('-date_added')

        elif sort == 'trending':
            recent_downloads = Download.objects.filter(time__gte=now().date() - datetime.timedelta(days=30))
            wps = wps.filter(download__in=recent_downloads).distinct()

            def f(wp):
                return recent_downloads.filter(wallpaper=wp).count()

            wps = sorted(wps, key=f, reverse=True)

        paginator = Paginator(wps, 12)
        page_obj = paginator.get_page(page)

        user_downloads = Download.objects.filter(time__gte=now().date() - datetime.timedelta(days=1),
                                                 user=self.request.user).count()

        context = {
            'object_list': page_obj,
            'categories': Category.objects.all(),
            'user_downloads': user_downloads,
            'form': SearchForm(data={'query': query}),
        }

        return render(self.request, template_name='wallpapers/wallpapers_list_view.html', context=context)


class WallpapersNotApprovedListView(CheckIfUserConverted, View):
    def get(self, *args, **kwargs):
        if self.request.user.is_superuser:
            wps = Wallpaper.objects.filter(approved=False)
            paginator = Paginator(wps, 1)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            context = {
                'object_list': page_obj,
            }

            return render(self.request, template_name='wallpapers/wallpapers_not_approved_list.html', context=context)
        else:
            return redirect('wallpapers_list_view')


class WallpaperDetailView(DetailView):
    queryset = Wallpaper.objects.all()
    template_name = 'wallpapers/wallpaper_detail_view.html'


class DownloadCreateView(View):
    def post(self, *args, **kwargs):
        pk = self.request.POST['pk']
        wp = Wallpaper.objects.get(pk=pk)
        print(f'wp with pk={pk}')

        if not self.request.session.get('downloaded'):
            self.request.session['downloaded'] = []

        if not settings.DEBUG:
            if wp.id not in self.request.session.get('downloaded'):
                Download.objects.create(wallpaper=wp, user=self.request.user)
        else:
            Download.objects.create(wallpaper=wp, user=self.request.user)

        self.request.session['downloaded'].append(wp.id)

        return HttpResponse(f'ok')


def wallpaper_approve(request):
    if request.method == 'POST':
        if request.user.is_superuser:
            pk = request.POST['pk']
            wp = Wallpaper.objects.get(pk=pk)

            wp.approved = True
            wp.save()

        return redirect('wallpapers_not_approved_list_view')


def wallpaper_approve_premium(request):
    if request.method == 'POST':
        if request.user.is_superuser:
            pk = request.POST['pk']
            wp = Wallpaper.objects.get(pk=pk)

            wp.approved = True
            wp.is_premium = True
            wp.save()

        return redirect('wallpapers_not_approved_list_view')


def wallpaper_delete(request):
    if request.method == 'POST':
        if request.user.is_superuser:
            pk = request.POST['pk']
            wp = Wallpaper.objects.get(pk=pk)

            wp.delete()

        return redirect('wallpapers_not_approved_list_view')


def robots_txt_view(request):
    lines = [
        "User-Agent: *",
        "Disallow: /private/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def indexnow_view(request):
    content = '5119ecb8d7bc4cad8c91f00fcd257863'
    return HttpResponse(content, content_type="text/plain")


class SetEmailResetPassword(PasswordResetView):
    form_class = UserConvertForm
    template_name = 'account/convert.html'

    def dispatch(self, request, *args, **kwargs):
        # if user not created - redirect
        if self.request.user.is_anonymous:
            return redirect('wallpapers_list_view')

        # if the user is not temporary - redirect
        if not self.request.user.temporary:
            return redirect('wallpapers_list_view')

        return super(SetEmailResetPassword, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"].lower()

        if User.objects.filter(email=email).exists():
            user_with_this_email = User.objects.get(email=email)
            if self.request.user != user_with_this_email:
                form.add_error('email', 'This e-mail is already taken.')
                return super().form_invalid(form)

        return super(SetEmailResetPassword, self).form_valid(form)
