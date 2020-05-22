"""""""""""""""""""""""logic classes"""""""""""""""""""""""
import random


class Deck(object):

    def __init__(self):
        self.totalCards = self.createCards()

    def fetchCard(self):
        return self.totalCards.pop()

    def totalCardsNum(self):
        return len(self.totalCards)

    def createCards(self):
        cards = []
        ranks = [("Two", 15), ("Three", 3), ("Four", 4), ("Five", 5), ("Six", 6), ("Seven", 7), ("Eight", 8),
                 ("Nine", 9), ("Ten", 10), ("Jack", 11), ("Queen", 12), ("King", 13), ("Ace", 14), ("Joker", 16)]
        patterns = ["Spades", "Clubs", "Diamonds", "Hearts"]
        for value in ranks:
            if value[0] == "Joker":
                card = Card("Joker", value[1])
                cards.append(card)
                cards.append(card)
                continue
            for pattern in patterns:
                card = Card(pattern, value[1])
                cards.append(card)
        random.shuffle(cards)
        return cards


class Card(object):

    def __init__(self, pattern, value):
        self.pattern = pattern
        self.cardValue = value
        self.name = pattern + ' ' + str(value)

    def getValue(self):
        return self.cardValue

    def getPattern(self):
        return self.pattern

    def getName(self):
        return self.name


class Player(object):

    def __init__(self, name):
        ''' Initialize the player object'''
        self.name = name
        '''self.title = None'''
        self.handCards = []
        self.cardsSelected = []

    def addCard(self, card):
        '''add a card to the player'''
        self.handCards.append(card)

    def playCards(self):
        ''' Play the selected cards from player'''
        self.cardsSelected = []

    def selectCard(self, card):
        '''Select card from hand'''
        self.handCards.remove(card)
        self.cardsSelected.append(card)

    def unselectAll(self):
        '''unselect all selected cards'''
        for card in self.cardsSelected:
            self.handCards.append(card)

        self.cardsSelected = []


class Game(object):
    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.field = []
        self.currentPlayer = None
        self.playersInRound = []
        self.gameOver = False
        self.winners = []

    def addPlayer(self):
        ''' add new player
         1--add player correctly
         0--same name exists
         -1--invalid player name'''
        playerName = input("Enter a player name or press enter to stop adding more players: ")
        if playerName.strip() != '':
            for pl in self.players:
                if playerName == pl.name:
                    print('The same name already exists, please enter another one.')
                    return 0
            player = Player(playerName.strip())
            self.players.append(player)
            return 1
        else:
            print('Invalid player name, please enter again.')
            return -1

    def playerNum(self):
        return len(self.players)

    def distributeCards(self):
        ''' Distribute cards to all players '''
        while self.deck.totalCardsNum() > 0:
            for player in self.players:
                if self.deck.totalCardsNum() > 0:
                    player.addCard(self.deck.fetchCard())
        self.currentPlayer = self.players[0]
        self.playersInRound = self.players[:]

    def makeMove(self):
        '''the current player makes move'''
        valid = self.validMove()
        if valid == "burn":
            self.playerBurn()
        elif not valid:
            print("Invalid Card Selections")
            self.currentPlayer.unselectAll()
        else:
            self.field = self.currentPlayer.cardsSelected
            self.currentPlayer.playCards()
            if not self.hasPlayerWon():
                self.moveToNextPlayer()
            self.isGameOver()

    def moveToNextPlayer(self):
        '''move to next player from current player'''
        index = self.playersInRound.index(self.currentPlayer)
        if index >= len(self.playersInRound) - 1:
            self.currentPlayer = self.playersInRound[0]
        else:
            self.currentPlayer = self.playersInRound[index + 1]

    def isGameOver(self):
        '''Check if the game is over '''
        if len(self.players) == 1:
            self.gameOver = True
        else:
            self.gameOver = False

    def hasPlayerWon(self):
        ''' Remove the current player from the game if he won
        True--the player has won
        False--the player has not won'''
        player = self.currentPlayer
        if not len(self.currentPlayer.handCards):
            indexRound = self.playersInRound.index(self.currentPlayer)
            indexPlayer = self.players.index(self.currentPlayer)
            self.moveToNextPlayer()
            self.winners.append(player)
            self.playersInRound.pop(indexRound)
            self.players.pop(indexPlayer)

        return len(player.handCards) == 0

    def roundOver(self):
        '''Check if the round is over if so restart it'''
        if len(self.playersInRound) == 1:
            self.field = []
            self.playersInRound = self.players[:]

    def playerPass(self):
        ''' remove the current player from the current round if he passed'''
        self.currentPlayer.unselectAll()
        index = self.playersInRound.index(self.currentPlayer)
        self.moveToNextPlayer()
        self.playersInRound.pop(index)
        self.roundOver()

    def playerBurn(self):
        ''' The current player burned the field '''
        self.field = []
        self.currentPlayer.playCards()
        self.hasPlayerWon()
        self.isGameOver()
        self.playersInRound = self.players[:]

    def validMove(self):
        '''check if the current move is valid'''
        playerCards = self.currentPlayer.cardsSelected
        field = self.field
        firstCard = playerCards[0].cardValue
        cardNums = []

        # Check if all cards are the same number except joker
        for card in playerCards:
            if card.cardValue == 16:
                continue
            if card.cardValue not in cardNums:
                cardNums.append(card.cardValue)
        if len(cardNums) > 1:
            return False

        # check if the field is empty
        if len(field) == 0:
            return True

        # get the field card's num
        for fieldCard in field:
            if fieldCard.cardValue == 16:
                continue
            else:
                fieldCardNum = fieldCard.cardValue

        # if the cards on field are bigger than the selected cards
        if fieldCardNum > firstCard:
            return False

        # the played card is 2, then burn this round
        if firstCard == 15:
            if len(field) == len(playerCards):
                return "burn"

        # the played cards are 2 and joker, then burn this round
        if firstCard == 16:
            if len(cardNums) == 0:
                return "burn"
            elif (cardNums[0] == 15) and len(field) == len(playerCards):
                return "burn"
            else:
                return len(field) == len(playerCards)

        return firstCard >= fieldCardNum and len(field) == len(playerCards)

    def playerTurn(self):
        ''' it is current player turn and ask for a move'''
        print("enter 'pass' to pass your turn or 'unselect' to unselect all cards or ")
        selCard = input("Enter the name of the card you want to select or press Enter to stop selecting: ")
        selCard = selCard.lower()
        player = self.currentPlayer
        handCardsNum = [str(card.cardValue) for card in player.handCards]
        field = self.field
        if selCard == "unselect":
            self.currentPlayer.unselectAll()

        elif (selCard == "" and len(player.cardsSelected) != 0) or (selCard == "pass" and len(field) != 0):
            return selCard

        elif selCard in handCardsNum:
            index = handCardsNum.index(selCard)
            card = player.handCards[index]
            player.selectCard(card)
        else:
            print("INVALID CARD SELECTION")
            return -1


