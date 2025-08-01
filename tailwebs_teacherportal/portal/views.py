from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
import json
from .models import Teacher, Student, AuditLog,SessionToken
from .utils import create_session_token, calculate_new_marks, log_audit_action, get_client_ip, validate_marks

# Create your views here.


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'GET':
        return render(request, 'portal/login.html')
    
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    
    # Input validation
    if not username or not password:
        messages.error(request, 'Username and password are required')
        return render(request, 'portal/login.html')
    
    # Prevent basic injection attempts
    if any(char in username for char in ['<', '>', '"', "'"]):
        messages.error(request, 'Invalid characters in username')
        return render(request, 'portal/login.html')
    
    try:
        teacher = Teacher.objects.get(username=username)
        if teacher.check_password(password):
            # Create session token
            token = create_session_token(teacher)
            request.session['auth_token'] = token
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    except Teacher.DoesNotExist:
        messages.error(request, 'Invalid credentials')
    
    return render(request, 'portal/login.html')

def home_view(request):
    """Display student list with inline editing capabilities"""
    students = Student.objects.all().order_by('name', 'subject')
    return render(request, 'portal/home.html', {'students': students})

@csrf_protect
@require_http_methods(["POST"])
def update_marks(request):
    """Handle inline marks updates with validation and audit logging"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        new_marks = data.get('marks')
        
        # Validate input
        if not student_id or new_marks is None:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        if not validate_marks(new_marks):
            return JsonResponse({'success': False, 'error': 'Marks must be between 0 and 100'})
        
        with transaction.atomic():
            student = get_object_or_404(Student, id=student_id)
            old_marks = student.marks
            student.marks = int(new_marks)
            student.save()
            
            # Log the action
            log_audit_action(
                teacher=request.user,
                action='UPDATE',
                student_name=student.name,
                subject=student.subject,
                old_marks=old_marks,
                new_marks=student.marks,
                ip_address=get_client_ip(request)
            )
        
        return JsonResponse({'success': True, 'message': 'Marks updated successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_protect
@require_http_methods(["POST"])
def delete_student(request):
    """Handle inline student deletion with audit logging"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        
        if not student_id:
            return JsonResponse({'success': False, 'error': 'Student ID required'})
        
        print(request.user)
        with transaction.atomic():
            student = get_object_or_404(Student, id=student_id)
            
            # Log the action before deletion
            log_audit_action(
                teacher=request.user,
                action='DELETE',
                student_name=student.name,
                subject=student.subject,
                old_marks=student.marks,
                ip_address=get_client_ip(request)
            )
            
            student.delete()
        
        return JsonResponse({'success': True, 'message': 'Student deleted successfully'})
    
    except Exception as e:
        print("---------------------",e)
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_protect
@require_http_methods(["POST"])
def add_student(request):
    """Handle new student addition with duplicate checking and business logic"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        subject = data.get('subject', '').strip()
        marks = data.get('marks')
        
        # Input validation
        if not name or not subject:
            return JsonResponse({'success': False, 'error': 'Name and subject are required'})
        
        if not validate_marks(marks):
            return JsonResponse({'success': False, 'error': 'Marks must be between 0 and 100'})
        
        # Sanitize inputs to prevent XSS
        name = name[:100]  # Limit length
        subject = subject[:100]
        marks = int(marks)
        
        with transaction.atomic():
            # Check if student with same name and subject exists
            try:
                existing_student = Student.objects.get(name=name, subject=subject)
                # Apply business logic for existing student
                old_marks = existing_student.marks
                new_marks = calculate_new_marks(existing_student.marks, marks)
                
                if new_marks > 100:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Total marks would exceed 100 (current: {old_marks}, adding: {marks})'
                    })
                
                print(new_marks,"--------------------")
                existing_student.marks = new_marks
                existing_student.save()
                
                log_audit_action(
                    teacher=request.user,
                    action='UPDATE',
                    student_name=name,
                    subject=subject,
                    old_marks=old_marks,
                    new_marks=new_marks,
                    ip_address=get_client_ip(request)
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Updated existing student. Marks increased from {old_marks} to {new_marks}'
                })
                
            except Student.DoesNotExist:
                # Create new student
                student = Student.objects.create(
                    name=name,
                    subject=subject,
                    marks=marks
                )
                
                log_audit_action(
                    teacher=request.user,
                    action='CREATE',
                    student_name=name,
                    subject=subject,
                    new_marks=marks,
                    ip_address=get_client_ip(request)
                )
                
                return JsonResponse({'success': True, 'message': 'Student added successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def logout_view(request):
    """Handle user logout and session cleanup"""
    # Clean up session token
    session_token = request.session.get('auth_token')
    if session_token:
        try:
            SessionToken.objects.get(token=session_token).delete()
        except:
            pass
    
    request.session.flush()
    return redirect('login')



from portal.models import Teacher, Student

def create_sample_data():
    print("------------------------------")
    """Create sample data for testing"""
    
    # Create a sample teacher if it doesn't exist
    if not Teacher.objects.filter(username='teacher1').exists():
        teacher = Teacher(username='teacher1')
        teacher.set_password('password123')
        teacher.save()
        print("Created teacher: teacher1 / password123")
    
    # Create sample students
    sample_students = [
        {'name': 'Manoj Khadse', 'subject': 'Mathematics', 'marks': 85},
        {'name': 'Yaman bisen', 'subject': 'Physics', 'marks': 92},
        {'name': 'Aman Dhole', 'subject': 'Chemistry', 'marks': 78},
        {'name': 'Nirmal rao', 'subject': 'Biology', 'marks': 88},
        {'name': 'Sarvesh Jagnade', 'subject': 'Mathematics', 'marks': 76},
        {'name': 'Suraj Durve', 'subject': 'Physics', 'marks': 94},
        {'name': 'Mayur Noroliya', 'subject': 'Chemistry', 'marks': 82},
        {'name': 'Tanmay Kumbhare', 'subject': 'Biology', 'marks': 90},
    ]
    
    for student_data in sample_students:
        student, created = Student.objects.get_or_create(
            name=student_data['name'],
            subject=student_data['subject'],
            defaults={'marks': student_data['marks']}
        )
        if created:
            print(f"Created student: {student.name} - {student.subject} ({student.marks})")


# create_sample_data()
print("Sample data creation completed!")


# print(SessionToken.objects.all().last().is_active,"---------------") 