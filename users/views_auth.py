# views_auth.py
from rest_framework import serializers, generics, permissions
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from utils.custom_response import success_response, error_response
from .serializers import LoginSerializer

User = get_user_model()

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)

        # Fetch user using email and password
        user = authenticate(request=self.context.get('request'), email=attrs["email"], password=attrs["password"])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return success_response(
            data=response.data,
            message="Login successful"
        )
