from django.test import TestCase
from django_dynamic_fixture import G, F

from ticket.models import Event, TicketType, Order
from django.utils import timezone


class TicketTypeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = G(Event)

    def test_avaialble_tickets(self):
        ticket_type = G(TicketType, name="Test", quantity=5, event=self.event)
        all_tickets = list(ticket_type.tickets.all())

        five_available_tickets = set(ticket_type.available_tickets())

        # book one ticket
        ticket = all_tickets[0]
        ticket.order = G(Order, ticket_type=ticket_type, quantity=1)
        ticket.save()

        four_available_tickets = set(ticket_type.available_tickets())

        self.assertCountEqual(five_available_tickets, all_tickets)
        self.assertCountEqual(four_available_tickets, set(all_tickets) - {ticket})

    def test_save(self):
        """Verifying that the save method creates Ticket(s) upon TicketType creation"""

        ticket_type_1 = G(TicketType, name="Without quantity", event=self.event)
        ticket_type_5 = G(TicketType, name="Test", quantity=5, event=self.event)

        one_ticket = ticket_type_1.tickets.count()
        five_tickets = ticket_type_5.tickets.count()

        self.assertEqual(one_ticket, 1)
        self.assertEqual(five_tickets, 5)


class OrderTest(TestCase):
    def test_book_tickets(self):
        order = G(Order, ticket_type=F(quantity=5), quantity=3)

        pre_booking_ticket_count = order.tickets.count()
        order.book_tickets()
        post_booking_ticket_count = order.tickets.count()

        with self.assertRaisesRegexp(Exception, r"Order already fulfilled"):
            order.book_tickets()

        self.assertEqual(pre_booking_ticket_count, 0)
        self.assertEqual(post_booking_ticket_count, 3)
        
    def test_cancel_tickets(self):
        order = G(Order, ticket_type=F(quantity=5), quantity=3) 
        pre_booking_ticket_count = order.tickets.count()
        order.book_tickets()
        
        order.cancel_tickets()
        post_cancel_ticket_count = order.tickets.count()
        
        
        
        self.assertEqual(pre_booking_ticket_count, 0)
        self.assertEqual(post_cancel_ticket_count, 3)
        
    def test_cancelled_orders(self):
        
        eve = G(Event, name="bbq", description="test desc")
        ticket_type_ge = G(TicketType, name="Gen", event=eve,quantity=6)
        #ticket_type_v = G(TicketType, name="vip", quantity=5, event=eve)
        order = G(Order, ticket_type=ticket_type_ge, quantity=3) 
        order1 = G(Order, ticket_type=ticket_type_ge, quantity=3)  
        order.book_tickets()
        order1.book_tickets() 
        order1.cancel_tickets()
        total,perc = order1.cancelled_orders()
        
        self.assertEqual(total, 2)
        self.assertEqual(perc, 50)
        
    
    def test_cancelled_orders_neg(self):
        eve = G(Event, name="bbq", description="test desc")
        ticket_type_ge = G(TicketType, name="Gen", event=eve,quantity=6)
        ticket_type_v = G(TicketType, name="vip", quantity=5, event=eve)
        order = G(Order, ticket_type=ticket_type_ge, quantity=3) 
        order1 = G(Order, ticket_type=ticket_type_ge, quantity=3)  
        order2 = G(Order, ticket_type=ticket_type_v, quantity=2)
        order.book_tickets()
        order1.book_tickets() 
        order2.book_tickets()
        order2.cancel_tickets()
        order1.cancel_tickets()
        date_check = order1.total_tickets()
        self.assertEqual(date_check, timezone.now().date())
           
