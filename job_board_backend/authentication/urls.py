from django.urls import path
from .views import RegisterView, UserProfileView, LogoutView, VerifyEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='user_detail'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
]