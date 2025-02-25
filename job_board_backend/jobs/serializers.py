from rest_framework import serializers
from .models import JobPosting, Location
from authentication.serializers import UserSerializer  # For nested user data

class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model."""
    class Meta:
        model = Location
        fields = ['id', 'country', 'city', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']

class JobPostingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a JobPosting.

    Accepts location_country, location_city, and location_address to create a Location
    instance. Used only for POST requests.
    """
    # posted_by = UserSerializer(read_only=True)
    location_country = serializers.CharField(write_only=True)
    location_city = serializers.CharField(write_only=True)
    location_address = serializers.CharField(write_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'description', 'category',
            'location_country', 'location_city', 'location_address',
            'job_type','created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create a new job posting, automatically handling location creation.

        Uses required location_country, location_city, and location_address to create
        or retrieve a Location instance.

        Args:
            validated_data (dict): Validated data from the request.

        Returns:
            JobPosting: The created job posting instance.
        """
        # Extract required location fields
        country = validated_data.pop('location_country')
        city = validated_data.pop('location_city')
        address = validated_data.pop('location_address')

        # Create or get Location instance
        location_data = {
            'country': country,
            'city': city,
            'address': address
        }
        location, _ = Location.objects.get_or_create(**location_data)
        validated_data['location'] = location

        return super().create(validated_data)

class JobPostingSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating a JobPosting.

    Excludes location input fields, showing only the location ForeignKey.
    Used for GET, PUT, and PATCH requests.
    """
    posted_by = UserSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'description', 'category', 'location',
            'job_type', 'posted_by', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'posted_by']