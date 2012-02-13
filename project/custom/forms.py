from django import forms
from custom.models import Location, LocationSubscription

class LocationSubscriptionForm(forms.Form):
    user_id = forms.CharField(widget=forms.HiddenInput)
    location_id = forms.CharField(widget=forms.HiddenInput)
    email_subscription = forms.ChoiceField(
        choices=LocationSubscription.EMAIL_FREQ_CHOICES,
        initial=LocationSubscription.EMAIL_DAILY_FREQ,
    )
    phone_subscription = forms.BooleanField(initial=True, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        return super(LocationSubscriptionForm, self).__init__(*args, **kwargs)

    def clean_user_id(self, *args, **kwargs):
        if self.user.id != int(self.cleaned_data['user_id']):
            raise forms.ValidationError('Invalid request. You can only update your subscriptions.')
        return self.cleaned_data['user_id']

    def clean_location_id(self, *args, **kwargs):
        try:
            Location.objects.get(id=self.cleaned_data['location_id'])
        except:
            raise forms.ValidationError('Invalid location submitted.')
        return self.cleaned_data['location_id']

    def clean_email_subscription(self, *args, **kwargs):
            if not self.user.email:
                raise forms.ValidationError('Please add your email address on the settings page before subscribing to alerts.')
            return self.cleaned_data['email_subscription']

    def clean_phone_subscription(self, *args, **kwargs):
        if not self.user.get_profile().mobile:
            raise forms.ValidationError('Please add your mobile number on the settings page before subscribing to SMS alerts.')
        return self.cleaned_data['phone_subscription']