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
    date_created = models.DateTimeField(auto_now_add=True)

    def get_game_type(self):
        return dict(Room.GAMECHOICES)[int(self.game_type)].lower()
