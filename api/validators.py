from django.core.exceptions import ValidationError

def validate_file_size(file):
    """Validate that the image file size is under 30 MB."""

    # --> Skip validation for existing files (when editing in admin)
    if not hasattr(file, "size"):
        return

    max_size = 30 * 1024 * 1024  # 30 MB
    if file.size > max_size:
        raise ValidationError("Image file size must be under 30 MB.")


def validate_image_format(file):
    """Validate that the image file is PNG or JPG only."""

    # --> Skip validation for existing files (when editing in admin)
    if not hasattr(file, "content_type"):
        return

    valid_formats = ["image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in valid_formats:
        raise ValidationError("Image must be PNG or JPG format only.")
