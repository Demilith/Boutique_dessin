from django.contrib import admin
from .models import ArtistProfile, Product
from .models import Order
import stripe
from django.conf import settings
from django.contrib import messages

@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user')
    readonly_fields = ('stripe_account_id',)
    fieldsets = (
        (None, {'fields': ('user', 'display_name', 'bio', 'header_image')}),
        ('Customization', {'fields': ('theme_color', 'custom_css', 'social_links', 'template_choice', 'font_choice')}),
        ('Stripe', {'fields': ('stripe_account_id',)}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'price_cents', 'stock', 'is_active', 'on_sale')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'buyer_email', 'amount_cents', 'fulfilled', 'created_at')
    list_filter = ('fulfilled',)
    actions = ['refund_order']

    def refund_order(self, request, queryset):
        for order in queryset:
            try:
                if order.stripe_payment_intent:
                    stripe.api_key = settings.STRIPE_SECRET_KEY
                    # attempt refund via payment_intent
                    stripe.Refund.create(payment_intent=order.stripe_payment_intent)
                    order.fulfilled = False
                    order.save()
                    self.message_user(request, f'Refund created for order {order.id}', level=messages.SUCCESS)
                else:
                    self.message_user(request, f'No payment intent for order {order.id}', level=messages.WARNING)
            except Exception as e:
                self.message_user(request, f'Failed to refund order {order.id}: {e}', level=messages.ERROR)
    refund_order.short_description = 'Refund selected orders via Stripe'
