from django.test import TestCase, Client
from .models import Room
import json

# Create your tests here.


class RequestsTestCase(TestCase):

    def setUp(self):
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        self.room = Room(game_type=0, max_players=4, code="AAAAA")
        self.room.save()

    def test_create_room(self):
        # Test for if the room is created properly.
        response = self.client.post('', {"game_type": 0, "max_players": 4})
        json_data = json.loads(response.content)
        self.assertTrue(json_data["success"])
        return json_data["success"]

    def test_join_existingroom(self):
        # Test for joining an existing room.
        # Specific to President
        response = self.client.get("/" + self.room.code)
        json_data = json.loads(response.content)
        self.assertEqual(json_data["success"], "president")

    def test_join_nonexistant_room(self):
        # Test for attempting to join a non-existant room.
        response = self.client.get("/AAAAB")
        json_data = json.loads(response.content)
        self.assertEqual(json_data["error"], "Room does not exist.")

    def test_join_insession_room(self):
        # Test for attempting to join a room in session.
        self.room.ingame = True
        self.room.save()
        response = self.client.get("/" + self.room.code)
        json_data = json.loads(response.content)
        self.assertEqual(json_data["error"], "Game is in session.")

    def test_join_fullroom(self):
        # Test for attempting to join a full room.
        self.room.max_players = 0
        self.room.save()
        response = self.client.get("/" + self.room.code)
        json_data = json.loads(response.content)
        self.assertEqual(json_data["error"], "Room is full.")
