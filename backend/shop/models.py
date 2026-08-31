from django.db import models
from django.contrib.auth.models import User


class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    display_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    stripe_account_id = models.CharField(max_length=200, blank=True, null=True)
    # Customization options for artist public page
    header_image = models.ImageField(upload_to='artist_headers/', blank=True, null=True)
    theme_color = models.CharField(max_length=20, blank=True, default='#ffffff')
    custom_css = models.TextField(blank=True)
    # Social links (store as JSON: {"instagram": "", "twitter": "", "website": ""})
    social_links = models.JSONField(blank=True, null=True)
    # Presentation template and font choices
    template_choice = models.CharField(max_length=50, default='default')
    font_choice = models.CharField(max_length=50, blank=True, default='system')

    def __str__(self):
        return self.display_name or self.user.username


class Product(models.Model):
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price_cents = models.PositiveIntegerField(default=0)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    on_sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.artist})"


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='orders')
    buyer_email = models.EmailField(blank=True, null=True)
    # Link to Django user when available (optional)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    amount_cents = models.PositiveIntegerField(default=0)
    stripe_payment_intent = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)
    # Invoice storage URL (S3 or other)
    invoice_url = models.CharField(max_length=1000, blank=True, null=True)
    refunded = models.BooleanField(default=False)
    refunded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.product} ({self.amount_cents/100:.2f} EUR)"
