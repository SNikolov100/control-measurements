from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .access import get_access_state


class ReadyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if get_access_state(user) != 'ready':
            raise AuthenticationFailed('Account is not ready for API access.')

        return super().get_token(user)