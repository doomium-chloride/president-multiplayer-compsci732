from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from django.shortcuts import get_object_or_404
from .serializers import RoomSerializer
from .models import Room
import string
import random

class CreateRoomView(APIView):

    # Create room
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Generate a new random code and see if it exists already. If not, break loop
            while True:
                room_code = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
                if not Room.objects.filter(code=room_code).first():
                    break
            serializer.save(code=room_code)
            content = {'success': 'Room successfully created.'}
            return Response(content)

class JoinRoomView(APIView):

    # Join room
    def get(self, request):
        room_code = self.scope['url_route']['kwargs']['room_code']

        # See if the current room exists
        if not Room.objects.filter(code=room_code).first():
            content = {'error': 'Room does not exist.'}
            return Response(content)

        # See if the current room is full
        room = Room.objects.get(code=room_code)
        if room.players == room.max_players:
            content = {'error': 'Room is full.'}
            return Response(content)


        # Successful join, increment the player count by 1
        Room.objects.filter(code=room_code).update(players=F('players')+1)

        # Returns the room code
        content = {'success': (room_code, room.game)}
        return Response(content)