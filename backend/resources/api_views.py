import json
import os
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
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
from .auth_helper import generate_token_for_user, get_authenticated_user

def user_to_dict(user):
    profile = getattr(user, 'profile', None)
    enrolled_ids = []
    if profile:
        enrolled_ids = list(profile.enrolled_subjects.values_list('id', flat=True))
    
    return {
        'id': user.id,
        'fullName': profile.full_name if profile and profile.full_name else (user.get_full_name() or user.username),
        'email': user.email or user.username,
        'role': profile.role if profile else 'ROLE_STUDENT',
        'designation': profile.designation if profile else '',
        'identifier': profile.identifier if profile else '',
        'currentSemester': profile.current_semester if profile else 1,
        'enrolledSubjectIds': enrolled_ids,
        'active': profile.is_active_user if profile else user.is_active,
    }

def resource_to_dict(res):
    subject_dict = None
    if res.subject:
        subject_dict = {
            'id': res.subject.id,
            'code': res.subject.code,
            'name': res.subject.name,
            'semester': res.subject.semester,
            'credits': res.subject.credits,
            'description': res.subject.description,
        }

    uploader_dict = None
    if res.uploaded_by:
        prof = getattr(res.uploaded_by, 'profile', None)
        uploader_dict = {
            'id': res.uploaded_by.id,
            'fullName': prof.full_name if prof and prof.full_name else (res.uploaded_by.get_full_name() or res.uploaded_by.username),
            'email': res.uploaded_by.email or res.uploaded_by.username,
            'role': prof.role if prof else 'ROLE_FACULTY',
            'designation': prof.designation if prof else '',
        }

    return {
        'id': res.id,
        'title': res.title,
        'description': res.description,
        'subject': subject_dict,
        'category': res.category,
        'semester': res.semester,
        'tags': res.tags,
        'fileName': res.file_name,
        'originalFileName': res.original_file_name or res.file_name,
        'fileDownloadUri': res.file_download_uri or f"/api/resources/download/{res.file_name}",
        'fileType': res.file_type or 'pdf',
        'fileSize': res.file_size,
        'downloadCount': res.download_count,
        'viewCount': res.view_count,
        'approved': res.is_approved,
        'uploadedBy': uploader_dict,
        'createdAt': res.created_at.isoformat() if res.created_at else None,
        'updatedAt': res.updated_at.isoformat() if res.updated_at else None,
    }

def workstation_to_dict(ws):
    return {
        'id': ws.id,
        'name': ws.name,
        'identifier': ws.identifier,
        'specs': ws.specs,
        'status': ws.status,
        'ipAddress': ws.ip_address,
    }

def booking_to_dict(b):
    return {
        'id': b.id,
        'workstation': workstation_to_dict(b.workstation),
        'user': user_to_dict(b.user),
        'purpose': b.purpose,
        'startTime': b.start_time.isoformat() if b.start_time else None,
        'endTime': b.end_time.isoformat() if b.end_time else None,
        'status': b.status,
        'adminRemarks': b.admin_remarks,
        'createdAt': b.created_at.isoformat() if b.created_at else None,
    }

# --- AUTH APIS ---
@csrf_exempt
def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    login_identifier = data.get('email') or data.get('username')
    password = data.get('password')

    if not login_identifier or not password:
        return JsonResponse({'message': 'Missing email or password'}, status=400)

    # Try finding user by email or username
    user = User.objects.filter(email__iexact=login_identifier).first()
    if not user:
        user = User.objects.filter(username__iexact=login_identifier).first()

    if user and user.check_password(password):
        token = generate_token_for_user(user)
        user_info = user_to_dict(user)
        resp = {
            'token': token,
            'type': 'Bearer',
            **user_info
        }
        return JsonResponse(resp)
    
    return JsonResponse({'message': 'Invalid email or password'}, status=400)


