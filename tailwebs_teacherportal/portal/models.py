from django.db import models
import hashlib
import secrets
from datetime import datetime

class Teacher(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=128)
    salt = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def set_password(self, raw_password):
        """Custom password hashing with salt"""
        self.salt = secrets.token_hex(16)
        # Combine password with salt and hash multiple times for security
        combined = f"{raw_password}{self.salt}"
        for _ in range(10000):  # Multiple iterations for stronger security
            combined = hashlib.sha256(combined.encode()).hexdigest()
        self.password_hash = combined
    
    def check_password(self, raw_password):
        """Verify password against stored hash"""
        combined = f"{raw_password}{self.salt}"
        for _ in range(10000):
            combined = hashlib.sha256(combined.encode()).hexdigest()
        return combined == self.password_hash
    
    def __str__(self):
        return self.username

class Student(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    marks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'subject']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class SessionToken(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def is_valid(self):
        from django.utils import timezone
        return self.is_active and self.expires_at > timezone.now()

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('CREATE', 'Create'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    student_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    old_marks = models.IntegerField(null=True, blank=True)
    new_marks = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    
    def __str__(self):
        return f"{self.teacher.username} - {self.action} - {self.student_name}"