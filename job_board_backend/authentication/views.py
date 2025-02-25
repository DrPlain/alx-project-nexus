from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, EmployerProfile, JobSeekerProfile
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, JobSeekerProfileSerializer, EmployerProfileSerializer

class RegisterView(generics.CreateAPIView):
    """
    API view for registering a new user.

    Accepts email, password, first_name, last_name, optional phone_number, and optional role in the request body.
    Creates a user and associated profile, returning the profile details and a success message.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Determine the profile serializer based on role
        if user.role == 'job_seeker':
            profile = JobSeekerProfile.objects.get(user=user)
            profile_serializer = JobSeekerProfileSerializer(profile)
        elif user.role == 'employer':
            profile = EmployerProfile.objects.get(user=user)
            profile_serializer = EmployerProfileSerializer(profile)
        elif user.role == 'admin':
            profile_serializer = UserSerializer(user)
        else:
            raise ValueError("Invalid role for profile creation")

        # Combine profile data with message
        response_data = profile_serializer.data
        response_data["message"] = "User registered successfully"
        return Response(response_data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def logout(request):
    """
    Log out a user by blacklisting the refresh token.

    This endpoint expects a POST request with a valid refresh token in the request data.
    When the token is successfully blacklisted, it prevents future use of the token,
    effectively logging out the user.

    Request Data:
        refresh (str): The refresh token that should be blacklisted.

    Returns:
        Response: A JSON response indicating the success or failure of the logout process.
                  On success, returns a message "Logged out successfully".
                  On failure (e.g., invalid token), returns an error message with a 400 status code.
    """
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully"})
    except:
        return Response({"error": "Invalid token"}, status=400)


class UserDetailView(generics.RetrieveAPIView):
    """
    API view for retrieving the authenticated user's profile.

    Requires JWT authentication via the Authorization header.
    Includes phone_number and email verification status in the response.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Return the currently authenticated user.

        Returns:
            User: The user instance associated with the request.
        """
        return self.request.user

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and Updating the authenticated user's profile.

    Requires JWT authentication via the Authorization header.
    Includes phone_number and email verification status in the response.
    """
    permission_classes = [IsAuthenticated]

    # def get_object(self):
    #     user = self.request.user
    #     return user.job_seeker_profile if user.job_seeker_profile else user.employer_profile

    # def get_serializer_class(self):
    #     return JobSeekerProfileSerializer if self.request.user.job_seeker_profile else EmployerProfileSerializer
    def get_object(self):
        user = self.request.user
        return getattr(user, "job_seeker_profile", None) or getattr(user, "employer_profile", None)

    def get_serializer_class(self):
        if hasattr(self.request.user, "job_seeker_profile"):
            return JobSeekerProfileSerializer
        elif hasattr(self.request.user, "employer_profile"):
            return EmployerProfileSerializer
        return None  # Handle case where no profile exists

    def update(self, request, *args, **kwargs):
        """Allows partial updates"""
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)