@csrf_exempt
def api_register(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    full_name = data.get('fullName') or data.get('name') or ''
    email = data.get('email') or ''
    password = data.get('password') or ''
    role = data.get('role', 'ROLE_STUDENT')
    identifier = data.get('identifier', '')
    semester = data.get('currentSemester')

    if not email or not password:
        return JsonResponse({'message': 'Email and password required'}, status=400)

    username = email.split('@')[0]
    base_username = username
    c = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{c}"
        c += 1

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'message': 'User with this email already exists'}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    user.first_name = full_name
    user.save()

    try:
        sem_int = int(semester) if semester else 1
    except Exception:
        sem_int = 1

    profile = UserProfile.objects.create(
        user=user,
        role=role,
        full_name=full_name or username,
        identifier=identifier,
        current_semester=sem_int,
    )

    # If student, enroll in matching semester subjects
    if role == 'ROLE_STUDENT':
        subjects = Subject.objects.filter(semester=sem_int)
        profile.enrolled_subjects.set(subjects)

    token = generate_token_for_user(user)
    user_info = user_to_dict(user)
    return JsonResponse({
        'token': token,
        'type': 'Bearer',
        **user_info
    })


def api_get_current_user(request):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Not authenticated'}, status=401)
    return JsonResponse(user_to_dict(user))


# --- RESOURCE APIS ---
@csrf_exempt
def api_resources_list(request):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse([], safe=False)

    qs = Resource.objects.all()

    approved_param = request.GET.get('approved')
    if approved_param is not None:
        is_app = approved_param.lower() in ['true', '1']
        qs = qs.filter(is_approved=is_app)

    semester = request.GET.get('semester')
    if semester:
        try:
            qs = qs.filter(semester=int(semester))
        except ValueError:
            pass

    category = request.GET.get('category')
    if category and category != 'ALL':
        qs = qs.filter(category=category)

    subject_id = request.GET.get('subjectId')
    if subject_id:
        try:
            qs = qs.filter(subject_id=int(subject_id))
        except ValueError:
            pass

    search = request.GET.get('search')
    if search:
        search = search.strip()
        from django.db.models import Q
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(tags__icontains=search) |
            Q(subject__name__icontains=search) |
            Q(subject__code__icontains=search)
        )

    # Role constraint: student only sees enrolled subjects
    profile = getattr(user, 'profile', None)
    if profile and profile.role == 'ROLE_STUDENT':
        enrolled = profile.enrolled_subjects.all()
        if enrolled.exists():
            qs = qs.filter(subject__in=enrolled)
        elif profile.current_semester:
            qs = qs.filter(semester=profile.current_semester)

    return JsonResponse([resource_to_dict(r) for r in qs], safe=False)


def api_resource_detail(request, pk):
    res = Resource.objects.filter(pk=pk).first()
    if not res:
        return JsonResponse({'message': 'Resource not found'}, status=404)
    
    res.view_count += 1
    res.save(update_fields=['view_count'])
    return JsonResponse(resource_to_dict(res))


@csrf_exempt
def api_resource_upload(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'User must be authenticated'}, status=401)

    profile = getattr(user, 'profile', None)
    user_role = profile.role if profile else 'ROLE_STUDENT'
    if user_role not in ['ROLE_ADMIN', 'ROLE_FACULTY']:
        return JsonResponse({'message': 'Access Denied: Only faculty and admin can upload resources.'}, status=403)

    file_obj = request.FILES.get('file')
    if not file_obj:
        return JsonResponse({'message': 'File cannot be empty'}, status=400)

    title = request.POST.get('title') or file_obj.name
    description = request.POST.get('description', '')
    subject_id = request.POST.get('subjectId')
    category = request.POST.get('category', 'LECTURE_NOTES')
    semester = request.POST.get('semester')
    tags = request.POST.get('tags', '')

    subject = None
    if subject_id:
        subject = Subject.objects.filter(pk=subject_id).first()

    sem_val = 1
    if semester:
        try:
            sem_val = int(semester)
        except ValueError:
            pass
    elif subject:
        sem_val = subject.semester

    import re
    cleaned_name = re.sub(r'[^a-zA-Z0-9.-]', '_', file_obj.name)
    stored_name = f"res_{int(timezone.now().timestamp())}_{cleaned_name}"

    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    file_path = os.path.join(settings.MEDIA_ROOT, stored_name)
    with open(file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)

    ext = cleaned_name.split('.')[-1].lower() if '.' in cleaned_name else 'pdf'
    
    is_admin = user_role == 'ROLE_ADMIN'
    res = Resource.objects.create(
        title=title,
        description=description,
        subject=subject,
        category=category,
        semester=sem_val,
        tags=tags,
        file_name=stored_name,
        original_file_name=file_obj.name,
        file_download_uri=f"/api/resources/download/{stored_name}",
        file_type=ext,
        file_size=file_obj.size,
        uploaded_by=user,
        department=profile.department if profile else None,
        is_approved=is_admin,
        status='Approved' if is_admin else 'Pending'
    )

    return JsonResponse(resource_to_dict(res))


