# Multiplayer Browser Game

## Github pages

https://ben-cheng565.github.io/COMPSCI732-Group25/

## Deployed version

### Edit after 24 May 2020:

This costed one of our members $$ but it's now successfully hosted!

http://35.244.87.252/

### Non-working version

This one doesn't cost anything but it also doesn't have a backend so it doesn't work anyway.

https://president-multiplayer.herokuapp.com/

## What this is

This is a multiplayer implementation of the card game President.

## What is it built on

The backend is built using Django and Python 3.7.6
The frontend is built using React.

## How do you run it locally

### Backend

You need redis-server, so assuming you have it installed,

run 
```
sudo service redis-server start
```

after that run

```
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py runserver
```

### Frontend

The front end relies on some node modules. 
To install these node modules, run 
```
npm install
```
After the node modules are installed, run 
```
npm run
```
to start the frontend.
(I think “npm run build” is for deployment)

## How to play

### Create and joint a room

![](/readme-assets/home-page.png "Home page")

First you need to make a game room.
One game room can have 2 - 4 players.

If a game room is successfully created, a room code will be generated.
You can share that room code with the people you want to play with.

You can join the game room by entering the room code into the join game form and pressing join game.

### Enter a name

![](/readme-assets/player-name.png "Enter a name")

Once you’re in the game room, you need to enter a name. The name must not exceed 13 characters.

![](/readme-assets/ready.png "ready")

Once you enter a name and you’re ready, press the ready button.

![](/readme-assets/other-player.png "Cocoa")

The blue cards represents the other players and displays how many card each player has, except yours.

Once everyone is ready, the game will begin and the cards will be handed out.

![](/readme-assets/rize-turn.png "Rize")

If a player’s number of cards is red, it means it’s their turn. If all number of cards are white, it means it’s your turn.

At the start of the first game, the first move must be 3 clubs.

![](/readme-assets/start-card.png "c3")

## Game rules

The lowest ranked card is 3, and the highest ranked card is joker, with the second highest ranked card being 2.
When it’s your turn you must play a card that is of a higher rank than what is already placed down.

![](/readme-assets/gameplay1.png "any card Cocoa has can be placed because they're all greater than 3")

If no card is already placed down, you can place any card unless it’s the first round of the first game, which means you must place a 3 of clubs card.

If you do not have a card of higher rank to play, you must skip your turns for the round. 
Even if you do have a playable card, you can skip anytime but you will forfeit that entire round.

If everyone except one player “skips”, the player that didn’t skip wins the round and gets to place a new card down (any card in their hand). This continues until everyone except one has emptied their hand.

After one round has ended a scoreboard will popup, the one that empties their hand first will get the highest score.

You can play again if everyone presses the playa gain button.

## Chat

There is a chatbox on the right of the game field.
This will let you chat with your fellow players and give out certain announcements like who skipped their turn or if a move is not allowed.
