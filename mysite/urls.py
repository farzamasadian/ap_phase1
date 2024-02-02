from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.sign_up_view, name='signup'),
    path('login/', views.log_in_view, name='login'),
    path('user-appointments/', views.user_appointments_view, name='user_appointments'),
    path('remove-appointment/<int:appointment_id>/', views.remove_appointment, name='remove_appointment'),
    path('add-appointment-capacity/', views.add_appointment_capacity, name='add_appointment_capacity'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('view-notifications/', views.view_notifications, name='view_notifications'),
    path('update-clinic-info/<int:clinic_id>/', views.update_clinic_info, name='update_clinic_info'),
    path('available-appointments/', views.fetch_available_appointments, name='available_appointments'),
    path('adjust-clinic-capacity/', views.adjust_clinic_capacity, name='adjust_clinic_capacity'),
    # ... other url patterns ...
]