"""""""""""""""""""""""for testing"""""""""""""""""""""


class View(object):
    ''' The view for the game '''

    def __init__(self, game):
        '''Initializes the view '''
        self.game = game
        self.players = game.players
        self.field = game.field
        self.players_in_round = game.playersInRound
        self.winners = game.winners
        self.curr_turn = game.currentPlayer
        self.game_over = False

    def updateInfo(self):
        ''' get all the current information from the Model '''

        self.players = self.game.players
        self.field = self.game.field
        self.players_in_round = self.game.playersInRound
        self.winners = self.game.winners
        self.curr_turn = self.game.currentPlayer
        self.game_over = self.game.gameOver

    def beforeGameShow(self):
        '''Show this before you start the game'''

        print("The current players are: \n" + '\n'.join([player.name for player in self.players]))
        print("Time to add players, you must add at least two")

    def showInfo(self):
        '''show the current state of the game '''
        print([player.name for player in self.players_in_round])
        '''print ([player.name for player in self.players])'''
        print("\n\nThe current cards on the field are: \n" + "\n".join([str(card.cardValue) for card in self.field]))
        print("\n\n It's " + self.curr_turn.name + " turn:")
        cards = sorted(self.curr_turn.handCards, key=lambda card: card.cardValue)
        count = 0
        print("The following are the cards they may play: \n" + "\n".join([str(card.cardValue) for card in cards]))

        selected_cards = self.curr_turn.cardsSelected
        print("\n\nThe following are the cards they have selected: \n" + "\n".join(
            [str(card.cardValue) for card in selected_cards]))

    def showWinners(self):
        ''' Show the winners in the correct order at the end of the game '''
        print('\n'.join([player.name for player in self.winners]))


if __name__ == "__main__":
    # initialize
    game = Game()
    view = View(game)
    while len(view.players) < 3:
        view.beforeGameShow()
        game.addPlayer()
        view.updateInfo()
    game.distributeCards()
    view.updateInfo()
    view.showInfo()

    # round begin
    while not view.game_over:
        view.showInfo()
        move = game.playerTurn()
        if move == "pass":
            game.playerPass()
        elif move == "":
            game.makeMove()

        view.updateInfo()
    view.showWinners()
