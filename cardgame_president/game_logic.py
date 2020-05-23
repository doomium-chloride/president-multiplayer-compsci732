from .models import Game, Player
from room_manager.models import Room
from textwrap import wrap
from django.db.models import F
import random


def getRoomByCode(code):
    return Room.objects.get(code=code)


def getGameByCode(code):
    return Game.objects.get(room=Room.objects.get(code=code))


def next_player(player, game):
    player.current_turn = False
    player.save()
    players = game.players.all().order_by('id')
    for i, p in enumerate(players):
        if p.channel_name == player.channel_name:
            index = i
            break
    for j in range(1, len(players) + 1):
        if not players[(index+j) % len(players)].skip_turn:
            players[(index+j) % len(players)].current_turn = True
            players[(index+j) % len(players)].save()
            break


def skip_turn(player, game):
    # Set the player skip state to true.
    player.skip_turn = True
    player.save()

    # Find the next player
    next_player(player, game)

    # Sees if there are any more skippable players.
    remaining = game.players.filter(skip_turn=False)
    if len(remaining) > 1:
        # There are still more players in the round
        return False
    reset_round(game)
    # Return the winner
    return remaining[0]


def new_game(game):

    # Reset game state
    game.current_card = ""
    game.jokers_remaining = 2
    game.round_num = game.round_num + 1
    game.save()


def reset_roles(game):
    for p in game.players.all():
        p.role = ""
        p.ready = False
        p.skip_turn = False
        p.save()


def reset_round(game):
    for p in game.players.all():
        if p.role == "":
            p.skip_turn = False
            p.save()
    game.current_card = ""
    game.save()


def play_move(move, player, game):
    # returned value meaning
    # -1: Invalid Move
    # 0: Player has finished their hand.
    # positive int: number of cards left in player hand.
    # Order of card values is 34567890JQKA2X
    card_order = "34567890JQKA2X"
    # Check if the player actually does have the card.
    # Also acts as a cheat guard.
    card_type = move[0].upper()
    card_num = move[1].upper()
    if card_type == "H":
        if card_num not in player.H:
            return -1
    elif card_type == "D":
        if card_num not in player.D:
            return -1
    elif card_type == "C":
        if card_num not in player.C:
            return -1
    elif card_type == "S":
        if card_num not in player.S:
            return -1
    elif card_type == "X":
        if player.X < 1:
            return -1

    # Check if this is the very first card of the very first round.
    # This should always be the 3 of clubs
    if game.round_num == 1 and "3" in player.C and move.upper() != "C3":
        return -1
    # Check if the card played is higher than the current card.
    if (game.current_card == "" or
            card_order.index(card_num) >
            card_order.index(game.current_card[1])):
        game.current_card = move
        # Remove the card from the player's hand
        if card_type == "H":
            player.H = player.H.replace(card_num, "")
        elif card_type == "D":
            player.D = player.D.replace(card_num, "")
        elif card_type == "C":
            player.C = player.C.replace(card_num, "")
        elif card_type == "S":
            player.S = player.S.replace(card_num, "")
        elif card_type == "X":
            player.X = player.X - 1
            game.jokers_remaining = game.jokers_remaining - 1
            game.save()
        player.num_cards = player.num_cards - 1
        player.save()
        game.save()

        # If the player has no more cards, set their skip state to True
        # and give the required role.
        if player.num_cards == 0:
            # Game only allows a maximum of 4 players.
            # Roles depend on the number of players.
            roles = ['PR']
            if len(game.players.all()) == 4:
                roles += ['VPR', 'VSC']
            elif len(game.players.all()) == 3:
                roles += ['VPR']
            roles += ['SC']
            player.skip_turn = True
            num_winners = game.players.filter(num_cards=0)
            player.role = roles[len(num_winners) - 1]
            player.score += len(game.players.all()) - len(num_winners)
            player.save()

        remaining = game.players.filter(skip_turn=False)
        if len(remaining) < 2 or card_type == "X":
            # There is just one more non-skipped player.
            # OR the highest card was played.
            reset_round(game)
            if player.num_cards == 0:
                next_player(player, game)
            else:
                player.current_turn = True
                player.save()
        else:
            next_player(player, game)

        return player.num_cards
    return -1


def game_winner(game):
    remaining = game.players.exclude(num_cards=0)
    if len(remaining) < 2:
        # Set the last player's role to Scum
        remaining[0].role = 'SC'
        remaining[0].save()
        return True
    return False


def serve_cards(players, code):
    # Create a deck of cards, shuffled.
    deck = []
    for i in "HDCS":
        for j in "34567890JQKA2":
            deck.append(i+j)
    deck += ["XX", "XX"]
    random.shuffle(deck)

    # Create handouts per player.
    handouts = []
    for j, i in enumerate(players):
        handout = []
        offset = 0

        # Reset player states
        i.skip_turn = False
        i.ready = False
        i.current_turn = False
        i.H = ""
        i.D = ""
        i.C = ""
        i.S = ""
        i.X = 0

        if j < 54 % len(players):
            offset = 1
        for _ in range(54//len(players) + offset):
            card = deck.pop()
            # Add the card to the Player object.
            if card[0] == "H":
                i.H += card[1]
            elif card[0] == "D":
                i.D += card[1]
            elif card[0] == "C":
                i.C += card[1]
            elif card[0] == "S":
                i.S += card[1]
            else:
                i.X = i.X + 1
            handout.append(card)
        i.num_cards = 54//len(players) + offset
        i.save()
        handouts.append(handout)

    # Reset game state
    game = getGameByCode(code)
    game.current_card = ""

    # Assign the current player.
    try:
        player = game.players.get(role="PR")
        # There is a president. They are the starting player.
        player.current_turn = True
        player.save()
    except Player.DoesNotExist:
        # Find the player with the 3 of clubs.
        for p in game.players.all():
            if "3" in p.C:
                p.current_turn = True
                p.save()
                break

    # Return the handouts as a list of lists to the Consumer.
    return handouts
