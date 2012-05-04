from django.contrib import admin

from sms.models import Sms

class SmsAdmin(admin.ModelAdmin):
    list_display = ('from_number', 'to_number', 'message', 'sent_date')
    search_fields = ('from_number', 'to_number', 'message')
    ordering = ('-sent_date',)

admin.site.register(Sms, SmsAdmin)