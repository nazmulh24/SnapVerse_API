from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit/delete it.
    Read permissions are allowed for any authenticated user.
    Write permissions are only allowed to the owner of the object.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwnerOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to perform any action.
    Only the owner can view, edit, or delete their own objects.
    """

    def has_object_permission(self, request, view, obj):
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

        if request.method not in permissions.SAFE_METHODS:
            return obj.user == user

        if obj.privacy == "public":
            return True
        elif obj.privacy == "private":
            return obj.user == user
        elif obj.privacy == "followers":
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
        if request.method not in permissions.SAFE_METHODS:
            return obj.user == request.user
        return True


class IsCommentOwnerPostOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission for comment deletion.
    - Anyone can view comments
    - Only comment author, post owner, or admin can delete comments
    - Only comment author can edit comments
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == "DELETE":
            return (
                obj.user == user
                or obj.post.user == user
                or user.is_staff
                or user.is_superuser
            )

        return obj.user == user
