import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from room_manager.models import Room
from .models import Game, Player
from .game_logic import getRoomByCode, getGameByCode, skip_turn, \
    new_game, reset_roles, reset_round, play_move, game_winner, \
    serve_cards
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
        player = Player(channel_name=self.channel_name, game=game)
        player.save()

        # Accept the websocket.
        self.accept()

        # Update frame for clients
        self.draw_frame()

    def disconnect(self, close_code):
        # A user has disconnected from a room.
        # The game state dictates what action to take.
        room = getRoomByCode(self.room_code)
        if not room.ingame:
            # If the room game hasn't started yet,
            # decrement player by one and send a
            # room message to other players in the group.
            room.players = room.players - 1
            room.save()

            # Get the Player object of the player who left.
            player = Player.objects.get(channel_name=self.channel_name)
            message = '{} has left the game lobby.'.format(player.name)
            self.send_message(message)

            # Update frame for clients
            self.draw_frame()

            # Remove the websocket from the group.
            async_to_sync(self.channel_layer.group_discard)(
                self.room_code,
                self.channel_name
            )

            # Delete the Player object.
            player.delete()
        else:
            # User disconnected from a game in progress, end it.
            message = 'The game has ended due to a user leaving the game.'
            self.send_message(message)

            # Freeze the game frame
            async_to_sync(self.channel_layer.group_send)(
                self.room_code,
                {
                    'type': 'freeze_game'
                }
            )

            # Remove the room from objects.
            # This should cascade the relevant Game and
            # Player objects to also be deleted.
            room.delete()

    def receive(self, text_data):
        # Get the message data recieved from the user.
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        player = Player.objects.get(channel_name=self.channel_name)
        if message_type == "game_move":
            # Check if the recieved move is from the player
            # that should be making a turn.
            if not player.current_turn:
                # The player isn't meant to make a move.
                # Return an error message to that player.
                self.send(text_data=json.dumps({
                    'type': 'room_message',
                    'message': 'It isn\'t your turn yet!'
                }))
                return
            # The message is related to a game move.

            move = text_data_json['move']
            game = getGameByCode(self.room_code)
            if move == "skip":
                # Player has stated they will skip their turn for this round.
                winner = skip_turn(player, game)
                # Send a response to the player that
                # their move has been accepted.
                self.move_response(move)
                # Send a message to the group of the
                # player skipping their turn.
                message = '{} has skipped their turn'.format(player.name)
                self.send_message(message)

                # Check if there are more than two players left in the round.
                # If not, that one player has won and is the starter.
                if winner:
                    # Returns a player if they are the only one left.
                    # There are no more than two players left. Round concluded.
                    # Send a room message of who has won the round.
                    message = '{} has won the round!'.format(winner.name)
                    self.send_message(message)
                    reset_round(game)

                # Update drawframe
                self.draw_frame()

            else:
                # Card(s) have been played.
                # Check returns te number of cards the player has.
                # -1 means the move they are attempting to make is invalid.
                check = play_move(move, player, game)
                if check == -1:
                    # An invalid move was made, send error message to player.
                    # This shouldn't normally be invoked as invalid moves
                    # should be unplayable client-side.
                    self.send(text_data=json.dumps({
                        'type': 'room_message',
                        'message': 'You cannot make this move!'
                    }))
                else:
                    # Send a response to the player that their
                    # move has been accepted.
                    self.move_response(move)
                    # If a player has finished their hand,
                    # declare their position.
                    # Check is the number of cards the player has left.
                    if check == 0:
                        message = '{} has finished with the '\
                            'position of {}!'.format(
                                player.name, player.get_role_display())
                        self.send_message(message)

                        # Check if there are any more players.
                        # If not, end the game.
                        if game_winner(game):
                            results = []
                            for p in game.players.all().order_by('-score'):
                                results.append([p.name, p.score])
                            async_to_sync(self.channel_layer.group_send)(
                                self.room_code,
                                {
                                    'type': 'results',
                                    'results': results
                                }
                            )
                    elif move.upper() == "XX":
                        message = '{} has won the round with a Joker!'.format(player.name)
                        self.send_message(message)
                    self.draw_frame()

        elif message_type == "name":
            # Player name registration
            name = text_data_json['name']
            # Check if that name already exists in this room.
            # No duplicates allowed.
            try:
                game = getGameByCode(self.room_code)
                game.players.get(name=name)
                self.send(text_data=json.dumps({
                    'type': 'room_message',
                    'message': 'This name is already chosen!'
                }))
            except Player.DoesNotExist:

                player.name = name
                player.save()

                # Send a name accepted response back to the client
                self.send(text_data=json.dumps({
                    'type': 'name_response',
                    'response': name,
                }))

                # Send a message to the room of a player joining.
                message = "{} has joined the game.".format(player.name)
                self.send_message(message)

                # Redraw frame
                self.draw_frame()

        elif message_type == "ready":
            game = getGameByCode(self.room_code)
            if game.room.ingame:
                # the player would like to player again.
                player.ready = True

                # Send a message to the chatbox that a player is ready.
                message = "{} would like to play again.".format(player.name)
                self.send_message(message)
            else:
                # toggle the ready state of the player. Used in pre-game
                player.ready = not player.ready
            player.save()

            players = game.players.all()

            if len(game.players.filter(ready=True)) == len(players) > 1:
                game.room.ingame = True
                game.room.save()
                new_game(game)
                handout = serve_cards(players, self.room_code)
                for k, i in enumerate(players):
                    async_to_sync(self.channel_layer.send)(
                        i.channel_name,
                        {
                            'type': 'handout',
                            'handout': handout[k]
                        }
                    )
                # Reset roles of players
                reset_roles(game)
            # Update frame
            self.draw_frame()

        elif message_type == "chat":
            # Get the player name to append to the beginning of the message.
            message = "{}: {}".format(player.name, text_data_json['message'])
            self.send_message(message)

    def draw_frame(self):
        players = {}
        for p in getGameByCode(self.room_code).players.all():
            info = {}
            info['name'] = p.name
            info['ready'] = p.ready
            info['role'] = p.role
            info['current_turn'] = p.current_turn
            info['skip_turn'] = p.skip_turn
            info['num_cards'] = p.num_cards

            players[p.name] = info

        game = getGameByCode(self.room_code)

        async_to_sync(self.channel_layer.group_send)(
            self.room_code,
            {
                'type': 'game_frame',
                'players': players,
                'current_card': game.current_card,
            }
        )

    def send_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_code,
            {
                'type': 'room_message',
                'message': message
            }
        )

    def move_response(self, move):
        self.send(text_data=json.dumps({
            'type': 'move_response',
            'move': move,
        }))

    def game_frame(self, event):
        self.send(text_data=json.dumps({
            'type': 'game_frame',
            'players': event['players'],
            'current_card': event['current_card'],
        }))

    def room_message(self, event):
        self.send(text_data=json.dumps({
            'type': 'room_message',
            'message': event['message'],
        }))

    def freeze_game(self, event):
        self.send(text_data=json.dumps({
            'type': 'freeze_game',
        }))

    def handout(self, event):
        self.send(text_data=json.dumps({
            'type': 'handout',
            'handout': event['handout'],
        }))

    def results(self, event):
        self.send(text_data=json.dumps({
            'type': 'results',
            'results': event['results'],
        }))
