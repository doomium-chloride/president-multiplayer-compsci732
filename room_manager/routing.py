from django.urls import re_path

from cardgame_president import consumers as President

websocket_urlpatterns = [
    re_path(r'^president/(?P<room_code>[A-Z]{5})$', President.GameConsumer)
]
