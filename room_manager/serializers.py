from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.Serializer):
    game = serializers.CharField()
    max_players = serializers.IntegerField()

    def create(self, validated_data):
        return Room.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.players = validated_data.get('players', instance.players)
        instance.ingame = validated_data.get('ingame', instance.ingame)
        instance.save()
        return instance