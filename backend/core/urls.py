from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from shop import views as shop_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'products', shop_views.ProductViewSet, basename='product')
router.register(r'artists', shop_views.ArtistProfileViewSet, basename='artist')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', shop_views.RegisterView.as_view(), name='register'),
    path('api/my/products/', shop_views.MyProductsView.as_view(), name='my-products'),
    path('api/my/profile/', shop_views.MyProfileView.as_view(), name='my-profile'),
    path('api/my/orders/', shop_views.MyOrdersView.as_view(), name='my-orders'),
    path('api/orders/my/', shop_views.CustomerOrdersView.as_view(), name='customer-orders'),
    path('api/orders/<int:pk>/refund/', shop_views.RefundOrderView.as_view(), name='refund-order'),
    path('api/stripe/create-account/', shop_views.CreateStripeAccountView.as_view(), name='create-stripe-account'),
    path('api/stripe/create-account-link/', shop_views.CreateStripeAccountLinkView.as_view(), name='create-stripe-account-link'),
    path('api/stripe/checkout/<int:pk>/', shop_views.CreateCheckoutSessionView.as_view(), name='stripe-checkout'),
    path('api/stripe/webhook/', shop_views.StripeWebhookView.as_view(), name='stripe-webhook'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
