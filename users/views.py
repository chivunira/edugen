from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_205_RESET_CONTENT
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserRegistrationSerializer
from .utils import send_verification_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from assessments.models import Assessment, AssessmentSummary
from edugen_tutor_model.models import Topic
from django.db.models import Count, Avg
from .serializers import UserProfileSerializer, UserProfileUpdateSerializer
import logging
from rest_framework.parsers import MultiPartParser, FormParser


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


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get assessment summaries
        topic_summaries = AssessmentSummary.objects.filter(user=user)

        # Calculate overall statistics
        overall_stats = topic_summaries.aggregate(
            total_assessments=Count('total_attempts'),
            average_score=Avg('average_score')
        )

        # Get topic-wise performance
        topic_performance = []
        for summary in topic_summaries:
            recent_assessments = Assessment.objects.filter(
                user=user,
                topic=summary.topic,
                status='completed'
            ).order_by('-end_time')[:5]

            topic_performance.append({
                'topic_id': summary.topic.id,
                'topic_name': summary.topic.name,
                'subject_name': summary.topic.subject.name,
                'total_attempts': summary.total_attempts,
                'best_score': float(summary.best_score),
                'average_score': float(summary.average_score),
                'last_attempt_date': summary.last_attempt_date,
                'recent_assessments': [{
                    'id': assessment.id,
                    'score': float(assessment.total_score),
                    'date': assessment.end_time
                } for assessment in recent_assessments]
            })

        # Get topics with no attempts
        attempted_topic_ids = topic_summaries.values_list('topic__id', flat=True)
        unattempted_topics = Topic.objects.exclude(
            id__in=attempted_topic_ids
        ).values('id', 'name', 'subject__name')

        response_data = {
            'user': UserProfileSerializer(user).data,
            'overall_stats': {
                'total_assessments': overall_stats['total_assessments'] or 0,
                'average_score': float(overall_stats['average_score'] or 0),
            },
            'topic_performance': topic_performance,
            'unattempted_topics': list(unattempted_topics)
        }

        return Response(response_data)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request):
        try:
            serializer = UserProfileUpdateSerializer(
                request.user,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                # Return full user profile after update
                profile_serializer = UserProfileSerializer(request.user)
                return Response(profile_serializer.data, status=HTTP_200_OK)

            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return Response(
                {'error': 'Failed to update profile'},
                status=HTTP_400_BAD_REQUEST
            )