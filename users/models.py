from django.db import models
from django.contrib.auth.models import AbstractUser

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

    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to="users/profile_pictures/",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_format],
    )
    cover_photo = models.ImageField(
        upload_to="users/cover_photos/",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_format],
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
