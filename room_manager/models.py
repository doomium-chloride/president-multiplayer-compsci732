from django.db import models

GAMES = [
    ('Pres', 'President')
]

class Room(models.Model):
    PRES = 1
    GAME_CHOICES = (
        (PRES, 'pres'),
    )
    code = models.CharField(max_length=5, primary_key=True)
    game = models.PositiveSmallIntegerField(choices=GAME_CHOICES)
    players = models.IntegerField(default=0)
    max_players = models.IntegerField()
    ingame = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code