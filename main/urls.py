from django.conf.urls import patterns, include, url
import django.contrib.auth

urlpatterns = patterns('main.views',
  url(r'^$', 'index'),
  url(r'^login_user$', 'login_user'),
)

# test urls
urlpatterns += patterns('main.is24',
  url(r'^is24_radius_search', 'is24_radius_search'),
  url(r'^settings', 'change_is24_settings'),
)

urlpatterns += (
  url(r'^login', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
	url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
)  