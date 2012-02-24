from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('project.custom.views',
    url(r'^location/browse/$', 'location_browse', name='location_browse'),
    url(r'^location/subscribe/$', 'location_subscribe', name='location_subscribe'),
    url(r'^location/(?P<slug>[-\w]+)/$', 'location', name='location'),
    url(r'^homepage-kml/$', 'homepage_kml', name='homepage_kml'),
    url(r'^$', 'homepage', name='homepage'),
)