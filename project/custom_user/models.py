from django.contrib.auth.models import User
from django.db import models

def get_profile_image_path(instance, filename):
    extension = filename.split('.')[-1]
    dir = "profile-images/%s/profile-image.%s" % (instance.user.id, extension)
    return dir

class Profile(models.Model):
    user = models.ForeignKey(User)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to=get_profile_image_path, max_length=256, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
            return u'%s' % self.user.get_full_name()