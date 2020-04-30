import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import F
from django.shortcuts import get_object_or_404
from room_manager.models import Room
from .models import Game, Player
from .game_logic import *
import string
import random
from chanels.layers import get_channel_layer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get room_code from url.
        # e.g. url/room_code.
        self.room_code = self.scope['url_route']['kwargs']['room_code']

        # Send a message to the room of a player joining.
        await self.channel_layer.group_send(
            self.room_code,
            {
                'type': 'room_message',
                'message': "A Player has joined the room."
            }
        )
        
        # Add the incoming websocket to a group.
        # Game-wide messages will be sent to this group reference.
        await self.channel_layer.group_add(
            self.room_code,
            self.channel_name
        )

        # Get the room object to get the room code.
        room = Room.objects.get(room_code=self.room_code)

        # Create new Player object.
        # Get the last player's order number. The new player will have the same order number + 1.
        last_player = Player.objects.filter(code=self.room_code).order_by('play_order').last()
        player = Player(channel_name=self.channel_name, game_code=self.room_code, player_order=(last_player.play_order + 1))
        player.save()

        # Accept the websocket.
        await self.accept()

        # Prompt the user to enter a display name.
        await self.send(text_data=json.dumps({
            'type': 'room_message',
            'message': "Please enter a name."
        }))

    await def disconnect(self, close_code):
        # A user has disconnected from a room.
        # The game state dictates what action to take.
        room = Room.objects.get(code=self.room_group_name)
        if not room.ingame:
            # If the room game hasn't started yet, decrement player by one and send a room message to other players in the group.
            room.update(players=F('players')-1)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'room_message',
                    'message': 'A user has left the game lobby.'
                }
            )

            # Remove the websocket from the group.
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            Player.objects.get(channel_name=self.channel_name).delete()
        else:
            # User disconnected from a game in progress, end it.
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'room_message',
                    'message': 'The game has ended due to a user leaving the room.'
                }
            )

            # Remove the room from objects.
            # This should cascade the relevant Game and Player objects to also be deleted.
            room = Room.objects.get(self.room_group_name).delete()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        response_type = text_data_json['type']
        player = Player.objects.get(channel_name=self.channel_name)
        if response_type == "move":
            move = text_data_json['move']
            check = play_move(move, player)
            if check == -1:
                # An invalid move was made, send error message to player.
                # This shouldn't normally be invoked as invalid moves should be unplayable client-side
                await self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_error',
                    'response': 'Invalid response.'
                }))
            else:
                # A valid move was made. Send the move made to all players
                await self.channel_layer.group_send(
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
                await self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_error',
                    'response': 'Invalid response.'
                }))
            else:
                # A valid skip was made. Send the skip messaage to all players
                await self.channel_layer.group_send(
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
                await self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_error',
                    'response': 'Invalid response.'
                }))
            else:
                player.name = text_data_json['name']
                player.save()
                await self.send(text_data=json.dumps({
                    'type': 'room_response',
                    'response_type': 'game_message',
                    'response': 'Name registered.'
                }))
                # Send room message
                await self.channel_layer.group_send(
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
                    await self.send(text_data=json.dumps({
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
                await self.channel_layer.send(i.channel_name, {
                    'type': 'room_response',
                    'response_type': 'handout',
                    'response': handout[k]
                })
            # If there exists a scum, then initiate card swap stage
            #TODO: this^

            # Send a message to player one to start their move
            await self.channel_layer.send(players[0].channel_name, {
                'type': 'room_response',
                'response_type': 'game_action',
                'response': "Make your move."
            })
            

    async def room_response(self, event):
        response = event['response']
        response_type = event['response_type']

        await self.send(text_data=json.dumps({
            'response_type': response_type,
            'response': response
        }))
