from django.db import models
from room_manager.models import Room

# Create your models here.


class Game(models.Model):
    room = models.OneToOneField(
        Room, on_delete=models.CASCADE, related_name="game")
    current_card = models.CharField(max_length=2, default="", blank=True)
    jokers_remaining = models.IntegerField(default=0)
    round_num = models.IntegerField(default=0)


class Player(models.Model):
    PRESIDENT = 'PR'
    VICE_PRESIDENT = 'VPR'
    VICE_SCUM = 'VSC'
    SCUM = 'SC'
    ROLE_CHOICES = (
        (PRESIDENT, 'President'),
        (VICE_PRESIDENT, 'Vice President'),
        (VICE_SCUM, 'Vice Scum'),
        (SCUM, 'Scum'),
    )
    name = models.CharField(max_length=12, default="...", blank=True)
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="players")
    channel_name = models.CharField(max_length=30)
    score = models.IntegerField(default=0)
    ready = models.BooleanField(default=False)
    current_turn = models.BooleanField(default=False)
    skip_turn = models.BooleanField(default=False)
    role = models.CharField(
        choices=ROLE_CHOICES, max_length=3, default='', blank=True)
    # Number of cards a player has left
    num_cards = models.IntegerField(default=0)
    # Hearts
    H = models.CharField(max_length=13, default="")
    # Diamonds
    D = models.CharField(max_length=13, default="")
    # Clubs
    C = models.CharField(max_length=13, default="")
    # Spades
    S = models.CharField(max_length=13, default="")
    # Jokers
    X = models.IntegerField(default=0)
