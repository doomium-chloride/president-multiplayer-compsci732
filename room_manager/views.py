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

            #TODO: websocket stuff here to make room

            return join_room(room_code)

class JoinRoomView(APIView):
    # Update room i.e. join a room
    def get(self, request, room_code=None):

        def join_room(room_code):
            target_room = get_object_or_404(Room.objects.all(), pk=room_code)
            serializer = RoomSerializer(instance=target_room, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save(players=F('players')+1)

                #TODO: websocket stuff here to join room

                content = {'success': 'Room successfully joined.'}
                return Response(content)
        # Room does not exist
        if not Room.objects.filter(code=room_code).first():
            content = {'error': 'Room does not exist.'}
            return Response(content)
        
        room = Room.objects.get(code=room_code)

        # Room is full
        if room.players == room.max_players:
            content = {'error': 'Room is full.'}
            return Response(content)
            
        return join_room(room_code)