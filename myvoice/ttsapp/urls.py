from django.urls import path
from .views import index, tts_azure, voices

urlpatterns = [
    path("", index, name="index"),
    path("api/tts/", tts_azure, name="tts_azure"),
    path("api/voices/", voices, name="voices"),
]
