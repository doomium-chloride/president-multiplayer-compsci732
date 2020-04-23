from django.db import models

# Create your models here.

class Game(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    max_players = models.IntegerField()
    round_num = models.IntegerField(default=0)
    current_card = models.IntegerField(default=-1)
    starting_player = models.IntegerField(default=-1)
    play_stack = models.IntegerField(default=-1)
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
    name = models.CharField(max_length=10)
    game_code = models.ForeignKey('Game', on_delete=models.CASCADE)
    play_order = models.IntegerField()
    skip_turn = models.BooleanField(default=False)
    role = models.CharField(choices=ROLE_CHOICES, max_length=3)
    h = models.CharField(max_length=13)
    d = models.CharField(max_length=13)
    c = models.CharField(max_length=13)
    s = models.CharField(max_length=13)
    j = models.IntegerField()