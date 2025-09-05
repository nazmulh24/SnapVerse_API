from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

from cloudinary.models import CloudinaryField

from users.managers import CustomUserManager
from api.validators import validate_file_size, validate_image_format


class User(AbstractUser):
    """
    Custom User model that uses email for authentication and has username as additional field
    """

    username = models.CharField(
        max_length=50,
        unique=True,
        help_text="50 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[AbstractUser.username_validator],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )

    # --> Pro subscription fields for monetization
    is_pro = models.BooleanField(default=False)
    pro_subscription_start = models.DateTimeField(null=True, blank=True)
    pro_subscription_end = models.DateTimeField(null=True, blank=True)

    email = models.EmailField(unique=True)
    profile_picture = CloudinaryField(
        "image",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_format],
        folder="snapverse/users/profile_pictures",
    )
    cover_photo = CloudinaryField(
        "image",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_format],
        folder="snapverse/users/cover_photos",
    )
    bio = models.TextField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )

    RELATIONSHIP_CHOICES = [
        ("single", "Single"),
        ("in_a_relationship", "In a Relationship"),
        ("married", "Married"),
        ("divorced", "Divorced"),
        ("widowed", "Widowed"),
    ]
    relationship_status = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)

    USERNAME_FIELD = "email"  # ---> Use email instead of username
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_pro_active(self):
        """Check if pro subscription is currently active"""
        if not self.is_pro:
            return False

        if self.pro_subscription_end and timezone.now() > self.pro_subscription_end:
            # Auto-expire subscription
            self.is_pro = False
            self.save(update_fields=["is_pro"])
            return False

        return True

    @property
    def pro_days_remaining(self):
        """Get remaining days in pro subscription"""
        if not self.is_pro_active or not self.pro_subscription_end:
            return 0

        remaining = self.pro_subscription_end - timezone.now()
        return max(0, remaining.days)

    def activate_pro_subscription(self, duration_days=30):
        """Activate pro subscription for specified duration"""
        self.is_pro = True
        self.pro_subscription_start = timezone.now()
        self.pro_subscription_end = timezone.now() + timedelta(days=duration_days)
        self.save(
            update_fields=["is_pro", "pro_subscription_start", "pro_subscription_end"]
        )

    def deactivate_pro_subscription(self):
        """Deactivate pro subscription"""
        self.is_pro = False
        self.save(update_fields=["is_pro"])
