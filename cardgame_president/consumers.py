import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models import F
from django.shortcuts import get_object_or_404
from room_manager.models import Room
from .models import Game, Player
from .game_logic import *
import string
import random
from chanels.layers import get_channel_layer

class GameConsumer(WebsocketConsumer):
    def connect(self):
        # Get room_code from url
        # e.g. url/room_code
        self.room_code = self.scope['url_route']['kwargs']['room_code']

        async_to_sync(self.channel_layer.group_add)(
            self.room_code,
            self.channel_name
        )

        room = Room.objects.get(room_code=self.room_code)

        # Create new player
        player = Player(channel_name=self.channel_name, game_code=self.room_code, player_order=(room.players - 1))
        player.save()

        self.accept()

        self.send(text_data=json.dumps({
            'response': 'Name required.'
        }))


    def disconnect(self, close_code):
        # A user has disconnected from a room.
        # If the room game hasn't started yet, decrement player by one and send update to other players in the group
        room_code = Player.objects.get(channel_name=self.channel_name).game_code
        room = Room.objects.get(code=room_code)
        if not room.ingame:
            room.update(players=F('players')-1)
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'room_response',
                    'response_type': 'game_message',
                    'response': 'A user has left the game lobby.'
                }
            )
            Player.objects.get(channel_name=self.channel_name).delete()
        else:
            # User disconnected from a game in progress, end it
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'room_response',
                    'response_type': 'game_message',
                    'response': 'A user has disconnected from the game.'
                }
            )

            async_to_sync(self.channel_layer.group_discard)(
                self.room_code,
                self.channel_name
            )

            # Remove game from Objects
            game = Game.objects.get(game_code=self.room_code)
            game.delete()

            # When a game is deleted, all Player objects associated with that game are also deleted.

            # Remove room from Objects
            room.delete()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        response_type = text_data_json['type']
        player = Player.objects.get(channel_name=self.channel_name)
        if response_type == "move":
            move = text_data_json['move']
            check = play_move(move, player)
            if check == -1:
                # An invalid move was made, send error message to player.
                # This shouldn't normally be invoked as invalid moves should be unplayable client-side
                self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_error',
                    'response': 'Invalid response.'
                }))
            else:
                # A valid move was made. Send the move made to all players
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'room_response',
                        'response_type': 'game_move',
                        'response': (self.channel_name, move)
                    }
                )
                # Check if there were any special changes.
                # Consecutive was enforced.
                # Sets was enforced.
                # If a player has finished their hand, declare their position.
        elif response_type == "skip":
            player = Player.objects.get(channel_name=self.channel_name)
            check = skip_turn(player)
            if check == -1:
                # An invalid skip was made, send error message to player.
                # This shouldn't normally be invoked as invalid skips should be unplayable client-side
                self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_error',
                    'response': 'Invalid response.'
                }))
            else:
                # A valid skip was made. Send the skip messaage to all players
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'room_response',
                        'response_type': 'game_move',
                        'response': (self.channel_name, 'skip')
                    }
                )
        elif response_type == "name":
            # Player name registration
            # Check if the room game has started yet.
            room = Room.objects.get(code=player.game_code)
            if room.ingame:
                # The game has already started, invalid message
                self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_error',
                    'response': 'Invalid response.'
                }))
            else:
                player.name = text_data_json['name']
                player.save()
                self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_message',
                    'response': 'Name registered.'
                }))
                # Send room message
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'room_response',
                        'response_type': 'player_join',
                        'response': (self.channel_name, player.name)
                    }
                )
        elif response_type == "start":
            # Check if all players have a registered name.
            players = Player.objects.filter(game_code=player.game_code).order_by('play_order')
            for i in players:
                if i.name == None:
                    self.send(text_data=json.dumps({
                        'type': 'room_response',
                        'response_type': 'game_message',
                        'response': 'All players are not ready yet.'
                    }))
                    return
            # Players are all ready, start the game
            room = Room.objects.get(code=player.game_code)
            room.ingame = True
            room.save()
            # Proceed to process cards then give to each player
            handout = serve_cards(players)
            channel_layer = get_channel_layer()
            for k, i in enumerate(players):
                self.channel_layer.send(i.channel_name, {
                    'type': 'room_response',
                    'response_type': 'handout',
                    'response': handout[k]
                })
            # If there exists a scum, then initiate card swap stage
            #TODO: this^

            # Send a message to player one to start their move
            self.channel_layer.send(players[0].channel_name, {
                'type': 'room_response',
                'response_type': 'game_action',
                'response': "Make your move."
            })
            

    def room_response(self, event):
        response = event['response']
        response_type = event['response_type']

        self.send(text_data=json.dumps({
            'response_type': response_type,
            'response': response
        }))
