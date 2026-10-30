from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import (
    Resource,
    Subject,
    Department,
    UserProfile,
    ResourceRequest,
    ResourceComment,
    LabWorkstation,
    WorkstationBooking
)
import os
import re
from django.conf import settings
from django.utils import timezone

def home_view(request):
    total_resources = Resource.objects.filter(is_approved=True).count()
    total_users = User.objects.count()
    total_subjects = Subject.objects.count()
    featured_resources = Resource.objects.filter(is_approved=True).order_by('-download_count')[:6]
    context = {
        'total_resources': total_resources,
        'total_users': total_users,
        'total_subjects': total_subjects,
        'featured_resources': featured_resources,
    }
    return render(request, 'resources/home.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Find user by username or email
        user_obj = User.objects.filter(username__iexact=identifier).first()
        if not user_obj:
            user_obj = User.objects.filter(email__iexact=identifier).first()

        if user_obj and user_obj.check_password(password):
            login(request, user_obj)
            messages.success(request, f"Welcome back, {user_obj.first_name or user_obj.username}!")
            
            profile = getattr(user_obj, 'profile', None)
            role = profile.role if profile else 'ROLE_STUDENT'
            if role == 'ROLE_FACULTY':
                return redirect('faculty_dashboard')
            elif role == 'ROLE_ADMIN' and user_obj.is_staff:
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('faculty_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'resources/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip() or username
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        role = request.POST.get('role', 'ROLE_STUDENT')
        identifier = request.POST.get('identifier', '').strip()
        semester = request.POST.get('semester', '1')

        if password != password_confirm:
            messages.error(request, "Passwords do not match!")
            return render(request, 'resources/register.html')

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username is already taken!")
            return render(request, 'resources/register.html')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email is already registered!")
            return render(request, 'resources/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = full_name
        user.save()

        try:
            sem_val = int(semester)
        except ValueError:
            sem_val = 1

        profile = UserProfile.objects.create(
            user=user,
            role=role,
            full_name=full_name,
            identifier=identifier,
            current_semester=sem_val,
        )

        if role == 'ROLE_STUDENT':
            subjects = Subject.objects.filter(semester=sem_val)
            profile.enrolled_subjects.set(subjects)

        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('dashboard')

    return render(request, 'resources/register.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

@login_required
def dashboard_view(request):
    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'ROLE_STUDENT'
    if role in ['ROLE_FACULTY', 'ROLE_ADMIN']:
        return redirect('faculty_dashboard')
    return redirect('student_dashboard')

@login_required
def faculty_dashboard_view(request):
    profile = getattr(request.user, 'profile', None)
    my_uploads = Resource.objects.filter(uploaded_by=request.user).order_by('-created_at')
    upload_count = my_uploads.count()
    subjects = Subject.objects.all().order_by('semester', 'code')

    context = {
        'profile': profile,
        'my_uploads': my_uploads,
        'upload_count': upload_count,
        'subjects': subjects,
    }
    return render(request, 'resources/faculty_dashboard.html', context)

@login_required
def student_dashboard_view(request):
    profile = getattr(request.user, 'profile', None)
    
    # Available resources
    resources = Resource.objects.filter(is_approved=True)
    if profile and profile.enrolled_subjects.exists():
        resources = resources.filter(subject__in=profile.enrolled_subjects.all())
    elif profile and profile.current_semester:
        resources = resources.filter(semester=profile.current_semester)
    
    # Also grab recent approved resources so student has ample items
    all_approved = Resource.objects.filter(is_approved=True).order_by('-created_at')[:8]

    my_requests = ResourceRequest.objects.filter(user=request.user).order_by('-requested_at')

    context = {
        'profile': profile,
        'resources': resources if resources.exists() else all_approved,
        'all_approved': all_approved,
        'my_requests': my_requests,
    }
    return render(request, 'resources/student_dashboard.html', context)

@login_required
def resource_list_view(request):
    query = request.GET.get('q', '').strip()
    sem = request.GET.get('sem', '').strip()
    cat = request.GET.get('category', '').strip()

    qs = Resource.objects.filter(is_approved=True)
    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(subject__name__icontains=query) |
            Q(subject__code__icontains=query)
        )
    if sem:
        try:
            qs = qs.filter(semester=int(sem))
        except ValueError:
            pass
    if cat and cat != 'ALL':
        qs = qs.filter(category=cat)

    subjects = Subject.objects.all().order_by('semester', 'code')
    context = {
        'resources': qs,
        'query': query,
        'selected_sem': sem,
        'selected_cat': cat,
        'subjects': subjects,
    }
    return render(request, 'resources/resource_list.html', context)

@login_required
def upload_resource_view(request):
    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'ROLE_STUDENT'
    if role not in ['ROLE_ADMIN', 'ROLE_FACULTY']:
        messages.error(request, "Only faculty and admin can upload resources.")
        return redirect('dashboard')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        subject_id = request.POST.get('subject')
        category = request.POST.get('category', 'LECTURE_NOTES')
        semester = request.POST.get('semester', '1')
        tags = request.POST.get('tags', '').strip()
        file_obj = request.FILES.get('file')

        if not title or not file_obj:
            messages.error(request, "Title and File are required!")
            return redirect('upload_resource')

        cleaned_name = re.sub(r'[^a-zA-Z0-9.-]', '_', file_obj.name)
        stored_name = f"res_{int(timezone.now().timestamp())}_{cleaned_name}"

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        file_path = os.path.join(settings.MEDIA_ROOT, stored_name)
        with open(file_path, 'wb+') as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

        subject = Subject.objects.filter(id=subject_id).first() if subject_id else None
        ext = cleaned_name.split('.')[-1].lower() if '.' in cleaned_name else 'pdf'
        is_admin = role == 'ROLE_ADMIN'

        Resource.objects.create(
            title=title,
            description=description,
            subject=subject,
            category=category,
            semester=int(semester) if semester else (subject.semester if subject else 1),
            tags=tags,
            file_name=stored_name,
            original_file_name=file_obj.name,
            file_download_uri=f"/api/resources/download/{stored_name}",
            file_type=ext,
            file_size=file_obj.size,
            uploaded_by=request.user,
            is_approved=is_admin,
            status='Approved' if is_admin else 'Pending'
        )

        messages.success(request, "Resource uploaded successfully!" + (" It is now live." if is_admin else " Awaiting admin approval."))
        return redirect('faculty_dashboard')

    subjects = Subject.objects.all().order_by('semester', 'code')
    return render(request, 'resources/upload_resource.html', {'subjects': subjects})

@login_required
def request_resource_view(request):
    if request.method == 'POST':
        resource_name = request.POST.get('resource_name', '').strip()
        subject = request.POST.get('subject', '').strip()
        semester = request.POST.get('semester')
        description = request.POST.get('description', '').strip()

        if not resource_name:
            messages.error(request, "Resource name is required.")
            return redirect('request_resource')

        sem_val = None
        if semester:
            try:
                sem_val = int(semester)
            except ValueError:
                pass

        ResourceRequest.objects.create(
            user=request.user,
            resource_name=resource_name,
            subject=subject,
            semester=sem_val,
            description=description,
            status='PENDING'
        )
        messages.success(request, f"Resource request for '{resource_name}' submitted to faculty!")
        return redirect('student_dashboard')

    return render(request, 'resources/request_resource.html')

@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if full_name:
            request.user.first_name = full_name
            if profile:
                profile.full_name = full_name
        if email:
            request.user.email = email
        if password:
            request.user.set_password(password)
        
        request.user.save()
        if profile:
            profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'resources/profile.html', {'profile': profile})
