from django.urls import path
from .views import *

app_name = "room_manager"

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', CreateRoomView.as_view()),
    path('/<str:room_code>', JoinRoomView.as_view()),
]