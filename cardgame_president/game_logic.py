from .models import Players
import random

def serve_cards(players):
    handouts = []
    deck = []
    for i in "HDCS":
        for j in "A234567890JQK":
            deck.append(j + i)
    deck.append("X")
    deck.append("X")
    random.shuffle(deck)

    for k, i in players:
        handout = []
        h = ""
        d = ""
        c = ""
        s = ""
        x = 0
        if k < 54%len(players):
            offset = 1
        else:
            offset = 0
        for j in (54//len(players) + offset):
            card = deck.pop()
            if card[0] == "H":
                h += card[1]
            elif card[0] == "D":
                d += card[1]
            elif card[0] == "C":
                c += card[1]
            elif card[0] == "S":
                s += card[1]
            elif card[0] == "X":
                x += 1
            handout.append(card)
        i.H = h
        i.D = d
        i.C = c
        i.S = s
        i.X = X
        handouts.append(handout)
        i.save()
    return handouts

                