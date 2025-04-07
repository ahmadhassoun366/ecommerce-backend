from rest_framework import serializers,generics, permissions
from django.contrib.auth import get_user_model,authenticate
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from utils.custom_response import success_response, error_response
from .serializers import ChangePasswordSerializer, PasswordResetSerializer, ResetPasswordSerializer
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Perform login and generate the tokens
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Fetch the user from validated data
            user = serializer.validated_data["user"]

            # Generate JWT tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            # Return the success response with tokens
            return success_response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, message="Login successful")

        except serializers.ValidationError as e:
            # Handle the case where credentials are invalid
            return error_response(
                message="The email or password is incorrect.",
                errors=e.detail
            )
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(response.data, message="User registered successfully")



class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(serializer.data, message="Profile retrieved successfully")

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(serializer.data, message="Profile updated successfully")


# Change Password View
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_password = serializer.validated_data.get('old_password')
        if not user.check_password(old_password):
            return error_response(message="Old password is incorrect")

        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return success_response(message="Password changed successfully")


# Password Reset Request View
class PasswordResetView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email=serializer.validated_data['email'])
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:8000/api/users/reset-password/{user.pk}/{token}/"

        # Send reset email
        send_mail(
            'Password Reset Request',
            f"Click the link to reset your password: {reset_link}",
            'no-reply@myapp.com',
            [user.email],
            fail_silently=False,
        )
        return success_response(message="Password reset email sent successfully.")


# Password Reset View
class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def get(self, request, user_id, token, *args, **kwargs):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return error_response(message="User not found")
        
        if not default_token_generator.check_token(user, token):
            return error_response(message="Invalid or expired token")
        
        return success_response(message="Valid token, ready to reset password.")

    def post(self, request, user_id, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return error_response(message="User not found")
        
        if not default_token_generator.check_token(user, token):
            return error_response(message="Invalid or expired token")

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return success_response(message="Password reset successfully.")