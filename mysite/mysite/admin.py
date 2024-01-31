from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['date_time', 'clinic', 'user', 'status']
    # Add more customizations as needed