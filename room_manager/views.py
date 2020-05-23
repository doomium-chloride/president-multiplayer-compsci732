from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from django.shortcuts import get_object_or_404
from .models import Room
from cardgame_president.game_logic import getRoomByCode
from cardgame_president.models import Game as PRES
import string
import random

class CreateRoomView(APIView):

    # Create room
    def post(self, request):
        game_type = int(request.data.get("game_type"))
        max_players = int(request.data.get("max_players"))
        while True:
            # Generate a new random code and see if it exists already. If not, break loop
            code = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
            if not Room.objects.filter(code=code).first():
                break
        room = Room(game_type=game_type, max_players=max_players, code=code)
        room.save()

        # Create the game-specific object
        if game_type == 0:
            # President game. Create a President-game specific object.
            game = PRES(room=room)
        game.save()

        content = {'success': code}
        return Response(content)

class JoinRoomView(APIView):

    # Join room
    def get(self, request, room_code):
        
        try:
            room = getRoomByCode(room_code)
            # See if the current room exists
        except Room.DoesNotExist:
            content = {'error': 'Room does not exist.'}
            return Response(content)

        # See if the current room is full
        if room.players == room.max_players:
            content = {'error': 'Room is full.'}
            return Response(content)

        # If the room is in session, return error
        if room.ingame:
            content = {'error': 'Game is in session.'}
            return Response(content)

        # Successful join, increment the player count by 1
        room.players = (room.players + 1)
        room.save()

        # Returns the room code
        content = {'success': room.get_game_type()}
        return Response(content)