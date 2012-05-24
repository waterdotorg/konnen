from django.contrib import admin

from sms_control.models import SmsControl, SmsControlLocale, SmsControlTrans

class SmsControlAdmin(admin.ModelAdmin):
    list_display = ('phrase', 'group', 'updated_date')
    search_fields = ('phrase', 'group')
    ordering = ('phrase',)

class SmsControlLocaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'language_code')
    search_fields = ('name', 'language_code')
    ordering = ('name',)

class SmsControlTransAdmin(admin.ModelAdmin):
    list_display = ('phrase_trans', 'updated_date')
    search_fields = ('phrase_trans',)
    ordering = ('phrase_trans',)

admin.site.register(SmsControl, SmsControlAdmin)
admin.site.register(SmsControlLocale, SmsControlLocaleAdmin)
admin.site.register(SmsControlTrans, SmsControlTransAdmin)