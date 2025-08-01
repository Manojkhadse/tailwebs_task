from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from .models import SessionToken



class CustomAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip authentication for login page and static files
        excluded_paths = [reverse('login'), '/static/']
        if any(request.path.startswith(path) for path in excluded_paths):
            response = self.get_response(request)
            return response
        
        # Handle Django Admin URLs separately
        if request.path.startswith('/admin/'):
            # Let Django's built-in authentication handle admin
            # Don't interfere with Django admin authentication
            response = self.get_response(request)
            return response
        
        # Check for session token
        session_token = request.session.get('auth_token')
        if session_token:
            try:
                token_obj = SessionToken.objects.get(token=session_token)
                if token_obj.is_valid():
                    request.user = token_obj.teacher
                    response = self.get_response(request)
                    return response
                else:
                    # Token expired, clean up
                    token_obj.delete()
                    request.session.flush()
            except SessionToken.DoesNotExist:
                request.session.flush()
        
        # Redirect to login if not authenticated
        print(request.path)
        if request.path != reverse('login'):
            print("-------------")
            return redirect('login')
        
        response = self.get_response(request)
        return response