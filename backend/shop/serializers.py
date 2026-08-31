from rest_framework import serializers
from .models import ArtistProfile, Product, Order
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'artist', 'title', 'description', 'price_cents', 'stock', 'image', 'image_url', 'is_active', 'is_new', 'on_sale', 'created_at']
        read_only_fields = ('artist',)

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ArtistProfileSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = ArtistProfile
        fields = ['id', 'user', 'display_name', 'bio', 'stripe_account_id', 'header_image', 'theme_color', 'custom_css', 'social_links', 'template_choice', 'font_choice', 'products']


class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['id', 'product', 'buyer_email', 'user_email', 'amount_cents', 'stripe_payment_intent', 'invoice_url', 'created_at', 'fulfilled', 'refunded', 'refunded_at']

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None
