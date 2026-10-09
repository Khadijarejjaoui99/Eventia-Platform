from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import qrcode
from io import BytesIO
from django.core.files import File

class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    attendees = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    host_name = models.CharField(max_length=200, null=True, blank=True)
    host_description = models.TextField(null=True, blank=True)
    host_image = models.ImageField(upload_to='core/images/', null=True, blank=True)
    venue_name = models.CharField(max_length=200, null=True, blank=True)
    venue_address = models.CharField(max_length=300, null=True, blank=True)
    wifi = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    restaurant = models.BooleanField(default=False)
    accessible = models.BooleanField(default=False)
    image = models.ImageField(upload_to='core/images/', default='core/images/1.jpg')


class Venue(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='venues', null=True, blank=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    description = models.TextField()

    capacity = models.IntegerField()
    event_duration = models.CharField(max_length=50)
    size = models.IntegerField()


    # Pricing
    price_start = models.DecimalField(max_digits=10, decimal_places=2)
    price_end = models.DecimalField(max_digits=10, decimal_places=2)

    # Contact Information
    phone = models.CharField(max_length=50)
    email = models.EmailField()

    # Amenities (Boolean fields for icons)
    wifi = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    catering = models.BooleanField(default=False)
    accessible = models.BooleanField(default=False)
    sound_system = models.BooleanField(default=False)
    av_equipment = models.BooleanField(default=False)

    rating = models.DecimalField(max_digits=3, decimal_places=1)

    # Gallery
    image1 = models.ImageField(upload_to='core/images/venues')
    image2 = models.ImageField(upload_to='core/images/venues',blank=True, null=True)
    image3 = models.ImageField(upload_to='core/images/venues',blank=True, null=True)
    image4 = models.ImageField(upload_to='core/images/venues',blank=True, null=True)

    def __str__(self):
        return self.name



class Vendor(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food & Catering'),
        ('decoration', 'Event Decoration'),
        ('photography', 'Photography'),
        ('music', 'Music & Entertainment'),
        ('transport', 'Transportation'),
        ('tech', 'Event Technology'),
        ('staff', 'Event Staff'),
        ('other', 'Other Services'),
    ]
    AVAILABILITY_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]
    Vendor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    description = models.TextField()

    experience_years = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    image = models.ImageField(upload_to='core/images/vendors', blank=True, null=True)

    specialties = models.CharField(max_length=500, blank=True)

    team_size = models.IntegerField(default=1)
    price_range = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=300, blank=True)

    mon_status = models.CharField(max_length=12, choices=AVAILABILITY_CHOICES, default='Unavailable')
    tue_status = models.CharField(max_length=12, choices=AVAILABILITY_CHOICES, default='Unavailable')
    wed_status = models.CharField(max_length=12, choices=AVAILABILITY_CHOICES, default='Unavailable')
    thu_status = models.CharField(max_length=12, choices=AVAILABILITY_CHOICES, default='Unavailable')
    fri_status = models.CharField(max_length=12, choices=AVAILABILITY_CHOICES, default='Unavailable')
    sat_status = models.CharField(max_length=12, choices=AVAILABILITY_CHOICES, default='Unavailable')
    sun_status = models.CharField(max_length=12, choices=AVAILABILITY_CHOICES, default='Unavailable')

    # ---- Portfolio (Up to 6 images) ----
    portfolio1 = models.ImageField(upload_to='core/images/vendors/', blank=True, null=True)
    portfolio2 = models.ImageField(upload_to='core/images/vendors/', blank=True, null=True)
    portfolio3 = models.ImageField(upload_to='core/images/vendors/', blank=True, null=True)
    portfolio4 = models.ImageField(upload_to='core/images/vendors/', blank=True, null=True)
    portfolio5 = models.ImageField(upload_to='core/images/vendors/', blank=True, null=True)
    portfolio6 = models.ImageField(upload_to='core/images/vendors/', blank=True, null=True)

    service1 = models.CharField(max_length=100, blank=True)
    service2 = models.CharField(max_length=100, blank=True)
    service3 = models.CharField(max_length=100, blank=True)
    service4 = models.CharField(max_length=100, blank=True)
    service5 = models.CharField(max_length=100, blank=True)
    service6 = models.CharField(max_length=100, blank=True)
    service7 = models.CharField(max_length=100, blank=True)

    def services_list(self):
        return [s for s in [
            self.service1,
            self.service2,
            self.service3,
            self.service4,
            self.service5,
            self.service6,
            self.service7
        ] if s]

    def portfolio_images(self):
        return [
            img for img in [
                self.portfolio1,
                self.portfolio2,
                self.portfolio3,
                self.portfolio4,
                self.portfolio5,
                self.portfolio6,
            ] if img
        ]

    def __str__(self):
        return self.name




class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('attendee', 'Attendee'),
        ('organizer', 'Event Organizer'),
        ('vendor', 'Vendor'),
        ('Venue_owner', 'Venue Owner'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')  # NEW FIELD

    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    languages = models.CharField(max_length=200, blank=True, null=True)

    instagram = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    twitter = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)

    interests = models.CharField(max_length=100, blank=True, null=True)

    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"



@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='tickets/', blank=True)

    def save(self, *args, **kwargs):
        # Generate QR code automatically
        qr_data = f"Ticket for {self.user.get_full_name()} | Event: {self.event.title} | Email: {self.user.email}"
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Save QR code image
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        filename = f'ticket_{self.user.id}_{self.event.id}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        super().save(*args, **kwargs)