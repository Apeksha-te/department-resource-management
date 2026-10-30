from django.contrib import admin
from .models import (
    Department,
    Category,
    Subject,
    UserProfile,
    Resource,
    ResourceRequest,
    ResourceComment,
    LabWorkstation,
    WorkstationBooking
)

admin.site.site_header = "Admin"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Admin Portal"

@admin.register(ResourceRequest)
class ResourceRequestAdmin(admin.ModelAdmin):
    list_display = ('resource_name', 'user', 'subject', 'semester', 'status', 'requested_at')
    list_filter = ('status', 'semester')
    search_fields = ('resource_name', 'user__username', 'description')
    list_editable = ('status',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'semester', 'subject', 'status', 'uploaded_by', 'created_at')
    list_filter = ('status', 'is_approved', 'category', 'semester')
    search_fields = ('title', 'description', 'tags', 'uploaded_by__username')
    list_editable = ('status',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'full_name', 'identifier', 'current_semester', 'is_active_user')
    list_filter = ('role', 'current_semester', 'is_active_user')
    search_fields = ('user__username', 'user__email', 'full_name', 'identifier')
    list_editable = ('role', 'is_active_user')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('dept_name', 'code', 'location', 'contact_number')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'semester', 'credits')
    list_filter = ('semester',)
    search_fields = ('code', 'name')

@admin.register(LabWorkstation)
class LabWorkstationAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'status', 'ip_address')
    list_filter = ('status',)
    search_fields = ('name', 'identifier')

@admin.register(WorkstationBooking)
class WorkstationBookingAdmin(admin.ModelAdmin):
    list_display = ('workstation', 'user', 'purpose', 'status', 'start_time', 'end_time')
    list_filter = ('status',)
    search_fields = ('workstation__identifier', 'user__username', 'purpose')
    list_editable = ('status',)

@admin.register(ResourceComment)
class ResourceCommentAdmin(admin.ModelAdmin):
    list_display = ('resource', 'user', 'comment_text', 'created_at')
    search_fields = ('resource__title', 'user__username', 'comment_text')
