from django.contrib import admin
from relationships.models import Follow


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("follower__username", "following__username")
    ordering = ("-created_at",)

    actions = ["approve_requests", "reject_requests"]

    def approve_requests(self, request, queryset):
        """Approve selected follow requests"""
        updated = 0
        for follow in queryset.filter(is_approved=False):
            follow.approve()
            updated += 1
        self.message_user(request, f"{updated} follow requests approved.")

    approve_requests.short_description = "Approve selected follow requests"

    def reject_requests(self, request, queryset):
        """Reject selected follow requests"""
        count = 0
        for follow in queryset.filter(is_approved=False):
            follow.reject()
            count += 1
        self.message_user(request, f"{count} follow requests rejected.")

    reject_requests.short_description = "Reject selected follow requests"
