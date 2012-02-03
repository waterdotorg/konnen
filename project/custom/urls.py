from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('project.custom.views',
    url(r'^location/(?P<slug>[-\w]+)/$', 'location', name='location'),
)