@csrf_exempt
def api_resource_delete(request, pk):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    res = Resource.objects.filter(pk=pk).first()
    if not res:
        return JsonResponse({'message': 'Resource not found'}, status=404)

    profile = getattr(user, 'profile', None)
    if profile and (profile.role == 'ROLE_ADMIN' or res.uploaded_by == user):
        res.delete()
        return JsonResponse({'message': 'Resource deleted successfully'})
    return JsonResponse({'message': 'Access denied'}, status=403)


@csrf_exempt
def api_resource_approve(request, pk):
    if request.method != 'PATCH':
        return JsonResponse({'message': 'Method not allowed'}, status=405)

    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    profile = getattr(user, 'profile', None)
    if not profile or profile.role != 'ROLE_ADMIN':
        return JsonResponse({'message': 'Only admin can approve resources'}, status=403)

    res = Resource.objects.filter(pk=pk).first()
    if not res:
        return JsonResponse({'message': 'Resource not found'}, status=404)

    approve_param = request.GET.get('approve', 'true').lower() == 'true'
    res.is_approved = approve_param
    res.status = 'Approved' if approve_param else 'Rejected'
    res.save()
    return JsonResponse(resource_to_dict(res))


def api_my_uploads(request):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    qs = Resource.objects.filter(uploaded_by=user)
    return JsonResponse([resource_to_dict(r) for r in qs], safe=False)


@csrf_exempt
def api_resource_comments(request, pk):
    res = Resource.objects.filter(pk=pk).first()
    if not res:
        return JsonResponse({'message': 'Resource not found'}, status=404)

    if request.method == 'GET':
        comments = res.comments.all().select_related('user', 'user__profile')
        resp = []
        for c in comments:
            prof = getattr(c.user, 'profile', None)
            resp.append({
                'id': c.id,
                'comment': c.comment_text,
                'createdAt': c.created_at.isoformat(),
                'user': {
                    'id': c.user.id,
                    'fullName': prof.full_name if prof and prof.full_name else (c.user.get_full_name() or c.user.username),
                    'role': prof.role if prof else 'ROLE_STUDENT',
                }
            })
        return JsonResponse(resp, safe=False)

    elif request.method == 'POST':
        user = get_authenticated_user(request)
        if not user:
            return JsonResponse({'message': 'Unauthorized'}, status=401)

        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        text = data.get('comment', '').strip()
        if not text:
            return JsonResponse({'message': 'Comment cannot be empty'}, status=400)

        comm = ResourceComment.objects.create(
            resource=res,
            user=user,
            comment_text=text
        )
        prof = getattr(user, 'profile', None)
        return JsonResponse({
            'id': comm.id,
            'comment': comm.comment_text,
            'createdAt': comm.created_at.isoformat(),
            'user': {
                'id': user.id,
                'fullName': prof.full_name if prof and prof.full_name else (user.get_full_name() or user.username),
                'role': prof.role if prof else 'ROLE_STUDENT',
            }
        })


def api_download_file(request, file_name):
    # Check resource id param if provided
    resource_id = request.GET.get('resourceId')
    res = None
    if resource_id:
        res = Resource.objects.filter(id=resource_id).first()
    if not res:
        res = Resource.objects.filter(file_name=file_name).first()

    if res:
        res.download_count += 1
        res.save(update_fields=['download_count'])

    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    if not os.path.exists(file_path):
        # Create a mock file on the fly if it does not exist
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Malnad College of Engineering (Autonomous)\nDepartment Resource Repository\nResource: {file_name}\nDownloaded at {timezone.now()}\n")

    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=res.original_file_name if res and res.original_file_name else file_name)
    return response


