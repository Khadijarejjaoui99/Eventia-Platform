from django.contrib import admin
from .models import Event, Venue, Vendor

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'location', 'date', 'price', 'rating')
    list_filter = ('category', 'location', 'date')
    search_fields = ('title', 'description', 'location')

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'city', 'capacity', 'price_start', 'price_end')
    list_filter = ('city', 'category', 'wifi', 'parking', 'catering', 'accessible')
    search_fields = ('name', 'city', 'category', 'address')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'location', 'rating', 'price',)

