from django.db import models
from authentication.models import User  # Import custom User model
import uuid

class Location(models.Model):
    """
    Model representing a location for job postings.

    Stores unique combinations of country, city, and address, all required fields.
    Automatically created by the JobPostingSerializer during job creation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.CharField(max_length=100)  # Required
    city = models.CharField(max_length=100)     # Required
    address = models.CharField(max_length=255)  # Required
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the location."""
        return f"{self.address}, {self.city}, {self.country}"

    class Meta:
        """Metadata for the Location model."""
        unique_together = ('country', 'city', 'address')  # Ensure uniqueness
        indexes = [
            models.Index(fields=['country', 'city']),  # Optimize filtering
        ]

class JobPosting(models.Model):
    """
    Model representing a job posting.

    Stores job details with a category as an ENUM (choices) and a location as a ForeignKey,
    linked to the user (admin) who posted it. The location is automatically created
    from required location_country, location_city, and location_address fields during creation.
    """
    JOB_TYPES = (
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('contract', 'Contract'),
        ('remote', 'Remote'),
    )
    
    CATEGORY_CHOICES = (
        ('tech', 'Tech'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jobs'
    )
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    posted_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='jobs_posted'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """Return a string representation of the job posting."""
        return self.title

    class Meta:
        """Metadata for the JobPosting model."""
        indexes = [
            models.Index(fields=['category']),  # Index on category ENUM
            models.Index(fields=['location']),  # Index on location ForeignKey
            models.Index(fields=['category', 'job_type']),  # Composite index
            models.Index(fields=['created_at']),  # For sorting by recency
        ]