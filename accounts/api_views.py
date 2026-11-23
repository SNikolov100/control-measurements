from rest_framework_simplejwt.views import TokenObtainPairView
from .api_serializers import ReadyTokenObtainPairSerializer


class ReadyTokenObtainPairView(TokenObtainPairView):
    serializer_class = ReadyTokenObtainPairSerializer