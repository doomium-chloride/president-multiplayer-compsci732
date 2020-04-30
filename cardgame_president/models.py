from django.db import models
from room_manager.models import Room

# Create your models here.

class Game(models.Model):
    code = models.ForeignKey('Room', on_delete=models.CASCADE)
    current_card = models.CharField(max_length=8, default="")
    current_turn = models.IntegerField(default=-1)
    order_up = models.BooleanField(default=False)
    consecutive = models.BooleanField(default=False)

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
    name = models.CharField(max_length=12, default=None)
    code = models.ForeignKey('Room', on_delete=models.CASCADE)
    channel_name = models.CharField(max_length=30, primary_key=True)
    play_order = models.IntegerField()
    skip_turn = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, max_length=3, default=None)
    H = models.CharField(max_length=13, default="")
    D = models.CharField(max_length=13, default="")
    C = models.CharField(max_length=13, default="")
    S = models.CharField(max_length=13, default="")
    W = models.IntegerField(default=0)