from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/update-marks/', views.update_marks, name='update_marks'),
    path('api/delete-student/', views.delete_student, name='delete_student'),
    path('api/add-student/', views.add_student, name='add_student'),
]