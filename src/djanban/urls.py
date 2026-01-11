from django.urls import path
from django.urls import re_path, include
from django.contrib import admin

from djanban.apps.index import views as index_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as serve_static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    path('', index_views.index, name="index"),

    re_path(r'^admin/', admin.site.urls),

    path('base/', include(('djanban.apps.base.urls', 'base'), namespace="base")),
    path('member/', include(('djanban.apps.members.urls', 'members'), namespace="members")),
    path('api/', include(('djanban.apps.api.urls', 'api'), namespace="api")),
    path('boards/', include(('djanban.apps.boards.urls', 'boards'), namespace="boards")),
    path('times/', include(('djanban.apps.dev_times.urls', 'dev_times'), namespace="dev_times")),
    path('charts/', include(('djanban.apps.charts.urls', 'charts'), namespace="charts")),
    path('hourly_rates/', include(('djanban.apps.hourly_rates.urls', 'hourly_rates'), namespace="hourly_rates")),
    path('fetch/', include(('djanban.apps.fetch.urls', 'fetch'), namespace="fetch")),
    path('forecasters/', include(('djanban.apps.forecasters.urls', 'forecasters'), namespace="forecasters")),
    path('environment/', include(('djanban.apps.dev_environment.urls', 'dev_environment'), namespace="dev_environment")),
    path('multiboards/', include(('djanban.apps.multiboards.urls', 'multiboards'), namespace="multiboards")),
    path('notifications/', include(('djanban.apps.notifications.urls', 'notifications'), namespace="notifications")),
    path('reports/', include(('djanban.apps.reports.urls', 'reports'), namespace="reports")),
    path('slideshow/', include(('djanban.apps.slideshow.urls', 'slideshow'), namespace="slideshow")),
    path('visitors/', include(('djanban.apps.visitors.urls', 'visitors'), namespace="visitors")),
    path('niko-niko-calendar/', include(('djanban.apps.niko_niko_calendar.urls', 'niko_niko_calendar'), namespace="niko_niko_calendar")),
    path('work-hours-packages/', include(('djanban.apps.work_hours_packages.urls', 'work_hours_packages'), namespace="work_hours_packages")),

    path('async_include/', include(('async_include.urls', 'async_include'), namespace="async_include")),

    path('password-reset/', include(('djanban.apps.password_reseter.urls', 'password_reseter'), namespace="password_reseter")),

    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('captcha/', include('captcha.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve_static, { 'document_root': settings.MEDIA_ROOT, }),
        re_path(r'^static/(?P<path>.*)$', serve_static, { 'document_root': settings.STATIC_ROOT }),
    ]
