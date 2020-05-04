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
        player = Player(channel_name=self.channel_name, game_code=self.room_code, play_order=(last_player.play_order + 1))
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
        room = Room.objects.get(code=self.room_code)
        if not room.ingame:
            # If the room game hasn't started yet, decrement player by one and send a room message to other players in the group.
            room.update(players=F('players')-1)
            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': 'A user has left the game lobby.'
                }
            )

            # Remove the websocket from the group.
            await self.channel_layer.group_discard(
                self.room_code,
                self.channel_name
            )

            # Delete the Player object.
            Player.objects.get(channel_name=self.channel_name).delete()
        else:
            # User disconnected from a game in progress, end it.
            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': 'The game has ended due to a user leaving the room.'
                }
            )

            # Remove the room from objects.
            # This should cascade the relevant Game and Player objects to also be deleted.
            room = Room.objects.get(self.room_code).delete()

    async def receive(self, text_data):
        # Get the message data recieved from the user.
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        player = Player.objects.get(channel_name=self.channel_name)
        if message_type == "game_move":
            player = text_data_json['player']
            game = Game.objects.get(code=self.room_code)
            # Check if the recieved move is from the player that should be making a turn.
            if player.play_order != game.current_turn:
                # The player isn't meant to make a move. Return an error message to that player.
                await self.send(text_data=json.dumps({
                    'type': 'room_message',
                    'message': 'It isn\'t your turn yet!'
                }))
            # The message is related to a game move.
            move = text_data_json['move']
            if move == "skip":
                # Player has stated they will skip their turn for this round.
                winner = skip_turn(player, game)
                # Send a message to the group of the player skipping their turn.
                await self.channel_layer.group_send(
                    self.room_code,
                    {
                        'type': 'game_move',
                        'player': player.channel_name,
                        'move': 'skip',
                        'special': 'None'
                    }
                )
                # Check if there are more than two players left in the round. If not, that one player has won and is the starter.
                if winner:
                    # Returns a player if they are the only one left.
                    # There are no more than two players left. Round concluded.
                    # Send a room message of who has won the round.
                    await self.channel_layer.group_send(
                        self.room_code,
                        {
                            'type': 'room_message',
                            'message': '{} has won the round!'.format(winner.name)
                        }
                    )
                    # Send a room command indicating the next round.
                    await self.channel_layer.group_send(
                        self.room_code,
                        {
                            'type': 'room_command',
                            'command': 'next_round'
                        }
                    )
                    new_round(game)
                await self.next_turn()


            else:
                # Card(s) have been played.
                check = play_move(move, special, player,)
                if check == -1:
                    # An invalid move was made, send error message to player.
                    # This shouldn't normally be invoked as invalid moves should be unplayable client-side
                    await self.send(text_data=json.dumps({
                        'type': 'room_message',
                        'message': 'An invalid move was made!'
                    }))
                else:
                    # A valid move was made. Send the move made to all players
                    await self.channel_layer.group_send(
                        self.room_code,
                        {
                            'type': 'game_move',
                            'player': player.channel_name,
                            'move': move,
                            'special': special
                        }
                    )
                    # If a player has finished their hand, declare their position.
                    # The check returns the number of cards the player has left.
                    if check == 0:
                        await self.channel_layer.group_send(
                            self.room_code,
                            {
                                'type': 'room_message',
                                'message': '{} has finished with the position of {}!'.format(player.name, player.role)
                            }
                        )

                        # Check if there are any more players. If not, end the game.
                        remaining = Player.objects.filter(code=self.room_code).filter(card_num>0)
                        if len(remaining) < 2:
                            # Set the last player's role to Scum
                            remaining[0].role = 'SC'
                            remaining[0].save()
                            players = Player.objects.filter(code=self.room_code)
                            results = []
                            for p in players:
                                results.append([player.role, player.name])
                            await self.channel_layer.group_send(
                                self.room_code,
                                {
                                    'type': 'results',
                                    'results': results
                                }
                            )
                            return
                    await self.next_turn()
            
        elif message_type == "name":
            # Player name registration
            player.name = text_data_json['name']
            player.save()

            # Send a message to the room of a player joining.
            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': "{} has joined the room.".format(player.name)
                }
            )
        elif message_type == "start":
            # Check if all players have a registered name.
            # If a player has a null name, then all players are not ready yet.
            players = Player.objects.filter(code=self.room_code).order_by('play_order')
            for k, i in enumerate(players):
                # Reassign order numbers to be perfectly in order with no number skips.
                i.play_order = k
                i.save()
                if i.name == None:
                    await self.send(text_data=json.dumps({
                        'type': 'room_message',
                        'message': 'All players are not ready yet.'
                    }))
                    return
            # Players are all ready, set the room ingame state to true to prevent further players joining.
            room = Room.objects.get(code=self.room_code)
            room.ingame = True
            room.save()
            # Proceed to process cards then give to each player
            handout = serve_cards(players, self.room_code)
            for k, i in enumerate(players):
                await self.channel_layer.send(i.channel_name, {
                    'type': 'handout',
                    'handout': handout[k]
                })

            # If there exists a scum, then initiate card swap stage
            #TODO: this^

            # Start the game.
            await self.next_turn()
        elif message_type == "chat":
            message = text_data_json['message']
            # Send a message to the room of a player joining.
            await self.channel_layer.group_send(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': message
                }
            )

    async def next_turn(self, *args)
        game = Game.objects.get(code=self.room_code)
        starter = Player.objects.get(play_order=game.play_order)
        # Send a message to the room of who is starting the game.
        await self.channel_layer.group_send(
            self.room_code,
            {
                'type': 'room_message',
                'message': "It is now {}'s turn.".format(starter.name)
            }
        )
        # Send a message to player one to start their move
        await self.channel_layer.send(starter.channel_name, {
            'type': 'game_command',
            'command': 'turn'
        })

    async def room_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'room_message',
            'message': message
        }))

    async def game_move(self, event):
        player = event['player']
        move = event['move']
        special = event['special']

        await self.send(text_data=json.dumps({
            'type': 'game_move',
            'player': player,
            'move': move,
            'special': special
        }))

    async def handout(self, event):
        handout = event['handout']
        await self.send(text_data=json.dumps({
            'type': 'handout',
            'handout': handout
        }))

    async def game_command(self, event):
        command = event['command']

        await self.send(text_data=json.dumps({
            'type': 'game_command',
            'command': command
        }))

    async def results(self, event):
        results = event['results']
        await self.send(text_data=json.dumps({
            'type': 'results',
            'results': results
        }))