import secrets
from datetime import datetime, timedelta
from django.utils import timezone
from .models import SessionToken, AuditLog

def generate_session_token():
    """Generate a secure random session token"""
    return secrets.token_urlsafe(64)

def create_session_token(teacher):
    """Create a new session token for teacher"""
    # Clean up old tokens
    SessionToken.objects.filter(teacher=teacher).delete()
    
    token = generate_session_token()
    expires_at = timezone.now() + timedelta(hours=24)  # 24 hour session
    
    session_token = SessionToken.objects.create(
        teacher=teacher,
        token=token,
        expires_at=expires_at
    )
    return token

def calculate_new_marks(existing_marks, new_marks):
    """
    Business logic for calculating marks when student with same name/subject exists
    This adds the new marks to existing ones but caps at 100
    """
    total = existing_marks + new_marks
    return min(total, 100)

def log_audit_action(teacher, action, student_name, subject, old_marks=None, new_marks=None, ip_address=None):
    """Log user actions for audit trail"""
    AuditLog.objects.create(
        teacher=teacher,
        action=action,
        student_name=student_name,
        subject=subject,
        old_marks=old_marks,
        new_marks=new_marks,
        ip_address=ip_address or '127.0.0.1'
    )

def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_marks(marks):
    """Validate marks are within acceptable range"""
    try:
        marks_int = int(marks)
        return 0 <= marks_int <= 100
    except (ValueError, TypeError):
        return False