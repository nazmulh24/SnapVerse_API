from django.contrib import admin
from .models import Post, Reaction, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("user", "caption_preview", "privacy")
    list_filter = ("privacy", "created_at")
    search_fields = ("caption", "user__username", "user__email")
    ordering = ("-created_at",)

    def caption_preview(self, obj):
        if obj.caption:
            return obj.caption[:50] + "..." if len(obj.caption) > 50 else obj.caption
        return "No caption"


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "post_caption", "reaction")
    list_filter = ("reaction", "created_at")
    search_fields = ("user__username", "post__caption")
    ordering = ("-created_at",)

    def post_caption(self, obj):
        if obj.post.caption:
            return (
                obj.post.caption[:30] + "..."
                if len(obj.post.caption) > 30
                else obj.post.caption
            )
        return f"Post by {obj.post.user.username}"

    post_caption.short_description = "Post"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "post_caption",
        "text_preview",
        "is_edited",
        "parent_comment",
    )
    list_filter = ("is_edited", "created_at")
    search_fields = ("text", "user__username", "post__caption")
    ordering = ("-created_at",)

    def post_caption(self, obj):
        if obj.post.caption:
            return (
                obj.post.caption[:25] + "..."
                if len(obj.post.caption) > 25
                else obj.post.caption
            )
        return f"Post by {obj.post.user.username}"

    post_caption.short_description = "Post"

    def text_preview(self, obj):
        return obj.text[:30] + "..." if len(obj.text) > 30 else obj.text

    text_preview.short_description = "Comment"
