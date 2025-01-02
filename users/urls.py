from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    RegisterUserView,
    LoginUserView,
    LogoutUserView,
    UpdateGradeView,
    VerifyCodeView,
    ResendCodeView,
)

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('update-grade/', UpdateGradeView.as_view(), name='update-grade'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('resend-code/', ResendCodeView.as_view(), name='resend-code'),
]
