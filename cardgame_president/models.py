from django.db import models

# Create your models here.

class Game(models.Model):
    code = models.CharField(max_length=5, primary_key=True)
    round_num = models.IntegerField(default=0)
    pres = models.CharField()
    vice_pres = models.CharField()
    scum = models.CharField()
    vice_scum = models.CharField()
    current_card = models.IntegerField()
    current_turn = models.CharField()
    order_up = models.BooleanField()
    consecutive = models.BooleanField()