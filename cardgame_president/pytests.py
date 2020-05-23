import json
import pytest
import asyncio
import os
from django.test import override_settings
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.conf.urls import url
from django.test import Client
from django.db import models
from .consumers import GameConsumer
from .models import Game, Player
from room_manager.models import Room

# The websocket is written in sync but the test is in async.
# This OS environ is only used for testing.
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "True"

game_type = 0
num_players = 4
time = 0.8

# There WILL be issues running this test.
# Database Lock errors and DoesNotExist errors are a result of
# this async test querying the database too early.
# This is not an issue in production as everything is synchronous.

def create_room():
    client = Client(HTTP_USER_AGENT='Mozilla/5.0')
    response = client.post('', {"game_type": game_type, "max_players": num_players})
    json_data = json.loads(response.content)
    return json_data["success"]

def join_room(code):
    client = Client(HTTP_USER_AGENT='Mozilla/5.0')
    response = client.get("/" + code)
    json_data = json.loads(response.content)
    return json_data["success"]

@pytest.mark.django_db
@pytest.mark.asyncio
async def test_websocket_consumer():
    # Mock game test.
    game_code = create_room()
    for _ in range(num_players):
        game_type = join_room(game_code)
    application = URLRouter([url(r'^president/(?P<room_code>[A-Z]{5})$', GameConsumer)])

    communicators = []

    names = ["Alvin", "Bob", "Cathy", "Deacon"]
    
    room = Room.objects.get(code=game_code)

    for i in range(num_players):
        communicator = WebsocketCommunicator(application, "/{}/{}".format(game_type, game_code))
        communicators.append(communicator)
        connected = await communicator.connect()
        # Test that a connection is made.
        assert connected

    for i in range(num_players):
        await communicators[i].send_json_to({"type": "name", "name": names[i]})
        await asyncio.sleep(time)  # Wait for the database to be updated.
        # Check if the player name is registered.
        assert room.game.players.get(name=names[i]).name
        await asyncio.sleep(time)  # Wait for the database to be updated.
        await communicators[i].send_json_to({"type": "ready"})
        await asyncio.sleep(time)  # Wait for the database to be updated.
        if i != num_players - 1:
            # Check if the player is ready.
            # When the last player is ready, all of their ready states are reset.
            assert room.game.players.get(name=names[i]).ready == True

    room = Room.objects.get(code=game_code)
    await asyncio.sleep(time)  # Wait for the database to be updated.
    # Check if the game has started.
    assert room.ingame == True

    # For now, change the handout of players so they aren't random.
    # Otherwise it'll be too hard to test.
    # Only use clubs cards and jokers.

    cards = ["3", "4", "5", "6", "7", "8", "9", "Q", "K", "A", "2", "X"]

    for i in range(num_players):
        player = room.game.players.get(name=names[i])
        player.num_cards = int(12 / num_players)
        player.C = ""
        player.X = 0
        for j in range(int(12 / num_players)):
            card = cards[i + num_players*j]
            if card != "X":
                player.C = player.C + card
            else:
                player.X = player.X + 1
        
        if i == 0:
            player.current_turn = True
        player.save()
    
    await asyncio.sleep(5)

    i = 0
    # Starts the match
    # The player must send the 3 of clubs first.
    await communicators[i].send_json_to({"type": "game_move", "move": "c3"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()

    # Successful card play.
    assert resp["current_card"] == "c3"
    # The same player cannot play another card as it isn't their turn.
    await communicators[i].send_json_to({"type": "game_move", "move": "c7"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    assert resp["message"] == "It isn't your turn yet!"

    i = 1
    # The second player plays their card 8.
    await communicators[i].send_json_to({"type": "game_move", "move": "c8"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["current_card"] == "c8"
    
    i = 2
    # Third player cannot play a card lower than the current.
    await communicators[i].send_json_to({"type": "game_move", "move": "c5"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["message"] == 'You cannot make this move!'

    # The third player plays their card 2.
    await communicators[i].send_json_to({"type": "game_move", "move": "c2"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["current_card"] == "c2"

    i = 3
    # The fourth player skips their turn.
    await communicators[i].send_json_to({"type": "game_move", "move": "skip"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful skip.
    assert resp["players"][names[i]]["skip_turn"] == True

    i = 0
    # The first player skips their turn.
    await communicators[i].send_json_to({"type": "game_move", "move": "skip"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful skip.
    assert resp["players"][names[i]]["skip_turn"] == True

    i = 1
    # The second player skips their turn.
    await communicators[i].send_json_to({"type": "game_move", "move": "skip"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    i = 2
    # The third player is the winner.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    assert resp["players"][names[i]]["current_turn"] == True
    assert resp["current_card"] == ""
    # The third player plays their card.
    await communicators[i].send_json_to({"type": "game_move", "move": "c9"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["current_card"] == "c9"

    i = 3
    # The fourth player plays a joker, winning the round.
    await communicators[i].send_json_to({"type": "game_move", "move": "xx"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["players"][names[i]]["current_turn"] == True
    assert resp["current_card"] == ""

    # The fourth player plays a 6
    await communicators[i].send_json_to({"type": "game_move", "move": "c6"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["current_card"] == "c6"

    i = 0
    # The first player skips
    await communicators[i].send_json_to({"type": "game_move", "move": "skip"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful skip.
    assert resp["players"][names[i]]["skip_turn"] == True

    i = 1
    # The second player plays an A
    await communicators[i].send_json_to({"type": "game_move", "move": "ca"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["current_card"] == "ca"

    i = 2
    # The third player skips
    await communicators[i].send_json_to({"type": "game_move", "move": "skip"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful skip.
    assert resp["players"][names[i]]["skip_turn"] == True

    # Test a chat message here
    await communicators[i].send_json_to({"type": "chat", "message": "TEST"})
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    assert resp["type"] == "room_message"
    assert resp["message"] == "{}: TEST".format(names[i])

    i = 3
    # The fourth player skips
    await communicators[i].send_json_to({"type": "game_move", "move": "skip"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    i = 1
    # The second player is the winner
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    assert resp["players"][names[i]]["current_turn"] == True
    assert resp["current_card"] == ""

    # Second player plays a 4
    await communicators[i].send_json_to({"type": "game_move", "move": "c4"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["current_card"] == "c4"
    # Second player has an empty hand, they are President
    assert resp["players"][names[i]]["role"] == "PR"

    i = 2
    # Third player plays a 5
    await communicators[i].send_json_to({"type": "game_move", "move": "c5"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    assert resp["current_card"] == "c5"
    # Third player has an empty hand, they are Vice-President
    assert resp["players"][names[i]]["role"] == "VPR"

    i = 3
    # Fourth player plays a queen
    await communicators[i].send_json_to({"type": "game_move", "move": "cq"})
    await asyncio.sleep(time)  # Wait for the database to be updated.
    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()
    # Successful card play.
    # Second player has an empty hand, they are Vice-Scum
    assert resp["players"][names[i]]["role"] == "VSC"

    i = 0
    # Because there is only one player left, they are scum.
    assert resp["players"][names[i]]["role"] == "SC"

    # All players ready up again, next game starts
    for i in range(num_players):
        await communicators[i].send_json_to({"type": "ready"})
        await asyncio.sleep(time)  # Wait for the database to be updated.

    # Once everyone is ready, next round starts.
    assert Room.objects.get(code=game_code).game.round_num == 2

    while await communicators[i].receive_nothing() is False:
        resp = await communicators[i].receive_json_from()

    # The president should be the starting player.
    assert resp["players"][names[1]]["current_turn"] == True
