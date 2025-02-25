from django.urls import path
from .views import JobPostingListCreateView, JobPostingDetailView

urlpatterns = [
    path('', JobPostingListCreateView.as_view(), name='job_list_create'),
    path('<uuid:pk>/', JobPostingDetailView.as_view(), name='job_detail'),
]