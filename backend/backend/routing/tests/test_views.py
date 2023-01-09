from django.test import TestCase
from routing.matching import LSA

class ViewsTest(TestCase):
    def test_lsa_selection_view(self):
        payload = {
            "route": [
                {"lon": 0, "lat": 0, "alt": 0},
                {"lon": 1, "lat": 1, "alt": 1},
                {"lon": 2, "lat": 2, "alt": 2},
            ]
        }
        response = self.client.post(
            '/routing/select?matcher=ml', 
            follow=True,
            content_type='application/json',
            data=payload,
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(len(response_json["route"]), 3)
        self.assertEqual(len(response_json["signalGroups"]), 0)
