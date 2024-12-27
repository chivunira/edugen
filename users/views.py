from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_205_RESET_CONTENT
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserRegistrationSerializer
from .utils import send_activation_email
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated


class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Set user as inactive until email verification
            user.is_active = False
            user.save()
            send_activation_email(user, request)
            return Response(
                {'message': 'User registered successfully'},
                status=HTTP_201_CREATED
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            if not user.is_active:
                return Response({'error': 'User account is not activated. Please activate your account via the email sent to you.'}, status=HTTP_400_BAD_REQUEST)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'Login successful',
            }, status=HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=HTTP_400_BAD_REQUEST)


class ActivateUserView(APIView):
    def get(self, request, activation_token):
        user = CustomUser.objects.filter(is_active=False).first()
        if user and check_password(activation_token, user.activation_token):
            user.is_active = True
            # Rehash the token to invalidate it
            user.activation_token = make_password("invalidated")
            user.save()
            return Response({'message': 'User Account activated successfully'}, status=200)
        return Response({'error': 'Invalid activation token'}, status=400)


class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'User logged out successfully'}, status=HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)
