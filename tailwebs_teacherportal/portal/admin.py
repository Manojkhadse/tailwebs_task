from django.contrib import admin
from .models import Teacher, Student, AuditLog, SessionToken

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['username', 'created_at']
    readonly_fields = ['password_hash', 'salt', 'created_at']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'marks', 'created_at', 'updated_at']
    list_filter = ['subject', 'created_at']
    search_fields = ['name', 'subject']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'action', 'student_name', 'subject', 'timestamp']
    list_filter = ['action', 'timestamp']
    readonly_fields = ['teacher', 'action', 'student_name', 'subject', 'old_marks', 'new_marks', 'timestamp', 'ip_address']

@admin.register(SessionToken)
class SessionTokenAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'created_at', 'expires_at', 'is_active']
    readonly_fields = ['token', 'created_at']