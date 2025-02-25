from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authentication.permissions import IsAdminUser  # Custom permission
from .models import JobPosting
from .serializers import JobPostingSerializer, JobPostingCreateSerializer

class JobPostingListCreateView(generics.ListCreateAPIView):
    """
    API view to list all active job postings or create a new one.

    - GET: Returns a list of active job postings (accessible to all authenticated users).
    - POST: Creates a new job posting (restricted to admins).
    """
    queryset = JobPosting.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]  # Base permission

    def get_serializer_class(self):
        """Use JobPostingCreateSerializer for POST, JobPostingSerializer for GET."""
        if self.request.method == 'POST':
            return JobPostingCreateSerializer
        return JobPostingSerializer

    def get_permissions(self):
        """Override to restrict POST to admins only."""
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Set the posted_by field to the current user (admin) during creation.

        Args:
            serializer: The serializer instance with validated data.
        """
        serializer.save(posted_by=self.request.user)

class JobPostingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific job posting.

    - GET: Accessible to all authenticated users.
    - PUT/PATCH/DELETE: Restricted to admins.
    """
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer  # Use only the retrieval serializer
    permission_classes = [IsAuthenticated]  # Base permission

    def get_permissions(self):
        """Override to restrict PUT, PATCH, DELETE to admins only."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]