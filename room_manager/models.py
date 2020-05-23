from django.db import models

class Room(models.Model):
    GAMECHOICES = [
        (0, 'President'),
    ]
    code = models.CharField(max_length=5, primary_key=True)
    game_type = models.IntegerField(choices=GAMECHOICES)
    players = models.IntegerField(default=0)
    max_players = models.IntegerField()
    ingame = models.BooleanField(default=False)

    def get_game_type(self):
        return dict(Room.GAMECHOICES)[int(self.game_type)].lower()