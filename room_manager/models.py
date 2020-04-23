from django.db import models

GAMES = [
    ('Pres', 'President')
]

class Room(models.Model):
    PRESIDENT = 'PRES'
    GAME_CHOICES = (
        (PRESIDENT, 'President'),
    )
    code = models.CharField(max_length=5, primary_key=True)
    game = models.CharField(choices=GAME_CHOICES, max_length=4)
    players = models.IntegerField(default=0)
    max_players = models.IntegerField()
    ingame = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code