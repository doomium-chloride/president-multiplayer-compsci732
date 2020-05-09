from django.db import models
from room_manager.models import Room

# Create your models here.

class Game(models.Model):
    room = models.ForeignKey('room_manager.Room', on_delete=models.CASCADE)
    current_card = models.CharField(max_length=2, default="")
    current_turn = models.IntegerField(default=-1)

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
    name = models.CharField(max_length=12, default="", blank=True)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=30, primary_key=True)
    play_order = models.IntegerField()
    skip_turn = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, max_length=3, default=None, blank=True, null=True)
    num_cards = models.IntegerField(default=-1)
    H = models.CharField(max_length=13, default="")
    D = models.CharField(max_length=13, default="")
    C = models.CharField(max_length=13, default="")
    S = models.CharField(max_length=13, default="")
    X = models.IntegerField(default=0)