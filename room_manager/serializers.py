from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)
    game = serializers.IntegerField()
    players = serializers.IntegerField()
    max_players = serializers.IntegerField()
    ingame = serializers.BooleanField()
    date_created = serializers.DateTimeField()

    def create(self, validated_data):
        return Room.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.players = validated_data.get('players', instance.players)
        instance.ingame = validated_data.get('ingame', instance.ingame)
        instance.save()
        return instance