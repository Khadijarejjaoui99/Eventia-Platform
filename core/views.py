from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Venue, Vendor, UserProfile, Ticket
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date
from django.db.models import Count, Sum

def home(request):
    return render(request, 'core/home.html')

def events(request):
    events = Event.objects.all().order_by('-id')
    return render(request, 'core/events.html', {'events': events})


def venues(request):
    venues = Venue.objects.all().order_by('-id')
    return render(request, 'core/venues.html', {'venues': venues})

def vendors(request):
    vendors = Vendor.objects.all().order_by('-id')
    return render(request, 'core/vendors.html', {'vendors': vendors})

def home(request):
    featured_events = []

    health_event = Event.objects.filter(category='sports').order_by('-id').first()
    education_event = Event.objects.filter(category='business').order_by('-id').first()
    technology_event = Event.objects.filter(category='Technology').order_by('-id').first()

    # Add events if they exist
    if health_event:
        featured_events.append(health_event)
    if education_event:
        featured_events.append(education_event)
    if technology_event:
        featured_events.append(technology_event)

    return render(request, 'core/home.html', {'featured_events': featured_events})

def organizer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.userprofile.role != 'organizer':
            messages.error(request, "Access denied.")
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
def user_login(request):
    if request.user.is_authenticated:
        if request.user.userprofile.role == 'organizer':
            return redirect('organizer')
        elif request.user.userprofile.role == 'vendor':
            return redirect('manage_vendors')
        return redirect('user_dashboard')

    # AJAX Login Request
    if request.method == "POST" and request.headers.get("HX-Request"):
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')

        errors = []

        if not email or not password:
            errors.append("Please fill in all fields.")

        user = authenticate(username=email, password=password)

        if not user:
            errors.append("Invalid email or password.")

        if errors:
            return JsonResponse({"status": "error", "errors": errors})

        login(request, user)

        role = user.userprofile.role
        if role == 'organizer':
            redirect_url = '/dashboard/organizer/'
        elif role == 'vendor':
            redirect_url = '/dashboard/vendor/'
        elif role == 'venue_owner':
            redirect_url = '/dashboard/venue_owner/'
        else:
            redirect_url = '/dashboard/'

        return JsonResponse({"status": "success", "redirect_url": redirect_url})


    return render(request, 'core/login.html')

