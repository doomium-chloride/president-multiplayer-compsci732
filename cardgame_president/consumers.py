import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from django.db.models import F
from django.shortcuts import get_object_or_404
from room_manager.serializers import RoomSerializer
from room_manager.models import Room
import string
import random

class GameConsumer(WebsocketConsumer):
    def connect(self):
        # Get room_code from url
        # e.g. url/room_code
        self.room_code = self.scope['url_route']['kwargs']['room_code']

        async_to_sync(self.channel_layer.group_add)(
            self.room_code,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # A user has disconnected from a room.
        # If the room game hasn't started yet, decrement player by one and send update to other groups
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        room = Room.objects.get(code=room_code)
        if room.ingame:
            target_room = get_object_or_404(Room.objects.all(), pk=room_code)
            serializer = RoomSerializer(instance=target_room, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save(players=F('players')-1)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'room_message',
                    'message': 'A user has left the game lobby.'
                }
            )
        else:
            # User disconnected from a game in progress, end it
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'room_message',
                    'message': 'A user has disconnected from the game.'
                }
            )

            async_to_sync(self.channel_layer.group_discard)(
                self.room_code,
                self.channel_name
            )

            #TODO: Remove game from Objects

            # Remove room from Objects
            room.delete()

    def receive(self, text_data):
        #TODO: Receive a game-specific command from the websocket.
        pass

    def room_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'message': message
        }))