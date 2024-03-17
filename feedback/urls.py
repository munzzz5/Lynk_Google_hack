from django.urls import path
from . import views

urlpatterns = [
    # Create
    path('', views.feedback_home, name='feedback_home'),
    path('create/', views.feedback_flow, name='create_feedback'),
    # Read (List view and Detail view)
    path('list/', views.list_feedback, name='list_feedback'),
    path('detail/<int:pk>/', views.detail_feedback, name='detail_feedback'),
    # Update
    path('edit/<int:pk>/', views.feedback_edit, name='edit_feedback'),
    # Delete
    path('delete/<int:pk>/', views.delete_feedback, name='delete_feedback'),
    path('reset_step/', views.reset_step, name='reset_step'),
]
