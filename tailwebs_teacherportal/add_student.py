import os
import sys
import subprocess
import django

def run_command(command, description):
    """Run a shell command"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_django():
    """Complete Django setup"""
    print("🚀 Django Teacher Portal Setup")
    print("===============================")
    
    # Run migrations
    if not run_command('python manage.py makemigrations', 'Creating migrations'):
        return False
    
    if not run_command('python manage.py migrate', 'Running migrations'):
        return False
    
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tailwebs_teacherportal.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    from portal.models import Teacher
    
    # Create admin user
    print("\n👤 Creating admin user...")
    username = "admin"
    password = "admin123"
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email="admin@example.com",
            password=password
        )
        print(f"✅ Created admin user: {username}")
    else:
        print(f"⚠️  Admin user '{username}' already exists")
    
    # Create teacher user
    print("\n👨‍🏫 Creating teacher user...")
    if not Teacher.objects.filter(username=username).exists():
        teacher = Teacher(username=username)
        teacher.set_password(password)
        teacher.save()
        print(f"✅ Created teacher user: {username}")
    else:
        print(f"⚠️  Teacher user '{username}' already exists")
    
    # Create sample data
    print("\n📚 Creating sample students...")
    from portal.models import Student
    
    sample_students = [
        {'name': 'Manoj Khadse', 'subject': 'Mathematics', 'marks': 92},
        {'name': 'Yaman Bisen', 'subject': 'Physics', 'marks': 85},
        {'name': 'Pratik Padole', 'subject': 'Chemistry', 'marks': 88},
        {'name': 'Aman Dhole', 'subject': 'Biology', 'marks': 90},
        {'name': 'Sarvesh Jagnade', 'subject': 'Mathematics', 'marks': 87},
    ]
    
    for student_data in sample_students:
        student, created = Student.objects.get_or_create(
            name=student_data['name'],
            subject=student_data['subject'],
            defaults={'marks': student_data['marks']}
        )
        if created:
            print(f"  ✅ Created: {student.name} - {student.subject} ({student.marks})")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Access Information:")
    print("======================")
    print("🌐 Teacher Portal: http://127.0.0.1:8000/")
    print("🔧 Django Admin:   http://127.0.0.1:8000/admin/")
    print(f"👤 Username:       {username}")
    print(f"🔑 Password:       {password}")
    print("\n▶️  Start server with: python manage.py runserver")

if __name__ == '__main__':
    setup_django()