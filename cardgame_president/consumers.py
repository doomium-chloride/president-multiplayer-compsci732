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
from channels.layers import get_channel_layer

class GameConsumer(WebsocketConsumer):
    def connect(self):
        # Get room_code from url.
        # e.g. url/room_code.
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        
        # Add the incoming websocket to a group.
        # Game-wide messages will be sent to this group reference.
        async_to_sync(self.channel_layer.group_add)(
            self.room_code,
            self.channel_name
        )

        # Get the game object
        game = getGameByCode(self.room_code)

        # Create new Player object.
        # Get the last player's order number. The new player will have the same order number + 1.
        players = getPlayersByCode(self.room_code)
        if len(players) < 1:
            play_order = 0
        else:
            play_order = Player.objects.filter(code=self.room_code).order_by('play_order').last().play_order
        player = Player(channel_name=self.channel_name, game=game, play_order=(play_order + 1))
        player.save()

        # Accept the websocket.
        self.accept()

        # Send a message to everyone else of the player entering.
        async_to_sync(self.channel_layer.group_send)(
            self.room_code,
            {
                'type': 'room_message',
                'message': "A user has joined the lobby."
            }
        )

        # Prompt the user to enter a display name.
        self.send(text_data=json.dumps({
            'type': 'room_message',
            'message': "Please enter a name."
        }))

    def disconnect(self, close_code):
        # A user has disconnected from a room.
        # The game state dictates what action to take.
        room = getRoomByCode(self.room_code)
        if not room.ingame:
            # If the room game hasn't started yet, decrement player by one and send a room message to other players in the group.
            room.update(players=F('players')-1)

            # Get the Player object of the player who left.
            player = Players.objects.get(channel_name=self.channel_name)
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': '{} has left the game lobby.'.format(player.name)
                }
            )
            
            # Send notifciation to clients to remove player from their displays
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'player_leave',
                    'channel_id': self.channel_name,
                    'name': player.name
                }
            )

            # Remove the websocket from the group.
            async_to_sync(self.channel_layer.group_discard)(
                self.room_code,
                self.channel_name
            )
            

            # Delete the Player object.
            player.delete()
        else:
            # User disconnected from a game in progress, end it.
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': 'The game has ended due to a user leaving the room.'
                }
            )

            # Send command to lock the room up (no more moves to be played)
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'game_command',
                    'command': 'close'
                }
            )

            # Remove the room from objects.
            # This should cascade the relevant Game and Player objects to also be deleted.
            room.delete()

    def receive(self, text_data):
        # Get the message data recieved from the user.
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        player = Player.objects.get(channel_name=self.channel_name)
        if message_type == "game_move":
            player = text_data_json['player']
            game = getGameByCode(self.room_code)
            # Check if the recieved move is from the player that should be making a turn.
            if player.play_order != game.current_turn:
                # The player isn't meant to make a move. Return an error message to that player.
                self.send(text_data=json.dumps({
                    'type': 'room_message',
                    'message': 'It isn\'t your turn yet!'
                }))
            # The message is related to a game move.
            move = text_data_json['move']
            if move == "skip":
                # Player has stated they will skip their turn for this round.
                winner = skip_turn(player, game)
                # Send a message to the group of the player skipping their turn.
                async_to_sync(self.channel_layer.group_send)(
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
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_code,
                        {
                            'type': 'room_message',
                            'message': '{} has won the round!'.format(winner.name)
                        }
                    )
                    # Send a room command indicating the next round.
                    async_to_sync(self.channel_layer.group_send)(
                        self.room_code,
                        {
                            'type': 'room_command',
                            'command': 'next_round'
                        }
                    )
                    new_round(self.room_code)
                self.next_turn()


            else:
                # Card(s) have been played.
                check = play_move(move, special, player,)
                if check == -1:
                    # An invalid move was made, send error message to player.
                    # This shouldn't normally be invoked as invalid moves should be unplayable client-side
                    self.send(text_data=json.dumps({
                        'type': 'room_message',
                        'message': 'An invalid move was made!'
                    }))
                else:
                    # A valid move was made. Send the move made to all players
                    async_to_sync(self.channel_layer.group_send)(
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
                        async_to_sync(self.channel_layer.group_send)(
                            self.room_code,
                            {
                                'type': 'room_message',
                                'message': '{} has finished with the position of {}!'.format(player.name, player.role)
                            }
                        )

                        # Check if there are any more players. If not, end the game.
                        players = getPlayersByCode(self.room_code).order_by('play_order')
                        remaining = players.filter(card_num>0)
                        if len(remaining) < 2:
                            # Set the last player's role to Scum
                            remaining[0].role = 'SC'
                            remaining[0].save()
                            results = []
                            for p in players:
                                results.append([player.role, player.name])
                            async_to_sync(self.channel_layer.group_send)(
                                self.room_code,
                                {
                                    'type': 'results',
                                    'results': results
                                }
                            )
                            return
                    self.next_turn()
            
        elif message_type == "name":
            # Player name registration
            player.name = text_data_json['name']
            player.save()

            # Send a message to the room of a player joining.
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': "{} has joined the game.".format(player.name)
                }
            )
            
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'player_join',
                    'channel_id': self.channel_name,
                    'name': player.name
                }
            )
        elif message_type == "start":
            # Check if all players have a registered name.
            # If a player has a null name, then all players are not ready yet.
            players = getPlayersByCode(self.room_code).order_by('play_order')
            for k, i in enumerate(players):
                # Reassign order numbers to be perfectly in order with no number skips.
                i.play_order = k
                i.save()
                if i.name == None:
                    self.send(text_data=json.dumps({
                        'type': 'room_message',
                        'message': 'All players are not ready yet.'
                    }))
                    return
            # Players are all ready, set the room ingame state to true to prevent further players joining.
            room = getRoomByCode(self.room_code)
            room.ingame = True
            room.save()
            # Proceed to process cards then give to each player
            handout = serve_cards(players, self.room_code)
            for k, i in enumerate(players):
                player_cardnums = []
                for j in players:
                    if j != i:
                        player_cardnums.append([j.channel_name, j.card_num])
                async_to_sync(self.channel_layer.send)(
                    i.channel_name,
                    {
                        'type': 'handout',
                        'handout': handout[k],
                        'player_cardnums': player_cardnums
                    }
                )

            # If there exists a scum, then initiate card swap stage
            #TODO: this^

            # Start the game.
            self.next_turn()
        elif message_type == "chat":
            message = text_data_json['message']
            # Send a message to the room of a player joining.
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'room_message',
                    'message': message
                }
            )

    def next_turn(self, *args):
        game = getGameByCode(self.room_code)
        starter = Player.objects.get(play_order=game.play_order)
        # Send a message to the room of who is starting the game.
        async_to_sync(self.channel_layer.group_send)(
            self.room_code,
            {
                'type': 'room_message',
                'message': "It is now {}'s turn.".format(starter.name)
            }
        )
        # Send a message to player one to start their move
        async_to_sync(self.channel_layer.send)(
            starter.channel_name, {
                'type': 'game_command',
                'command': 'turn'
            }
        )

    def room_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type': 'room_message',
            'message': message
        }))

    def game_move(self, event):
        player = event['player']
        move = event['move']
        special = event['special']

        self.send(text_data=json.dumps({
            'type': 'game_move',
            'player': player,
            'move': move,
            'special': special
        }))

    def handout(self, event):
        handout = event['handout']
        player_cardnums = event['player_cardnums']
        self.send(text_data=json.dumps({
            'type': 'handout',
            'handout': handout,
            'player_cardnums': player_cardnums
        }))

    def game_command(self, event):
        command = event['command']

        self.send(text_data=json.dumps({
            'type': 'game_command',
            'command': command
        }))

    def results(self, event):
        results = event['results']
        self.send(text_data=json.dumps({
            'type': 'results',
            'results': results
        }))

    def player_join(self, event):
        channel_id = event['channel_id']
        name = event['name']
        self.send(text_data=json.dumps({
            'type': 'player_join',
            'channel_id': channel_id,
            'name': name
        }))

    def player_leave(self, event):
        channel_id = event['channel_id']
        name = event['name']
        self.send(text_data=json.dumps({
            'type': 'player_leave',
            'channel_id': channel_id,
            'name': name
        }))