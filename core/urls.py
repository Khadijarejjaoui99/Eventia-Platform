from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events, name='events'),
    path('venues/', views.venues, name='venues'),
    path('vendors/', views.vendors, name='vendors'),
    path("login/", views.user_login, name="login"),
    path('register/', views.register, name='register'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

    path('venue/<int:venue_id>/', views.venue_detail, name='venue_detail'),

    path('vendor/<int:vendor_id>/', views.vendor_detail, name='vendor_detail'),

    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/<int:user_id>/', views.profile, name='profile'),

    path('my_events/', views.my_events, name='my_events'),
    path('my_ticket/', views.my_ticket, name='my_ticket'),

    path('logout/', views.user_logout, name='logout'),

    path('editprofile/', views.editprofile, name='editprofile'),
    path('organizer/event/<int:event_id>/attendees/', views.event_attendees, name='event_attendees'),

    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('event/<int:event_id>/register/', views.register_ticket, name='register_event'),
    path('dashboard/organizer/', views.organizer, name='organizer'),
    path('dashboard/venue_owner/', views.manage_venues, name='manage_venues'),

    path('venue/create/', views.add_venue, name='create_venue'),

    path('venues/<int:venue_id>/edit/', views.edit_venue, name='edit_venue'),

    # Delete Vendor
    path('venues/<int:venue_id>/delete/', views.delete_venue, name='delete_venue'),

    path('dashboard/vendor/', views.manage_vendors, name='manage_vendors'),

    path('vendors/create/', views.create_vendor, name='create_vendor'),

    path('vendors/<int:vendor_id>/edit/', views.edit_vendor, name='edit_vendor'),

    # Delete Vendor
    path('vendors/<int:vendor_id>/delete/', views.delete_vendor, name='delete_vendor'),

    path('dashboard/manage_events', views.manage_events, name='manage_events'),

    path('dashboard/organizer/manage-events/', views.manage_events, name='manage_events'),
    path('dashboard/organizer/create-event/', views.create_event, name='create_event'),
    path("events/<int:event_id>/edit/", views.edit_event, name="edit_event"),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),


    path('analytics/', views.analytics, name='analytics'),
]