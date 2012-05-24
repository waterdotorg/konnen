from django.contrib import admin

from custom.models import Location, LocationSubscription, LocationPost, \
    WaterSourceType, Community, Provider, LocationPostReporterRemarks

class LocationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'slug', 'published_date')
    search_fields = ('title', 'content')
    ordering = ('-published_date',)
    date_hierarchy = 'published_date'

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

admin.site.register(Location, LocationAdmin)
admin.site.register(LocationSubscription)
admin.site.register(LocationPost, LocationPostAdmin)
admin.site.register(WaterSourceType, WaterSourceTypeAdmin)
admin.site.register(Community, CommunityAdmin)
admin.site.register(Provider, ProviderAdmin)
admin.site.register(LocationPostReporterRemarks, LocationPostReporterRemarksAdmin)