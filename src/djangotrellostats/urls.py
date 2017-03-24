# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin

from djangotrellostats.apps.index import views as index_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as serve_static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    url(r'^$', index_views.index, name="index"),

    url(r'^admin/', admin.site.urls),

    url(r'^base/', include('djangotrellostats.apps.base.urls', namespace="base")),
    url(r'^member/', include('djangotrellostats.apps.members.urls', namespace="members")),
    url(r'^api/', include('djangotrellostats.apps.api.urls', namespace="api")),
    url(r'^boards/', include('djangotrellostats.apps.boards.urls', namespace="boards")),
    url(r'^times/', include('djangotrellostats.apps.dev_times.urls', namespace="dev_times")),
    url(r'^charts/', include('djangotrellostats.apps.charts.urls', namespace="charts")),
    url(r'^hourly_rates/', include('djangotrellostats.apps.hourly_rates.urls', namespace="hourly_rates")),
    url(r'^fetch/', include('djangotrellostats.apps.fetch.urls', namespace="fetch")),
    url(r'^environment/', include('djangotrellostats.apps.dev_environment.urls', namespace="dev_environment")),
    url(r'^slideshow/', include('djangotrellostats.apps.slideshow.urls', namespace="slideshow")),
    url(r'^visitors/', include('djangotrellostats.apps.visitors.urls', namespace="visitors")),
    url(r'^niko-niko-calendar/', include('djangotrellostats.apps.niko_niko_calendar.urls', namespace="niko_niko_calendar")),

    url(r'^async_include/', include('async_include.urls', namespace="async_include")),

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),

    url(r'^captcha/', include('captcha.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve_static, { 'document_root': settings.MEDIA_ROOT, }),
        url(r'^static/(?P<path>.*)$', serve_static, { 'document_root': settings.STATIC_ROOT }),
        #url(settings.ANGULAR_URL_REGEX, serve_static, { 'document_root': settings.ANGULAR_ROOT })
    ]


