from operator import itemgetter

from django_dynamic_fixture import G

from test import APITestCase, AnyOrder, Any
from ticket.models import Order, Event, TicketType


class EndpointsTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = G(Event, name="Summer Party", description="We have a pool !")
        cls.ticket_type1 = G(TicketType, name="Early Bird", event=cls.event, quantity=1)
        cls.ticket_type2 = G(TicketType, name="Night Owl", event=cls.event, quantity=2)

    def test_unauth_requests(self):
        unauth_event_detail_resp = self.client.get("/api/events/1")
        unauth_event_list_resp = self.client.get("/api/events")
        unauth_order_detail_resp = self.client.get("/api/orders/1")
        unauth_order_list_resp = self.client.get("/api/orders")
        unauth_order_create_resp = self.client.post("/api/orders")

        self.assertEqual(unauth_event_detail_resp.status_code, 401)
        self.assertEqual(unauth_event_list_resp.status_code, 401)
        self.assertEqual(unauth_order_detail_resp.status_code, 401)
        self.assertEqual(unauth_order_list_resp.status_code, 401)
        self.assertEqual(unauth_order_create_resp.status_code, 401)

    def test_event_detail(self):
        self.authorize()
        resp = self.client.get(f"/api/events/{self.event.pk}")

        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(
            resp.data,
            {
                "id": self.event.pk,
                "name": "Summer Party",
                "description": "We have a pool !",
                "ticket_types": AnyOrder(
                    [
                        {"id": self.ticket_type1.pk, "name": "Early Bird"},
                        {"id": self.ticket_type2.pk, "name": "Night Owl"},
                    ],
                    key=itemgetter("id"),
                ),
            },
        )

    def test_event_list(self):
        another_event = G(Event, name="Sponge Bob Concert", description="Bring your scuba diving gear")

        self.authorize()
        resp = self.client.get("/api/events")

        self.assertEqual(resp.status_code, 200)
        self.assertCountEqual(
            resp.data,
            [
                {
                    "id": self.event.pk,
                    "name": "Summer Party",
                    "description": "We have a pool !",
                    "ticket_types": AnyOrder(
                        [
                            {"id": self.ticket_type1.pk, "name": "Early Bird"},
                            {"id": self.ticket_type2.pk, "name": "Night Owl"},
                        ],
                        key=itemgetter("id"),
                    ),
                },
                {
                    "id": another_event.pk,
                    "name": "Sponge Bob Concert",
                    "description": "Bring your scuba diving gear",
                    "ticket_types": [],
                },
            ],
        )

    def test_ticket_ordering(self):
        self.authorize()

        not_enought_ticket_resp = self.client.post(
            "/api/orders", data={"ticket_type": self.ticket_type1.pk, "quantity": 2}
        )
        successful_resp = self.client.post("/api/orders", data={"ticket_type": self.ticket_type2.pk, "quantity": 2})

        self.assertEqual(not_enought_ticket_resp.status_code, 400)
        self.assertEqual(not_enought_ticket_resp.data, ["Couldn't book tickets"])
        self.assertEqual(successful_resp.status_code, 201)
        self.assertEqual(successful_resp.data, {"id": Any(int), "ticket_type": self.ticket_type2.pk, "quantity": 2})

    def test_order_detail(self):
        user = self.authorize()
        order = G(Order, user=user)
        detail_url = f"/api/orders/{order.pk}"

        resp = self.client.get(detail_url)

        self.authorize()  # Change user
        other_user_resp = self.client.get(detail_url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["id"], order.pk)
        self.assertEqual(other_user_resp.status_code, 404)

    def test_order_list(self):
        user = self.authorize()
        order_a = G(Order, user=user)
        order_b = G(Order, user=user)

        resp = self.client.get("/api/orders")
        self.authorize()  # Change user
        no_order_resp = self.client.get("/api/orders")

        self.assertEqual(resp.status_code, 200)
        self.assertCountEqual([order["id"] for order in resp.data], [order_a.pk, order_b.pk])
        self.assertEqual(no_order_resp.status_code, 200)
        self.assertEqual(no_order_resp.data, [])
