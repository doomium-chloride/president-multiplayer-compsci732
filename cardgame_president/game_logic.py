from .models import Game, Player
from textwrap import wrap
from django.db.models import F
import random

def getRoomByCode(code):
    return Room.objects.get(code=code)
    
def getGameBycode(code):
    return Game.objects.get(room=Room.objects.get(code=code))

def getPlayersByCode(code):
    return Players.objects.filter(game=Game.objects.get(room=Room.objects.get(code=code)))

def skip_turn(player, game):
    # Set the player skip state to true.
    player.skip_turn = True
    player.save()
    # Sees if there are any more skippable players.
    players = getPlayersByCode(code)
    turn = game.current_turn + 1

    # While loop to find the next valid player.
    while (players.get(play_order=turn).skip_turn):
        turn = (turn + 1) % len(players)
    game.current_turn = turn
    game.save()

    count = 0
    for p in players:
        if not p.skip_turn:
            count += 1
        if count > 1:
            # More than two players still in the round.
            return False
    return True

def new_round(code):
    # Reset player skip states.
    players = getPlayersByCode(code)
    for player in players:
        player.skip_turn = False
        player.save()
    # Reset game special states.
    game = getGameByCode(code)
    game.current_card = -1
    game.save()

def play_move(move, special, player, game):
    # returned value meaning
    # -1: Invalid Move
    # 0: Player has finished their hand.
    # positive int: number of cards left in player hand.
    # Order of card values is 34567890JKQA2X
    card_order = "34567890JKQA2X"
    # Check if the player actually does have the card.
    # Also acts as a cheat guard.
    card_type = move[0]
    card_num = move[1]
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
    # Check if the card played is higher than the current card.
    if card_order.index(card_num) > card_order.index(game.current_card[:1]):
        game.current_card = move
        # Remove the card from the player's hand
        player.update(card_num=F('card_num')-1)
        if card_type == "H":
            player.H = player.H.replace(card_num, "")
        elif card_type == "D":
            player.D = player.D.replace(card_num, "")
        elif card_type == "C":
            player.C = player.C.replace(card_num, "")
        elif card_type == "S":
            player.S = player.S.replace(card_num, "")

        
        players = getPlayersByCode(code)

        # If the player has no more cards, set their skip state to True and give the required role.
        if player.card_num == 0:
            player.skip_turn = True

            # Game only allows a maximum of 4 players.
            # Roles depend on the number of players.
            roles = ['PR']
            if len(players) == 4:
                roles += ['VPR', 'VSC']
            elif len(players) == 3:
                roles += [None]
            roles += ['SC']

            player.role = roles[len(players.filter(card_num<1)) - 1]
            player.save()            

        # While loop to find the next valid player.
        while (players.get(play_order=turn).skip_turn):
            turn = (turn + 1) % len(players)
        game.current_turn = turn
        game.save()

        return player.card_num
    return -1

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
            handout += card
        i.save()
        handouts += handout

    # Reset game state
    game = getGameByCode(code)
    game.current_card = ""

    # Set the current turn to the player who has the 3 of clubs.
    for p in players:
        if "3" in p.C:
            game.current_turn = p.play_order
    game.save()

    # Return the handouts as a list of lists to the Consumer.
    return handouts
    