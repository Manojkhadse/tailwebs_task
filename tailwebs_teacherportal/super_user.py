import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tailwebs_teacherportal.settings')
django.setup()

from django.contrib.auth.models import User

def fix_admin_access():
    print("🔧 Fixing Django Admin Access")
    print("=============================")
    
    # Create a superuser for admin access
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email (optional): ").strip()
    password = input("Enter admin password (default: admin123): ").strip() or "admin123"
    
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User '{username}' already exists!")
            choice = input("Update password? (y/n): ").lower()
            if choice == 'y':
                user = User.objects.get(username=username)
                user.set_password(password)
                user.is_superuser = True
                user.is_staff = True
                user.save()
                print(f"✅ Updated user '{username}' with admin privileges")
            else:
                print("❌ Cancelled")
                return
        else:
            # Create new superuser
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Created superuser '{username}'")
        
        print("\n🎉 Admin access fixed!")
        print("📋 Next steps:")
        print("1. Run: python manage.py migrate (if you haven't already)")
        print("2. Start server: python manage.py runserver")
        print("3. Access admin at: http://127.0.0.1:8000/admin/")
        print(f"4. Login with: {username} / {password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    fix_admin_access()