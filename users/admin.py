from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from users.models import User


class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the User model.
    """

    model = User

    list_display = ("email", "username", "get_full_name", "is_active", "is_staff")
    list_filter = ("is_staff", "is_active", "is_superuser")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "date_of_birth",
                    "gender",
                    "phone_number",
                    "location",
                )
            },
        ),
        (
            "Profile",
            {
                "fields": (
                    "username",
                    "profile_picture",
                    "cover_photo",
                    "bio",
                    "relationship_status",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_private",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important dates",
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    search_fields = ("email", "username")
    ordering = ("-date_joined",)

    readonly_fields = ("date_joined", "last_login", "updated_at")

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    get_full_name.short_description = "Full Name"

    def profile_image_tag(self, obj):
        """Display profile picture thumbnail in admin"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.profile_picture.url,
            )
        return "No Image"

    profile_image_tag.short_description = "Profile Picture"


admin.site.register(User, CustomUserAdmin)
