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
    for i, p in enumerate(game.players.all()):
        if p.channel_name == player.channel_name:
            index = i
    for index in range(index + len(game.players.all())):
        if game.players.all()[(index+1)%len(game.players.all())].skip_turn == False:
            game.players.all()[(index+1)%len(game.players.all())].current_turn = True
            game.players.all()[(index+1)%len(game.players.all())].save()
            break

def skip_turn(player, game):
    # Set the player skip state to true.
    player.skip_turn = True
    player.current_turn = False
    player.save()

    # Find the next player
    next_player(room)

    # Sees if there are any more skippable players.
    remaining = game.players.all().filter(skip_turn=False)
    if len(remaining) > 1:
        # There are still more players in the round
        return False

    # Return the winner
    return remaining[0]

def new_game(game):
    # Reset player states.
    for p in game.players.all():
        p.skip_turn = False
        p.ready = False
        p.current_turn = False
        p.num_cards = -1
        p.H = ""
        p.D = ""
        p.C = ""
        p.S = ""
        p.X = 0
        p.save()

    # Reset game state
    game.current_card = ""
    game.jokers_remaining = 2
    game.round = game.round + 1
    game.save()

def reset_roles(game):
    for p in game.players.all():
        p.role = ""
        p.ready = False
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
    # Order of card values is 34567890JKQA2X
    card_order = "34567890JKQA2X"
    # Check if the player actually does have the card.
    # Also acts as a cheat guard.
    card_type = move[0].upper()
    card_num = move[1].upper()
    if card_type == "H":
        if card_num not in player.H: return -1
    elif card_type == "D":
        if card_num not in player.D: return -1
    elif card_type == "C":
        if card_num not in player.C: return -1
    elif card_type == "S":
        if card_num not in player.S: return -1
    elif card_type == "X":
        if player.X < 1: return -1

    # Check if this is the very first card of the very first round.
    # This should always be the 3 of clubs
    if game.round_num == 1 and "3" in player.C and move.upper() != "C3":
        return -1
    # Check if the card played is higher than the current card.
    if card_order.index(card_num) > card_order.index(game.current_card[:1]) or game.current_card == "":
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

        skip_state = True

        # If the player has no more cards, set their skip state to True and give the required role.
        if player.card_num == 0:
            player.skip_turn = True

            # Game only allows a maximum of 4 players.
            # Roles depend on the number of players.
            roles = ['PR']
            if len(players) == 4:
                roles += ['VPR', 'VSC']
            elif len(players) == 3:
                roles += ['NOR']
            roles += ['SC']

            player.role = roles[len(players.filter(card_num<1)) - 1]
            player.save()

        remaining = game.players.all().filter(skip_turn=False)
        if len(remaining) < 2 or (card_type == "X" or (card_num == 2 and game.jokers_remaining == 0)):
            # There is just one more player. OR the highest card was played.
            reset_round(game)
            if player.card_num == 0:
                next_player(player,game) 

        return player.card_num
    return -1

def game_winner(game):
    remaining = game.players.all().filter(card_num>0)
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
        if j < 54 % len(players):
            offset = 1
        for k in range(54//len(players) + offset):
            card = deck.pop()
            # Add the card to the Player object.
            if card[0] == "H":
                i.H = i.H + card[1]
            elif card[0] == "D":
                i.D = i.D + card[1]
            elif card[0] == "C":
                i.C = i.C + card[1]
            elif card[0] == "S":
                i.S = i.S + card[1]
            elif card[0] == "X":
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
        player = game.players.all().get(role="SC")
        # There is a scum. They are the starting player.
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
    