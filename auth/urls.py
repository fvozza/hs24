from django.conf.urls import patterns, include, url

urlpatterns = patterns('auth.views',
    url(r'^authorize', 'authorize'),
    url(r'^authorized', 'authorize'),
    url(r'^unauthorize', 'unauthorize'),
    url(r'^testis24$', 'testIS24'),
    url(r'^oauth_callback', 'oauth_callback'),
)