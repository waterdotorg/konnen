import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.dispatch import receiver

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

    def remove_profile_images(self):
        if self.image:
            user_profile_pic_path = settings.MEDIA_ROOT + '/profile-images/' + str(self.user.id)
            if os.path.isdir(user_profile_pic_path):
                    shutil.rmtree(user_profile_pic_path)
            self.image = ''
            self.save()

@receiver(user_logged_in)
def user_logged_in_signal(sender, request, user, **kwargs):
    try:
        profile = request.user.get_profile()
    except Profile.DoesNotExist:
        # opportunistically add profiles
        profile = Profile(user=request.user)
        profile.save()