def vendor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.userprofile.role != 'vendor':
            messages.error(request, "Access denied. Vendor account required.")
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def register(request):

    # logged-in user cannot access register page
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == "POST" and request.headers.get("HX-Request"):  # if AJAX/HTMX request
        first_name = request.POST.get('firstName', '').strip()
        last_name = request.POST.get('lastName', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirmPassword', '')
        role = request.POST.get('userRole', '')

        errors = []

        if not first_name or not last_name or not email or not password or not confirm_password:
            errors.append("Please fill in all fields.")

        if password != confirm_password:
            errors.append("Passwords do not match.")


        if User.objects.filter(username=email).exists():
            errors.append("Email already registered.")

        if errors:
            return JsonResponse({"status": "error", "errors": errors})

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Assign role
        profile = user.userprofile
        profile.role = role
        profile.save()

        return JsonResponse({"status": "success"})

    return render(request, 'core/register.html')


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # If user is logged in, fetch their tickets
    tickets = None
    if request.user.is_authenticated:
        tickets = Ticket.objects.filter(event=event, user=request.user)

    return render(request, 'core/event.html', {
        'event': event,
        'tickets': tickets,
    })

def venue_detail(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    return render(request, 'core/venue.html', {'venue': venue})


def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    return render(request, 'core/vendor.html', {'vendor': vendor})

@login_required
def user_logout(request):
        storage = get_messages(request)
        for _ in storage:
            pass
        logout(request)
        return redirect('login')

@login_required
def user_dashboard(request):
    if request.user.userprofile.role == 'organizer':
        return redirect('organizer')
    elif request.user.userprofile.role == 'vendor':
        return redirect('manage_vendors')
    elif request.user.userprofile.role == 'venue_owner':
        return redirect('manage_venues')

    user = request.user
    upcoming_tickets = Ticket.objects.filter(user=user)

    upcoming_events = [ticket.event for ticket in upcoming_tickets][:3]

    context = {
        "user": user,
        "events": upcoming_events,
        "tickets": upcoming_tickets
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    return render(request, 'core/profile.html', {
        "user": user,
        "user_profile": user_profile
    })



@login_required
def my_ticket(request):
    tickets = Ticket.objects.filter(user=request.user).select_related('event')
    return render(request, 'core/myticket.html', {'tickets': tickets})

def venue_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.userprofile.role != 'venue_owner':
            messages.error(request, "Access denied. Venue owner account required.")
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
@login_required
@venue_owner_required
def add_venue(request):
    if request.method == "POST":
        venue = Venue.objects.create(
            owner=request.user,
            name=request.POST.get('name'),
            category=request.POST.get('category'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            description=request.POST.get('description'),
            capacity=request.POST.get('capacity'),
            event_duration=request.POST.get('event_duration'),
            size=request.POST.get('size'),
            price_start=request.POST.get('price_start'),
            price_end=request.POST.get('price_end'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            rating=request.POST.get('rating') or 0,
            wifi='wifi' in request.POST,
            parking='parking' in request.POST,
            catering='catering' in request.POST,
            accessible='accessible' in request.POST,
            sound_system='sound_system' in request.POST,
            av_equipment='av_equipment' in request.POST,
            image1=request.FILES.get('image1'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),
            image4=request.FILES.get('image4'),
        )
        return redirect('manage_venues')

    return render(request, 'core/add_venue.html')

@login_required
@venue_owner_required
def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id, owner=request.user)
    venue.delete()
    return redirect('manage_venues')

@login_required
@venue_owner_required
def edit_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id, owner=request.user)

    if request.method == "POST":
        venue.name = request.POST.get('name')
        venue.category = request.POST.get('category')
        venue.address = request.POST.get('address')
        venue.city = request.POST.get('city')
        venue.description = request.POST.get('description')
        venue.capacity = request.POST.get('capacity')
        venue.event_duration = request.POST.get('event_duration')
        venue.size = request.POST.get('size')
        venue.price_start = request.POST.get('price_start')
        venue.price_end = request.POST.get('price_end')
        venue.phone = request.POST.get('phone')
        venue.email = request.POST.get('email')
        venue.rating = request.POST.get('rating') or 0

        # Amenities
        venue.wifi = 'wifi' in request.POST
        venue.parking = 'parking' in request.POST
        venue.catering = 'catering' in request.POST
        venue.accessible = 'accessible' in request.POST
        venue.sound_system = 'sound_system' in request.POST
        venue.av_equipment = 'av_equipment' in request.POST

        # Images (update only if new files are uploaded)
        for i in range(1, 6):
            file = request.FILES.get(f'image{i}')
            if file:
                setattr(venue, f'image{i}', file)

        venue.save()
        return redirect('manage_venues')

    return render(request, 'core/edit_venue.html', {'venue': venue})

@login_required
@venue_owner_required
def my_venues(request):
    venues = Venue.objects.filter(owner=request.user)
    return render(request, 'core/my_venues.html', {'venues': venues})


@login_required
def add_vendor(request):
    if request.method == "POST":
        Vendor.objects.create(
            owner=request.user,
            name=request.POST.get('name'),
            category=request.POST.get('category'),
            location=request.POST.get('location'),
            description=request.POST.get('description'),
            experience_years=request.POST.get('experience_years'),
            price=request.POST.get('price'),
            rating=request.POST.get('rating'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            image=request.FILES.get('image'),
        )
        return redirect('my_vendors')

    return render(request, 'core/add_vendor.html')

@login_required
@vendor_required
def manage_vendors(request):
    vendors = Vendor.objects.filter(Vendor=request.user)
    return render(request, 'core/edit_vendor.html', {'vendors': vendors})

@login_required
@venue_owner_required
def manage_venues(request):
    venues = Venue.objects.filter(owner=request.user)
    return render(request, 'core/edit_venue.html', {'venues': venues})

@login_required
@vendor_required
def create_vendor(request):
    if request.method == "POST":
        name = request.POST.get('name')
        category = request.POST.get('category')
        location = request.POST.get('location')
        description = request.POST.get('description')
        experience_years = request.POST.get('experience_years', 0)
        price = request.POST.get('price', 0)
        specialties = request.POST.get('specialties', '')
        team_size = request.POST.get('team_size', 1)
        price_range = request.POST.get('price_range', '')
        rating = request.POST.get('rating', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')

        # Availability
        mon_status = request.POST.get('mon_status', 'Unavailable')
        tue_status = request.POST.get('tue_status', 'Unavailable')
        wed_status = request.POST.get('wed_status', 'Unavailable')
        thu_status = request.POST.get('thu_status', 'Unavailable')
        fri_status = request.POST.get('fri_status', 'Unavailable')
        sat_status = request.POST.get('sat_status', 'Unavailable')
        sun_status = request.POST.get('sun_status', 'Unavailable')

        # Services
        service1 = request.POST.get('service1', '')
        service2 = request.POST.get('service2', '')
        service3 = request.POST.get('service3', '')
        service4 = request.POST.get('service4', '')
        service5 = request.POST.get('service5', '')
        service6 = request.POST.get('service6', '')
        service7 = request.POST.get('service7', '')

        # Images
        image = request.FILES.get('image')
        portfolio1 = request.FILES.get('portfolio1')
        portfolio2 = request.FILES.get('portfolio2')
        portfolio3 = request.FILES.get('portfolio3')
        portfolio4 = request.FILES.get('portfolio4')
        portfolio5 = request.FILES.get('portfolio5')
        portfolio6 = request.FILES.get('portfolio6')

        Vendor.objects.create(
            Vendor=request.user,
            name=name,
            category=category,
            location=location,
            description=description,
            experience_years=experience_years,
            price=price,
            specialties=specialties,
            team_size=team_size,
            price_range=price_range,
            phone=phone,
            rating=rating,
            email=email,
            address=address,
            mon_status=mon_status,
            tue_status=tue_status,
            wed_status=wed_status,
            thu_status=thu_status,
            fri_status=fri_status,
            sat_status=sat_status,
            sun_status=sun_status,
            service1=service1,
            service2=service2,
            service3=service3,
            service4=service4,
            service5=service5,
            service6=service6,
            service7=service7,
            image=image,
            portfolio1=portfolio1,
            portfolio2=portfolio2,
            portfolio3=portfolio3,
            portfolio4=portfolio4,
            portfolio5=portfolio5,
            portfolio6=portfolio6,
        )
        return redirect('manage_vendors')

    return render(request, 'core/create_vendor.html')

@login_required
@vendor_required
def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id, Vendor=request.user)  # make sure user owns it
    if request.method == "POST":
        vendor.name = request.POST.get('name')
        vendor.category = request.POST.get('category')
        vendor.location = request.POST.get('location')
        vendor.description = request.POST.get('description')
        vendor.experience_years = request.POST.get('experience_years', 0)
        vendor.price = request.POST.get('price', 0)
        vendor.specialties = request.POST.get('specialties', '')
        vendor.team_size = request.POST.get('team_size', 1)
        vendor.price_range = request.POST.get('price_range', '')
        vendor.rating = request.POST.get('rating', '')
        vendor.phone = request.POST.get('phone', '')
        vendor.email = request.POST.get('email', '')
        vendor.address = request.POST.get('address', '')

        # Availability
        vendor.mon_status = request.POST.get('mon_status', 'Unavailable')
        vendor.tue_status = request.POST.get('tue_status', 'Unavailable')
        vendor.wed_status = request.POST.get('wed_status', 'Unavailable')
        vendor.thu_status = request.POST.get('thu_status', 'Unavailable')
        vendor.fri_status = request.POST.get('fri_status', 'Unavailable')
        vendor.sat_status = request.POST.get('sat_status', 'Unavailable')
        vendor.sun_status = request.POST.get('sun_status', 'Unavailable')

        # Services
        vendor.service1 = request.POST.get('service1', '')
        vendor.service2 = request.POST.get('service2', '')
        vendor.service3 = request.POST.get('service3', '')
        vendor.service4 = request.POST.get('service4', '')
        vendor.service5 = request.POST.get('service5', '')
        vendor.service6 = request.POST.get('service6', '')
        vendor.service7 = request.POST.get('service7', '')

        # Images (update only if new ones are uploaded)
        if request.FILES.get('image'):
            vendor.image = request.FILES.get('image')
        if request.FILES.get('portfolio1'):
            vendor.portfolio1 = request.FILES.get('portfolio1')
        if request.FILES.get('portfolio2'):
            vendor.portfolio2 = request.FILES.get('portfolio2')
        if request.FILES.get('portfolio3'):
            vendor.portfolio3 = request.FILES.get('portfolio3')
        if request.FILES.get('portfolio4'):
            vendor.portfolio4 = request.FILES.get('portfolio4')
        if request.FILES.get('portfolio5'):
            vendor.portfolio5 = request.FILES.get('portfolio5')
        if request.FILES.get('portfolio6'):
            vendor.portfolio6 = request.FILES.get('portfolio6')

        # Save the updated vendor
        vendor.save()

        return redirect('manage_vendors')

    return render(request, 'core/edit_vendor.html', {'vendor': vendor})


@login_required
@vendor_required
def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.delete()
    return redirect('manage_vendors')


@login_required
@vendor_required
def my_vendors(request):
    vendors = Vendor.objects.filter(owner=request.user)
    return render(request, 'core/my_vendors.html', {'vendors': vendors})


# views.py
@login_required
def editprofile(request):
    user = request.user
    user_profile = request.user.userprofile
    interest_choices = ["Music", "Technology", "Art", "Sports", "Reading",
                        "Travel", "Gaming", "Food", "Movies", "Fitness"]

    if request.method == "POST":
        # Update User fields
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.save()

        # Update profile fields
        user_profile.bio = request.POST.get("bio") or ""
        user_profile.location = request.POST.get("location") or ""
        user_profile.languages = request.POST.get("languages") or ""

        # Update interest (single choice)
        user_profile.interests = request.POST.get("interest") or ""

        # Social links
        user_profile.instagram = request.POST.get("instagram")
        user_profile.facebook = request.POST.get("facebook")
        user_profile.twitter = request.POST.get("twitter")
        user_profile.linkedin = request.POST.get("linkedin")

        # Profile photo
        if "profile_photo" in request.FILES:
            user_profile.profile_image = request.FILES["profile_photo"]

        user_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile", user_id=user.id)

    return render(request, 'core/editprofile.html', {
        "user": user,
        "profile": user_profile,
        "interest_choices": interest_choices
    })


@login_required
def register_ticket(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if user already registered
    if Ticket.objects.filter(event=event, user=request.user).exists():
        messages.info(request, "You have already registered for this event.")
        return redirect('my_events')

    ticket = Ticket.objects.create(event=event, user=request.user)
    messages.success(request, "Registration successful! Your ticket has been generated.")
    return redirect('ticket_detail', ticket_id=ticket.id)

def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    return render(request, 'core/ticket_detail.html', {'ticket': ticket})


@login_required
def my_events(request):
    registered_events = Ticket.objects.filter(user=request.user).select_related('event')
    return render(request, 'core/myevents.html', {'registered_events': registered_events})

@login_required
@organizer_required
def organizer(request):
    events = Event.objects.filter(organizer=request.user)[:3]
    all_events = Event.objects.filter(organizer=request.user)

    recent_registrations = Ticket.objects.filter(event__in=all_events) \
        .select_related('user', 'event') \
        .order_by('-created_at')[:4]

    return render(request, 'core/organizer_dashboard.html', {
        "events": events,
        'recent_registrations': recent_registrations,
    })

@login_required
@organizer_required
def event_attendees(request, event_id):
    event = get_object_or_404(Event, id=event_id, organizer=request.user)
    tickets = Ticket.objects.filter(event=event).select_related('user')

    attendees = []
    for ticket in tickets:
        attendees.append({
            "ticket_id": ticket.id,
            "name": f"{ticket.user.first_name} {ticket.user.last_name}",
            "email": ticket.user.email,
        })

    return JsonResponse({
        "event_title": event.title,
        "total_attendees": tickets.count(),
        "attendees": attendees
    })



@login_required
@organizer_required
def manage_events(request):
    events = Event.objects.filter(organizer=request.user).order_by('-date')

    events_with_tickets = events.annotate(tickets_sold=Count('ticket'))

    for event in events_with_tickets:
        event.revenue = event.price * event.tickets_sold

    return render(request, 'core/manage_events.html', {'events': events_with_tickets})

@login_required
@organizer_required
def create_event(request):
    if request.method == "POST":
        title = request.POST.get('title')
        category = request.POST.get('category', '')
        description = request.POST.get('description', '')
        location = request.POST.get('location', '')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time') or None
        end_time = request.POST.get('end_time') or None
        attendees = request.POST.get('attendees') or 0
        price = request.POST.get('price') or 0
        rating = request.POST.get('rating') or None
        host_name = request.POST.get('host_name', '')
        host_description = request.POST.get('host_description', '')
        venue_name = request.POST.get('venue_name', '')
        venue_address = request.POST.get('venue_address', '')
        wifi = True if request.POST.get('wifi') else False
        parking = True if request.POST.get('parking') else False
        restaurant = True if request.POST.get('restaurant') else False
        accessible = True if request.POST.get('accessible') else False
        image = request.FILES.get('image') or 'core/images/1.jpg'
        host_image = request.FILES.get('host_image') or None

        # Create the event
        Event.objects.create(
            organizer=request.user,
            title=title,
            category=category,
            description=description,
            location=location,
            date=date,
            start_time=start_time,
            end_time=end_time,
            attendees=attendees,
            price=price,
            rating=rating,
            host_name=host_name,
            host_description=host_description,
            host_image=host_image,
            venue_name=venue_name,
            venue_address=venue_address,
            wifi=wifi,
            parking=parking,
            restaurant=restaurant,
            accessible=accessible,
            image=image,
        )

        return redirect('manage_events')  # safely redirect
    else:
        return redirect('manage_events')

@login_required
@organizer_required
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id, organizer=request.user)
    event.delete()
    return redirect('manage_events')

@login_required
@organizer_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id,  organizer=request.user)

    if request.method == "POST":
        event.title = request.POST.get("title")
        event.category = request.POST.get("category")
        event.description = request.POST.get("description")
        event.location = request.POST.get("location")
        event.date = request.POST.get("date")
        event.start_time = request.POST.get("start_time")
        event.end_time = request.POST.get("end_time")

        event.attendees = request.POST.get("attendees")
        event.price = request.POST.get("price")
        event.rating = request.POST.get("rating")

        event.host_name = request.POST.get("host_name")
        event.host_description = request.POST.get("host_description")

        event.venue_name = request.POST.get("venue_name")
        event.venue_address = request.POST.get("venue_address")

        event.wifi = "wifi" in request.POST
        event.parking = "parking" in request.POST
        event.restaurant = "restaurant" in request.POST
        event.accessible = "accessible" in request.POST

        if "image" in request.FILES:
            event.image = request.FILES["image"]

        if "host_image" in request.FILES:
            event.host_image = request.FILES["host_image"]

        event.save()
        return redirect("manage_events")


@login_required
def register_vendor(request):
    if request.method == "POST":
        Vendor.objects.create(
            name=request.POST.get('name'),
            category=request.POST.get('category'),
            location=request.POST.get('location'),
            description=request.POST.get('description'),
            experience_years=request.POST.get('experience_years', 0),
            price=request.POST.get('price', 0),
            rating=request.POST.get('rating', 0),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            image=request.FILES.get('image'),
        )
        messages.success(request, "Vendor registered successfully.")
        return redirect('vendors')

    return render(request, 'core/register_vendor.html')

@login_required
def register_venue(request):
    if request.method == "POST":
        Venue.objects.create(
            name=request.POST.get('name'),
            category=request.POST.get('category'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            description=request.POST.get('description'),
            capacity=request.POST.get('capacity'),
            event_duration=request.POST.get('event_duration'),
            size=request.POST.get('size'),
            price_start=request.POST.get('price_start'),
            price_end=request.POST.get('price_end'),
            phone=request.POST.get('phone'),
            email=request.POST.get('email'),
            wifi=bool(request.POST.get('wifi')),
            parking=bool(request.POST.get('parking')),
            catering=bool(request.POST.get('catering')),
            accessible=bool(request.POST.get('accessible')),
            sound_system=bool(request.POST.get('sound_system')),
            av_equipment=bool(request.POST.get('av_equipment')),
            rating=request.POST.get('rating', 0),
            image1=request.FILES.get('image1'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),
            image4=request.FILES.get('image4'),
        )
        messages.success(request, "Venue registered successfully.")
        return redirect('venues')

    return render(request, 'core/register_venue.html')



@login_required
@organizer_required
def analytics(request):
    user = request.user

    # Only organizers can access analytics
    if user.userprofile.role != 'organizer':
        return render(request, 'core/analytics.html', {'error': 'You are not an organizer!'})

    # Get organizer's events
    events = Event.objects.filter(organizer=user)

    total_events = events.count()

    # Annotate each event with tickets sold
    events_with_tickets = events.annotate(tickets_sold=Count('ticket'))

    # Total registrations / attendees
    total_registrations = Ticket.objects.filter(event__organizer=user).count()
    total_attendees_field = total_registrations or 0

    # Total revenue using annotated tickets_sold
    total_revenue = sum(event.price * event.tickets_sold for event in events_with_tickets)

    context = {
        'events': events_with_tickets,          # For "Tickets Sold Per Event" chart
        'total_events': total_events,
        'total_attendees_field': total_attendees_field,
        'total_registrations': total_registrations,
        'total_revenue': total_revenue,
    }

    return render(request, 'core/analytics.html', context)