# --- SUBJECT APIS ---
@csrf_exempt
def api_subjects_list(request):
    if request.method == 'GET':
        subjects = Subject.objects.all().order_by('semester', 'code')
        resp = []
        for s in subjects:
            resp.append({
                'id': s.id,
                'code': s.code,
                'name': s.name,
                'semester': s.semester,
                'credits': s.credits,
                'description': s.description,
            })
        return JsonResponse(resp, safe=False)

    elif request.method == 'POST':
        user = get_authenticated_user(request)
        if not user or getattr(user.profile, 'role', '') != 'ROLE_ADMIN':
            return JsonResponse({'message': 'Only admin can add subjects'}, status=403)
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST

        s = Subject.objects.create(
            code=data.get('code'),
            name=data.get('name'),
            semester=data.get('semester', 1),
            credits=data.get('credits', 3),
            description=data.get('description', '')
        )
        return JsonResponse({
            'id': s.id,
            'code': s.code,
            'name': s.name,
            'semester': s.semester,
            'credits': s.credits,
            'description': s.description,
        })


def api_subjects_by_semester(request, sem):
    subjects = Subject.objects.filter(semester=sem).order_by('code')
    resp = []
    for s in subjects:
        resp.append({
            'id': s.id,
            'code': s.code,
            'name': s.name,
            'semester': s.semester,
            'credits': s.credits,
            'description': s.description,
        })
    return JsonResponse(resp, safe=False)


@csrf_exempt
def api_subject_delete(request, pk):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user or getattr(user.profile, 'role', '') != 'ROLE_ADMIN':
        return JsonResponse({'message': 'Only admin can delete subjects'}, status=403)
    Subject.objects.filter(pk=pk).delete()
    return JsonResponse({'message': 'Subject deleted'})


@csrf_exempt
def api_subject_enroll(request, pk):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)
    
    subject = Subject.objects.filter(pk=pk).first()
    if not subject:
        return JsonResponse({'message': 'Subject not found'}, status=404)

    profile = getattr(user, 'profile', None)
    if profile:
        profile.enrolled_subjects.add(subject)
        ids = list(profile.enrolled_subjects.values_list('id', flat=True))
        return JsonResponse({
            'message': f"Successfully enrolled in {subject.code} - {subject.name}",
            'enrolledSubjectIds': ids
        })
    return JsonResponse({'message': 'Profile error'}, status=500)


@csrf_exempt
def api_subject_unenroll(request, pk):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    profile = getattr(user, 'profile', None)
    if profile:
        profile.enrolled_subjects.remove(pk)
        ids = list(profile.enrolled_subjects.values_list('id', flat=True))
        return JsonResponse({
            'message': 'Successfully unenrolled',
            'enrolledSubjectIds': ids
        })
    return JsonResponse({'message': 'Profile error'}, status=500)


def api_my_courses(request):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)
    profile = getattr(user, 'profile', None)
    if not profile:
        return JsonResponse([], safe=False)
    
    courses = profile.enrolled_subjects.all().order_by('code')
    resp = [{
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'semester': c.semester,
        'credits': c.credits,
        'description': c.description
    } for c in courses]
    return JsonResponse(resp, safe=False)


@csrf_exempt
def api_update_my_semester(request):
    if request.method != 'PATCH':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)
    semester = request.GET.get('semester')
    if not semester:
        return JsonResponse({'message': 'Missing semester'}, status=400)
    
    profile = getattr(user, 'profile', None)
    if profile:
        try:
            profile.current_semester = int(semester)
            # Re-enroll in that semester's courses
            subjects = Subject.objects.filter(semester=profile.current_semester)
            profile.enrolled_subjects.set(subjects)
            profile.save()
            return JsonResponse(user_to_dict(user))
        except ValueError:
            return JsonResponse({'message': 'Invalid semester'}, status=400)
    return JsonResponse({'message': 'Profile error'}, status=500)


# --- WORKSTATION APIS ---
def api_workstations_list(request):
    ws = LabWorkstation.objects.all().order_by('identifier')
    return JsonResponse([workstation_to_dict(w) for w in ws], safe=False)


