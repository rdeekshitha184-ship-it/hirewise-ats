
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.resume_upload,
    name='resume_upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export/', views.export_csv, name='export_csv'),
    path('delete-resume/<int:resume_id>/', views.delete_resume, name='delete_resume'),
]