from django.contrib import admin

from custom.models import Location, LocationSubscription, LocationPost, \
    WaterSourceType, Community, Provider, LocationPostReporterRemarks, LocationPostNotificationLog, \
    LocationSubscriptionNotificationLog

class LocationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'slug', 'published_date')
    search_fields = ('title', 'content')
    ordering = ('-published_date',)
    date_hierarchy = 'published_date'

class LocationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'email_subscription', 'phone_subscription', 'last_email_daily_date', 'last_email_weekly_date')
    search_fields = ('user', 'location__title')
    ordering = ('-created_date',)
    date_hierarchy = 'created_date'

class LocationPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'published_date')
    search_fields = ('title', 'content')
    ordering = ('-published_date',)
    date_hierarchy = 'published_date'

class WaterSourceTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date')
    search_fields = ('title',)
    ordering = ('title',)

class CommunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date')
    search_fields = ('title',)
    ordering = ('title',)

class ProviderAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date')
    search_fields = ('title',)
    ordering = ('title',)

class LocationPostReporterRemarksAdmin(admin.ModelAdmin):
    list_display = ('code', 'text', 'created_date')
    search_fields = ('code', 'text')
    ordering = ('code',)

class LocationPostNotificationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'location_post', 'notification_type', 'created_date')
    search_fields = ('user', 'location_post', 'notification_type')
    ordering = ('-created_date',)
    date_hierarchy = 'created_date'

class LocationSubscriptionNotificationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'location_subscription', 'notification_type', 'created_date')
    search_fields = ('user', 'location_subscription', 'notification_type')
    ordering = ('-created_date',)
    date_hierarchy = 'created_date'

admin.site.register(Location, LocationAdmin)
admin.site.register(LocationSubscription, LocationSubscriptionAdmin)
admin.site.register(LocationPost, LocationPostAdmin)
admin.site.register(WaterSourceType, WaterSourceTypeAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(LocationPostReporterRemarks, LocationPostReporterRemarksAdmin)
admin.site.register(LocationPostNotificationLog, LocationPostNotificationLogAdmin)
admin.site.register(LocationSubscriptionNotificationLog, LocationSubscriptionNotificationLogAdmin)