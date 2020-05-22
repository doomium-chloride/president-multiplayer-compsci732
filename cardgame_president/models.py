from django.db import models
from room_manager.models import Room

# Create your models here.

class Game(models.Model):
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name="room")
    current_card = models.CharField(max_length=2, default="")
    jokers_remaining = models.IntegerField()

class Player(models.Model):
    PRESIDENT = 'PR'
    VICE_PRESIDENT = 'VPR'
    NORMAL = 'NOR'
    VICE_SCUM = 'VSC'
    SCUM = 'SC'
    ROLE_CHOICES = (
        (PRESIDENT, 'President'),
        (VICE_PRESIDENT, 'Vice President'),
        (NORMAL, 'Normal'),
        (VICE_SCUM, 'Vice Scum'),
        (SCUM, 'Scum'),
    )
    name = models.CharField(max_length=12, default="...", blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="players")
    channel_name = models.CharField(max_length=30)
    ready = models.BooleanField(default=False)
    current_turn = models.BooleanField(default=False)
    skip_turn = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, max_length=3, default='', blank=True)
    # Number of cards a player has left
    num_cards = models.IntegerField(default=-1)
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