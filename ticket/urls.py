from rest_framework.routers import SimpleRouter

from . import viewsets


router = SimpleRouter(trailing_slash=False)
router.register(r"events", viewsets.EventViewSet)
router.register(r"orders", viewsets.OrderViewSet)

urlpatterns = router.urls
