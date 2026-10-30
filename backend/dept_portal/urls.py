from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from resources import api_views
from resources import template_views

urlpatterns = [
    # Django Admin (Figure 6.2.4)
    path('admin/', admin.site.urls),

    # HTML Template Views (Report Figures 6.2.1, 6.2.2, 6.2.3, 6.2.5, 6.2.6)
    path('', template_views.home_view, name='home'),
    path('login/', template_views.login_view, name='login'),
    path('register/', template_views.register_view, name='register'),
    path('logout/', template_views.logout_view, name='logout'),
    path('dashboard/', template_views.dashboard_view, name='dashboard'),
    path('faculty/dashboard/', template_views.faculty_dashboard_view, name='faculty_dashboard'),
    path('student/dashboard/', template_views.student_dashboard_view, name='student_dashboard'),
    path('resources/', template_views.resource_list_view, name='resource_list'),
    path('upload/', template_views.upload_resource_view, name='upload_resource'),
    path('request-resource/', template_views.request_resource_view, name='request_resource'),
    path('profile/', template_views.profile_view, name='profile'),

    # REST APIs (for localhost:5173 React Frontend)
    # Auth APIs
    path('api/auth/login', api_views.api_login, name='api_login'),
    path('api/auth/register', api_views.api_register, name='api_register'),
    path('api/auth/me', api_views.api_get_current_user, name='api_get_current_user'),

    # Resource APIs
    path('api/resources', api_views.api_resources_list, name='api_resources_list'),
    path('api/resources/upload', api_views.api_resource_upload, name='api_resource_upload'),
    path('api/resources/my-uploads', api_views.api_my_uploads, name='api_my_uploads'),
    path('api/resources/<int:pk>', api_views.api_resource_detail, name='api_resource_detail'),
    path('api/resources/<int:pk>/delete', api_views.api_resource_delete, name='api_resource_delete_alt'),
    path('api/resources/<int:pk>/approve', api_views.api_resource_approve, name='api_resource_approve'),
    path('api/resources/<int:pk>/comments', api_views.api_resource_comments, name='api_resource_comments'),
    path('api/resources/download/<str:file_name>', api_views.api_download_file, name='api_download_file'),

    # Subject APIs
    path('api/subjects', api_views.api_subjects_list, name='api_subjects_list'),
    path('api/subjects/semester/<int:sem>', api_views.api_subjects_by_semester, name='api_subjects_by_semester'),
    path('api/subjects/<int:pk>', api_views.api_subject_delete, name='api_subject_delete'),
    path('api/subjects/<int:pk>/enroll', api_views.api_subject_enroll, name='api_subject_enroll'),
    path('api/subjects/<int:pk>/unenroll', api_views.api_subject_unenroll, name='api_subject_unenroll'),
    path('api/subjects/my-courses', api_views.api_my_courses, name='api_my_courses'),
    path('api/subjects/my-semester', api_views.api_update_my_semester, name='api_update_my_semester'),

    # Workstation APIs
    path('api/workstations', api_views.api_workstations_list, name='api_workstations_list'),
    path('api/workstations/book', api_views.api_workstations_book, name='api_workstations_book'),
    path('api/workstations/my-bookings', api_views.api_my_bookings, name='api_my_bookings'),
    path('api/workstations/all-bookings', api_views.api_all_bookings, name='api_all_bookings'),
    path('api/workstations/bookings/<int:pk>/status', api_views.api_update_booking_status, name='api_update_booking_status'),

    # Stats API
    path('api/stats', api_views.api_stats, name='api_stats'),

    # Admin APIs
    path('api/admin/users', api_views.api_admin_users, name='api_admin_users'),
    path('api/admin/users/<int:pk>/role', api_views.api_admin_user_role, name='api_admin_user_role'),
    path('api/admin/users/<int:pk>/status', api_views.api_admin_user_status, name='api_admin_user_status'),
    path('api/admin/users/<int:pk>', api_views.api_admin_user_delete, name='api_admin_user_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
