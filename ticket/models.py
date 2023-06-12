from django.db import models, transaction
from django.conf import settings
from collections import defaultdict
from django.utils import timezone

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class TicketType(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, related_name="ticket_types", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, editable=False)

    quantity.help_text = "The number of actual tickets available upon creation"

    def available_tickets(self):
        return self.tickets.filter(order__isnull=True)

    def save(self, *args, **kwargs):
        new = not self.pk
        super().save(*args, **kwargs)
        if new:
            self.tickets.bulk_create([Ticket(ticket_type=self)] * self.quantity)


class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, related_name="tickets", on_delete=models.CASCADE)
    order = models.ForeignKey(
        "ticket.Order", related_name="tickets", default=None, null=True, on_delete=models.SET_NULL
    )


class Order(models.Model):
    
    STATUS=(('CAN','Cancelled'),('BOOK','Booked'),('NEW','New'),)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.PROTECT)
    ticket_type = models.ForeignKey(TicketType, related_name="orders", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    fulfilled = models.BooleanField(default=False)
    # New fields to capture cancel status, cancel date and order datetime.
    order_status = models.CharField(max_length=4, choices=STATUS,default='NEW')
    cancel_date= models.DateField(null = True)
    order_date= models.DateTimeField(null = True)

    def book_tickets(self):
        if self.fulfilled:
            raise Exception("Order already fulfilled")
        qs = self.ticket_type.available_tickets().select_for_update(skip_locked=True)[: self.quantity]
        try:
            with transaction.atomic():
                updated_count = self.ticket_type.tickets.filter(id__in=qs).update(order=self)
                if updated_count != self.quantity:
                    raise Exception
        except Exception:
            return
        self.fulfilled = True
        # Extra lines to add while saving the order.
        self.order_status = 'BOOK'
        self.order_date = timezone.now()
        self.save(update_fields=["fulfilled","order_status","order_date"])
        
    def cancel_tickets(self) :
        ''' Cancels the order if the time diff is less than or equal to 30 minutes.'''
        
        if self.fulfilled:
            
            # if the time difference is between 30 minutes of booking the tickets then cancel
            time_diff= ((timezone.now() - self.order_date) / 60).total_seconds()/60
            if time_diff <= 30:
                self.cancel_date = timezone.now().date()
                self.order_status = 'CAN'
                self.save(update_fields=[ "cancel_date","order_status"])
            else:
                raise ValueError('Order can not be cancelled after 30 minutes of booking')    
        else:
            raise ValueError('Order can not be cancelled')    
        
    def cancelled_orders(self):
        '''Returns all orders and percentage of canclelled orders'''
        
        event = Event.objects.filter(name=self.ticket_type.event.name).prefetch_related('ticket_types')
        
        total_orders =0
        perc_cancelled =0
        event_name = self.ticket_type.event.name
        if event is not None:
            base_queryset =  Order.objects.filter(ticket_type__event__name = event_name)
            orders = base_queryset.filter(order_status='BOOK')
            orders_cancelled = base_queryset.filter(order_status='CAN')
            total_orders = orders.count() + orders_cancelled.count()
            if total_orders !=0:
                perc_cancelled = (orders_cancelled.count() / total_orders) * 100
                 
        else:
            raise ValueError('No Event by the name.')
                
        
        return total_orders, perc_cancelled 
    
        
    def total_tickets(self):
        
        ''' Returns the total number cancelled tickets for a date, sorted by the count of the tickets'''
        orders = Order.objects.filter(order_status='CAN')
        highest_ticket= defaultdict(int)
        for order in orders:
            highest_ticket[order.cancel_date] += order.quantity
        date_with_tickets = dict(sorted(highest_ticket.items(),key = lambda x: x[1]))  
        return list(date_with_tickets.keys())[0]
