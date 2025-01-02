from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_205_RESET_CONTENT
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserRegistrationSerializer
from .utils import send_verification_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

import logging

logger = logging.getLogger(__name__)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                # Create inactive user
                user = serializer.save()
                user.is_active = False
                user.save()

                # Send verification email with code
                if send_verification_email(user):
                    return Response({
                        'message': 'Registration successful. Please check your email for verification code.',
                        'email': user.email
                    }, status=201)
                else:
                    raise Exception("Failed to send verification email")

            except Exception as e:
                return Response({'error': str(e)}, status=400)
        return Response({'error': serializer.errors}, status=400)


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
                'user': {
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'email': user.email,
                    'grade': user.grade,
                }
            }, status=HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'error': 'Email and verification code are required'}, status=400)

        try:
            # Add logging for debugging
            logger.info(f"Attempting to verify code for email: {email}")

            user = CustomUser.objects.filter(
                email=email,
                is_active=False
            ).first()

            if not user:
                return Response({'error': 'User not found or already verified'}, status=400)

            if user.verification_code != code:
                return Response({'error': 'Invalid verification code'}, status=400)

            # Verify user
            user.is_active = True
            user.verification_code = None
            user.save()

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Account verified successfully',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'email': user.email,
                    'grade': user.grade,
                }
            }, status=200)

        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return Response({'error': 'Verification failed'}, status=400)


class ResendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=400)

        try:
            user = CustomUser.objects.get(email=email, is_active=False)
            if send_verification_email(user):
                return Response({'message': 'New verification code sent'}, status=200)
            return Response({'error': 'Failed to send verification code'}, status=400)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


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


class UpdateGradeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        grade = request.data.get('grade')

        if not grade:
            return Response(
                {'error': 'Grade is required'},
                status=HTTP_400_BAD_REQUEST
            )

        user = request.user
        user.grade = grade
        user.save()

        return Response(
            {'message': 'Grade updated successfully'},
            status=HTTP_200_OK
        )
