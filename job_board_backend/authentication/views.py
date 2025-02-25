from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User, EmployerProfile, JobSeekerProfile
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, JobSeekerProfileSerializer, EmployerProfileSerializer
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404
from drf_yasg import openapi

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

class LogoutView(generics.GenericAPIView):
    """
    API view to log out a user by blacklisting their refresh token.

    This endpoint requires JWT authentication and expects a POST request with a valid
    refresh token in the request body. Upon success, the refresh token is blacklisted,
    preventing further use and effectively logging out the user. Only authenticated
    users can access this endpoint.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Log out a user by blacklisting their refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The refresh token to blacklist",
                    example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={'application/json': {"message": "Logged out successfully"}}
            ),
            400: openapi.Response(
                description="Invalid token",
                examples={'application/json': {"error": "Invalid or missing refresh token"}}
            ),
            401: "Authentication required"
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to blacklist a refresh token.

        Args:
            request: The incoming HTTP request containing the refresh token.

        Returns:
            Response: JSON response with success message or error details.
        """
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)

        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Logout failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


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
    API view for retrieving and updating the authenticated user's profile.

    Requires JWT authentication via the Authorization header.
    Supports 'job_seeker' (JobSeekerProfile) and 'employer' (EmployerProfile) roles.
    Returns phone_number and email verification status in the response.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if not user.is_authenticated:
            raise Http404("Authentication required")  # This will trigger 401 via permissions for real requests
        if user.role == 'job_seeker':
            profile, created = JobSeekerProfile.objects.get_or_create(user=user)
            return profile
        elif user.role == 'employer':
            profile, created = EmployerProfile.objects.get_or_create(
                user=user, defaults={'company_name': f"{user.first_name}'s Company"}
            )
            return profile
        elif user.role == 'admin':
            raise Http404("Admins do not have profiles")
        raise Http404("No profile exists for this user's role")

    def get_serializer_class(self):
        user = self.request.user
        # Allow Swagger schema generation without raising exceptions
        if getattr(self, 'swagger_fake_view', False) or not user.is_authenticated:
            # Default to JobSeekerProfileSerializer for schema purposes (or choose EmployerProfileSerializer)
            return JobSeekerProfileSerializer
        if user.role == 'job_seeker':
            return JobSeekerProfileSerializer
        elif user.role == 'employer':
            return EmployerProfileSerializer
        elif user.role == 'admin':
            raise Http404("Admins do not have profiles")
        raise Http404("Invalid role for profile access")

    
    def get(self, request, *args, **kwargs):
        """Handle GET request to retrieve the user's profile."""
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update the authenticated user's profile (partial updates allowed).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="User's first name", example="Tobenna"),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="User's last name", example="Obiasor"),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description="User's phone number", example="07068669403"),
                'skills': openapi.Schema(type=openapi.TYPE_STRING, description="Skills for Job Seeker profile", example="Python, Django"),
                'resume': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY, description="Resume file for Job Seeker profile"),
                'experience': openapi.Schema(type=openapi.TYPE_STRING, description="Experience for Job Seeker profile", example="5 years"),
                'company_name': openapi.Schema(type=openapi.TYPE_STRING, description="Company name for Employer profile", example="ABCD company"),
                'website': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Website for Employer profile", example="https://abcd.com"),
            },
            description="Fields depend on role: 'job_seeker' uses skills/resume/experience, 'employer' uses company_name/website. User fields are editable."
        ),
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                examples={
                    'application/json': {
                        'job_seeker': {
                            "user": {
                                "id": "ae6e63e2-618d-4957-90b7-dba945cc3c81",
                                "first_name": "Jane",
                                "last_name": "Doe",
                                "phone_number": "1234567890",
                                "email": "jane@example.com",
                                "is_email_verified": False,
                                "role": "job_seeker",
                                
                            },
                            "skills": "Python, Django",
                            "resume": "file",
                            "experience": "5 years"
                        },
                        'employer': {
                            "user": {
                                "id": "ae6e63e2-618d-4957-90b7-dba945cc3c81",
                                "first_name": "Tobenna",
                                "last_name": "Obiasor",
                                "phone_number": "07068669403",
                                "email": "tobennaobiasor@gmail.com",
                                "is_email_verified": False,
                                "role": "employer"
                            },
                            "company_name": "ABCD company",
                            "website": None
                        }
                    }
                }
            ),
            400: "Invalid data provided",
            401: "Authentication required",
            404: "Profile not found for this role"
        }
    )
    def update(self, request, *args, **kwargs):
        """Allows partial updates to the user's profile."""
        kwargs["partial"] = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)