from rest_framework import mixins, viewsets, exceptions

from .models import Event, TicketType, Order
from .serializers import EventSerializer, TicketTypeSerializer, OrderSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.prefetch_related("ticket_types")


class OrderViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order.book_tickets()
        if not order.fulfilled:
            order.delete()
            raise exceptions.ValidationError("Couldn't book tickets")
