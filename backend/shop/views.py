import os
import stripe
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from .models import ArtistProfile, Product, Order
from .utils import generate_invoice_pdf, upload_buffer_to_s3
from django.utils import timezone
from .serializers import ArtistProfileSerializer, ProductSerializer
from .serializers import UserRegistrationSerializer, TokenPairSerializer
from rest_framework import serializers as drf_serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # artists can modify their own products/profiles
        user = request.user
        if hasattr(obj, 'artist'):
            return obj.artist.user == user
        if hasattr(obj, 'user'):
            return obj.user == user
        return False


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'artist_profile', None)
        if profile is None:
            raise drf_serializers.ValidationError('Artist profile required to create products')
        serializer.save(artist=profile)


class MyProductsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'artist_profile', None)
        if not profile:
            return Response({'detail': 'Artist profile not found.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductSerializer(profile.products.all(), many=True, context={'request': request})
        return Response(serializer.data)


class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'artist_profile', None)
        if not profile:
            return Response({'detail': 'Artist profile not found.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ArtistProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        profile = getattr(request.user, 'artist_profile', None)
        if not profile:
            return Response({'detail': 'Artist profile not found.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ArtistProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArtistProfileViewSet(viewsets.ModelViewSet):
    queryset = ArtistProfile.objects.all()
    serializer_class = ArtistProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreateStripeAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # create a Stripe Express account for the authenticated artist
        user = request.user
        profile = getattr(user, 'artist_profile', None)
        if not profile:
            return Response({'detail': 'Artist profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            account = stripe.Account.create(type='express', country='FR', email=user.email)
            profile.stripe_account_id = account['id']
            profile.save()
            return Response({'stripe_account_id': account['id']})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # create artist profile
            ArtistProfile.objects.create(user=user, display_name=user.username)
            refresh = RefreshToken.for_user(user)
            token_ser = TokenPairSerializer({'access': str(refresh.access_token), 'refresh': str(refresh)})
            return Response(token_ser.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateStripeAccountLinkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # create an account link so the artist can complete onboarding
        user = request.user
        profile = getattr(user, 'artist_profile', None)
        if not profile or not profile.stripe_account_id:
            return Response({'detail': 'Stripe account not found for artist.'}, status=status.HTTP_400_BAD_REQUEST)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            account_link = stripe.AccountLink.create(
                account=profile.stripe_account_id,
                refresh_url=request.build_absolute_uri('/'),
                return_url=request.build_absolute_uri('/'),
                type='account_onboarding',
            )
            return Response({'url': account_link['url']})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateCheckoutSessionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not product.artist.stripe_account_id:
            return Response({'detail': 'Artist not connected to Stripe.'}, status=status.HTTP_400_BAD_REQUEST)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        commission_pct = getattr(settings, 'COMMISSION_PERCENT', 10)
        application_fee = int(product.price_cents * commission_pct / 100)

        try:
            host = request.get_host()
            success_url = request.build_absolute_uri('/')
            cancel_url = request.build_absolute_uri('/')
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {'name': product.title},
                        'unit_amount': product.price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                payment_intent_data={
                    'application_fee_amount': application_fee,
                    'transfer_data': {'destination': product.artist.stripe_account_id},
                },
                metadata={'product_id': str(product.id)}
            )
            return Response({'url': session.url})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'artist_profile', None)
        if not profile:
            return Response({'detail': 'Artist profile not found.'}, status=status.HTTP_400_BAD_REQUEST)
        # orders for the artist's products
        orders = Order.objects.filter(product__artist=profile).order_by('-created_at')
        from .serializers import OrderSerializer
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)


class RefundOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

        # only the artist who owns the product or staff can refund
        user = request.user
        if not (user.is_staff or (order.product and order.product.artist and order.product.artist.user == user)):
            return Response({'detail': 'Not permitted.'}, status=status.HTTP_403_FORBIDDEN)

        if not order.stripe_payment_intent:
            return Response({'detail': 'No payment intent to refund.'}, status=status.HTTP_400_BAD_REQUEST)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            stripe.Refund.create(payment_intent=order.stripe_payment_intent)
            order.refunded = True
            order.refunded_at = timezone.now()
            order.fulfilled = False
            order.save()
            return Response({'detail': 'Refund initiated.'})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except Exception as e:
            return Response(status=400)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # Use metadata to find the product and record the order
            metadata = session.get('metadata', {}) or {}
            product_id = metadata.get('product_id')
            try:
                product = Product.objects.get(pk=int(product_id)) if product_id else None
            except Exception:
                product = None

            # Create an Order record
            try:
                amount = session.get('amount_total') or 0
                payment_intent = session.get('payment_intent')
                buyer_email = session.get('customer_details', {}).get('email') if session.get('customer_details') else None
                order = Order.objects.create(
                    product=product,
                    buyer_email=buyer_email,
                    amount_cents=amount,
                    stripe_payment_intent=payment_intent,
                    user=User.objects.filter(email__iexact=buyer_email).first() if buyer_email else None,
                )
                # decrement stock and mark fulfilled if possible
                try:
                    if product and product.stock is not None and product.stock > 0:
                        product.stock = max(0, product.stock - 1)
                        product.save()
                    order.fulfilled = True
                    order.save()
                except Exception:
                    pass

                try:
                    subject = f"Your purchase of {product.title if product else 'an item'}"
                    plain = f"Thank you for your purchase. Order id: {order.id}. Amount: €{(order.amount_cents/100):.2f}"
                    html = f"<html><body><h1>Thank you for your purchase</h1><p>Order id: {order.id}</p><p>Item: {product.title if product else 'Item'}</p><p>Amount: €{(order.amount_cents/100):.2f}</p></body></html>"
                    recipient = [buyer_email] if buyer_email else []

                    # generate invoice PDF
                    invoice_pdf = generate_invoice_pdf(order)

                    # upload to S3 if configured and set invoice_url
                    invoice_url = None
                    try:
                        if getattr(settings, 'USE_S3', False):
                            key = f'invoices/invoice_{order.id}.pdf'
                            invoice_url = upload_buffer_to_s3(invoice_pdf, key)
                            order.invoice_url = invoice_url
                            order.save()
                    except Exception:
                        invoice_url = None

                    if recipient:
                        if invoice_url:
                            # send link in email
                            html_with_link = html + f"<p>Download your invoice <a href='{invoice_url}'>here</a>.</p>"
                            send_mail(subject, plain, settings.DEFAULT_FROM_EMAIL, recipient, html_message=html_with_link)
                        else:
                            # attach PDF inline
                            email = EmailMessage(subject, plain, settings.DEFAULT_FROM_EMAIL, recipient)
                            email.content_subtype = 'html'
                            invoice_pdf.seek(0)
                            email.attach(f'invoice_{order.id}.pdf', invoice_pdf.read(), 'application/pdf')
                            email.send(fail_silently=True)

                    # notify artist with a simple email
                    if product and product.artist and product.artist.user and product.artist.user.email:
                        artist_email = product.artist.user.email
                        a_subject = f"Your item sold: {product.title}"
                        a_message = f"Your item '{product.title}' was sold. Order id: {order.id}."
                        send_mail(a_subject, a_message, settings.DEFAULT_FROM_EMAIL, [artist_email])
                except Exception:
                    pass
            except Exception:
                pass

        return Response(status=200)


class CustomerOrdersView(APIView):
    """Return orders for the authenticated customer's email."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        email = user.email
        if not email:
            return Response({'detail': 'User has no email on account.'}, status=status.HTTP_400_BAD_REQUEST)
        orders = Order.objects.filter(buyer_email__iexact=email).order_by('-created_at')
        from .serializers import OrderSerializer
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)
