from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from django.shortcuts import get_object_or_404
from .serializers import RoomSerializer
from .models import Room
from cardgame_president.models import Game
import string
import random

class CreateRoomView(APIView):

    # Create room
    def post(self, request):
        game = request.data.get("game")
        max_players = request.data.get("max_players")
        while True:
            # Generate a new random code and see if it exists already. If not, break loop
            code = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
            if not Room.objects.filter(code=code).first():
                break
        room = Room(game=game, max_players=max_players, code=code)
        room.save()
        content = {'success': room_code}
        return Response(content)

class JoinRoomView(APIView):

    # Join room
    def get(self, request, code):
        
        room = Room.objects.get(code=code)
        # See if the current room exists
        if not room:
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
        Room.objects.get(code=code).update(players=F('players')+1)

        # Create the game
        game = Game(code=code)
        game.save()

        # Returns the room code
        content = {'success': (room.game)}
        return Response(content)