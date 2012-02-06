from django.contrib import admin

from custom_user.models import Profile

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('bio')
    ordering = ('-created_date',)

admin.site.register(Profile, ProfileAdmin)