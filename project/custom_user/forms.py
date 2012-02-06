import re

from django import forms
from django.contrib.auth.models import User

class SettingsAccountForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField(max_length=255, required=False)
    mobile = forms.CharField(max_length=20, required=False)
    content = forms.CharField(widget=forms.Textarea)
    image = forms.ImageField(label='Image', max_length=200, required=False)

    def __init__(self, user, data, files, *args, **kwargs):
        profile = user.get_profile()
        defaults = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'mobile': profile.mobile,
            'content': profile.content,
        }

        data_dict = dict(zip(data.keys(), data.values()))
        data_is_empty = not bool(data_dict)
        self.user = user
        defaults = defaults if data_is_empty else data
        return super(SettingsAccountForm, self).__init__(defaults, files, *args, **kwargs)

    def clean_username(self, *args, **kwargs):
        existing_users = User.objects.filter(username=self.cleaned_data['username'])
        if existing_users and existing_users[0].pk != self.user.pk:
            raise forms.ValidationError('The username %s is already registered.' % self.cleaned_data['username'])
        regex_username = re.search(r'[a-zA-Z0-9\-_\+\$@\.]+', self.cleaned_data['username'])
        if (self.cleaned_data['username'] != regex_username.group(0)):
            raise forms.ValidationError('Username field may only contain alpha-numeric characters, hypens or underscores.')
        return self.cleaned_data['username']

    def clean_email(self, *args, **kwargs):
        existing_users = User.objects.filter(email=self.cleaned_data['email']).exclude(pk=self.user.pk)
        if existing_users and self.cleaned_data['email']:
            raise forms.ValidationError('The email %s is already registered.' % self.cleaned_data['email'])
        return self.cleaned_data['email']

    def clean_image(self, *args, **kwargs):
        data = self.cleaned_data['image']
        # Limit uploaded images to 4096k
        if data and data.size > 4194304:
            raise forms.ValidationError('Image file size is over the allowed maximum.')
        return self.cleaned_data['image']

    def apply_to_user(self, files):
        user = self.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        profile = user.get_profile()
        profile.mobile = self.cleaned_data['mobile']
        profile.content = self.cleaned_data['content']

        if 'image' in files:
            # Remove the profile image folder for the user so we clear any
            # cached images
            profile.remove_profile_images()
            profile.image = files['image']
        profile.save()
        user.save()
        del user._profile_cache     # gotta do this to see results, unfortunately