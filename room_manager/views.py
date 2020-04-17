from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from django.shortcuts import get_object_or_404
from .serializers import RoomSerializer
from .models import Room
import string
import random

class RoomView(APIView):

    # Create room
    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Generate a new random code and see if it exists already. If not, break loop
            while True:
                room_code = ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
                if not Room.objects.filter(code=room_code).first():
                    break
            serializer.save(code=room_code)
            content = {'success': 'Room successfully created.'}
            return Response(content)