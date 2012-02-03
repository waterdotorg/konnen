from django.contrib import admin

from custom.models import Location

class LocationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title', 'slug', 'published_date')
    search_fields = ('title', 'content')
    ordering = ('-published_date',)
    date_hierarchy = 'published_date'

admin.site.register(Location, LocationAdmin)