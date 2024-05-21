from django.contrib import admin

from distances.models import Distance


@admin.register(Distance)
class DistanceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'distance'
    )
    fieldsets = (
        (None, {
            'fields': (
                'distance',
                'restaurant',
                'order_address',
                'created_at',
                'updated_at',
            )
        }),
    )
    autocomplete_fields = ['restaurant']
    readonly_fields = ('created_at', 'updated_at')
