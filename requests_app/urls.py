from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import SupportRequestViewSet

router = DefaultRouter()
router.register("requests", SupportRequestViewSet, basename="support-request")

urlpatterns = router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)