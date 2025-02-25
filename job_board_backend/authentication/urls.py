from django.urls import path
from .views import RegisterView, UserDetailView, UserProfileView, logout

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout, name='logout'),
    # path('me/', UserDetailView.as_view(), name='user_detail'),
    path('profile/', UserProfileView.as_view(), name='user_detail'),
]