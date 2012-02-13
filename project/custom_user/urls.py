from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('project.custom_user.views',
    url(r'^settings/$', 'settings_account', name='settings'),
    url(r'^settings/account/$', 'settings_account', name='settings_account'),
    url(r'^settings/remove-profile-image/$', 'settings_remove_profile_image', name='settings_remove_profile_image'),
    url(r'^member/(?P<username>[a-zA-Z0-9\-_\+\$@\.]+)/$', 'member_account', name='member_account'),
)