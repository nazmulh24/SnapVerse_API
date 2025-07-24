from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit/delete it.
    Read permissions are allowed for any authenticated user.
    Write permissions are only allowed to the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the post.
        return obj.user == request.user


class IsOwnerOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to perform any action.
    Only the owner can view, edit, or delete their own objects.
    """

    def has_object_permission(self, request, view, obj):
        # All permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsPostOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission specifically for posts.
    - Anyone can view public posts
    - Only followers can view followers-only posts
    - Only the owner can view private posts
    - Only the owner can edit/delete posts
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Write permissions are only allowed to the owner
        if request.method not in permissions.SAFE_METHODS:
            return obj.user == user

        # Read permissions based on privacy settings
        if obj.privacy == "public":
            return True
        elif obj.privacy == "private":
            return obj.user == user
        elif obj.privacy == "followers":
            # Check if user follows the post owner
            if obj.user == user:
                return True
            return user.following.filter(following=obj.user, is_approved=True).exists()

        return False


class IsCommentOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for comments.
    - Anyone can view comments on posts they can see
    - Only comment owner can edit/delete comments
    """

    def has_object_permission(self, request, view, obj):
        # Write permissions are only allowed to the owner of the comment
        if request.method not in permissions.SAFE_METHODS:
            return obj.user == request.user

        # Read permissions: can view if user can see the post
        # This logic would need to be implemented based on post permissions
        return True  # For now, allow reading all comments


class IsCommentOwnerPostOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for comment deletion.
    - Anyone can view comments
    - Only comment author, post owner, or admin can delete comments
    - Only comment author can edit comments
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For DELETE: Allow comment author, post owner, or admin
        if request.method == "DELETE":
            return (
                obj.user == user  # Comment author
                or obj.post.user == user  # Post owner
                or user.is_staff  # Admin
                or user.is_superuser  # Superuser
            )

        # For other write operations (PUT, PATCH): Only comment author
        return obj.user == user
