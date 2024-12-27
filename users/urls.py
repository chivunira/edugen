from django.urls import path
from .views import RegisterUserView, LoginUserView, ActivateUserView, LogoutUserView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('activate/<uuid:activation_token>/', ActivateUserView.as_view(), name='activate'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
]