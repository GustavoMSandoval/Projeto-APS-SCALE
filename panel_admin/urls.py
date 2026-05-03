from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),

    path('users/', views.users, name='users'),
    path('users/<int:id>/', views.user_edit, name='user_edit'),

    path('emergy/', views.emergy_list, name='emergy_list'),
    path('emergy/create/', views.emergy_create, name='emergy_create'),
    path('emergy/edit/<int:id>/', views.emergy_edit, name='emergy_edit'),
    path('emergy/delete/<int:id>/', views.emergy_delete, name='emergy_delete'),

    path('projects/', views.project, name='project'),
    path('projects/edit/<int:id>/', views.project_edit, name='project_edit'),
    path('projects/<int:id>/results/', views.project_results_admin, name='project_results_admin')
]