@csrf_exempt
def api_workstations_book(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    ws_id = data.get('workstationId')
    purpose = data.get('purpose', '')
    start_time = data.get('startTime')
    end_time = data.get('endTime')

    ws = LabWorkstation.objects.filter(id=ws_id).first()
    if not ws:
        return JsonResponse({'message': 'Workstation not found'}, status=404)

    booking = WorkstationBooking.objects.create(
        workstation=ws,
        user=user,
        purpose=purpose,
        start_time=start_time or timezone.now(),
        end_time=end_time or (timezone.now() + timezone.timedelta(hours=2)),
        status='APPROVED' if getattr(user.profile, 'role', '') == 'ROLE_ADMIN' else 'PENDING'
    )

    return JsonResponse(booking_to_dict(booking))


def api_my_bookings(request):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)
    bookings = WorkstationBooking.objects.filter(user=user)
    return JsonResponse([booking_to_dict(b) for b in bookings], safe=False)


def api_all_bookings(request):
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)
    bookings = WorkstationBooking.objects.all()
    return JsonResponse([booking_to_dict(b) for b in bookings], safe=False)


@csrf_exempt
def api_update_booking_status(request, pk):
    if request.method != 'PATCH':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user:
        return JsonResponse({'message': 'Unauthorized'}, status=401)

    booking = WorkstationBooking.objects.filter(pk=pk).first()
    if not booking:
        return JsonResponse({'message': 'Booking not found'}, status=404)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    status_val = data.get('status')
    admin_remarks = data.get('adminRemarks', '')
    if status_val:
        booking.status = status_val
    if admin_remarks:
        booking.admin_remarks = admin_remarks
    booking.save()

    return JsonResponse(booking_to_dict(booking))


# --- STATS API ---
def api_stats(request):
    total_resources = Resource.objects.filter(is_approved=True).count()
    from django.db.models import Sum
    downloads = Resource.objects.aggregate(total=Sum('download_count'))['total'] or 0
    total_users = User.objects.count()
    total_subjects = Subject.objects.count()
    available_workstations = LabWorkstation.objects.filter(status='AVAILABLE').count()
    active_bookings = WorkstationBooking.objects.filter(status='APPROVED').count()

    return JsonResponse({
        'totalResources': total_resources,
        'totalDownloads': downloads,
        'totalUsers': total_users,
        'totalSubjects': total_subjects,
        'availableWorkstations': available_workstations,
        'activeBookings': active_bookings,
    })


# --- ADMIN USERS APIS ---
@csrf_exempt
def api_admin_users(request):
    user = get_authenticated_user(request)
    if not user or getattr(user.profile, 'role', '') != 'ROLE_ADMIN':
        return JsonResponse({'message': 'Forbidden'}, status=403)

    users = User.objects.all().select_related('profile')
    return JsonResponse([user_to_dict(u) for u in users], safe=False)


@csrf_exempt
def api_admin_user_role(request, pk):
    if request.method != 'PATCH':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user or getattr(user.profile, 'role', '') != 'ROLE_ADMIN':
        return JsonResponse({'message': 'Forbidden'}, status=403)

    target_user = User.objects.filter(pk=pk).first()
    if not target_user:
        return JsonResponse({'message': 'User not found'}, status=404)

    role = request.GET.get('role')
    if role and hasattr(target_user, 'profile'):
        target_user.profile.role = role
        target_user.profile.save()

    return JsonResponse(user_to_dict(target_user))


@csrf_exempt
def api_admin_user_status(request, pk):
    if request.method != 'PATCH':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user or getattr(user.profile, 'role', '') != 'ROLE_ADMIN':
        return JsonResponse({'message': 'Forbidden'}, status=403)

    target_user = User.objects.filter(pk=pk).first()
    if not target_user:
        return JsonResponse({'message': 'User not found'}, status=404)

    active_val = request.GET.get('active', 'true').lower() == 'true'
    target_user.is_active = active_val
    target_user.save()
    if hasattr(target_user, 'profile'):
        target_user.profile.is_active_user = active_val
        target_user.profile.save()

    return JsonResponse(user_to_dict(target_user))


@csrf_exempt
def api_admin_user_delete(request, pk):
    if request.method != 'DELETE':
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    user = get_authenticated_user(request)
    if not user or getattr(user.profile, 'role', '') != 'ROLE_ADMIN':
        return JsonResponse({'message': 'Forbidden'}, status=403)

    User.objects.filter(pk=pk).delete()
    return JsonResponse({'message': 'User deleted successfully'})
