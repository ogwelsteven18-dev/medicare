from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('list/', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('delete/<int:pk>/', views.user_delete, name='user_delete'),
]
