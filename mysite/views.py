from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
import requests
from .forms import *
from django.contrib import messages
from .models import Notification, Clinic, Appointment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test


def sign_up_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'patient':
                user.email = form.cleaned_data.get('email')
            # Further processing based on user type
            user.save()
            # Redirect to a success page, login page, or home page
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})



def log_in_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to a success page, such as the user's profile or home page
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_appointments_view(request):
    user_appointments = Appointment.get_appointments_for_user(request.user)
    return render(request, 'user_appointments.html', {'appointments': user_appointments})


# Helper function to check if a user is an admin
def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def remove_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if request.method == 'POST':
        appointment.delete()
        # Redirect to a success page, such as the appointment listing
        return redirect('appointments_list')
    return render(request, 'remove_appointment.html', {'appointment': appointment})

@login_required
@user_passes_test(is_admin)
def add_appointment_capacity(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a success page, such as the appointment listing
            return redirect('appointments_list')
    else:
        form = AppointmentForm()
    return render(request, 'add_appointment_capacity.html', {'form': form})



def fetch_available_appointments(request):
    """
    Fetches available appointments from an external API and displays them.
    """
    try:
        response = requests.get('http://127.0.0.1:5000/available')
        if response.status_code == 200:
            available_appointments = response.json()
            context = {'appointments': available_appointments}
        else:
            context = {'error': 'Failed to fetch available appointments.'}
    except Exception as e:
        context = {'error': f'An error occurred: {e}'}

    return render(request, 'available_appointments.html', context)


class ClinicCapacityForm(forms.Form):
    clinic_code = forms.IntegerField(label='Clinic Code')
    reserved_appointments = forms.IntegerField(label='Reserved Appointments')

def adjust_clinic_capacity(request):
    if request.method == 'POST':
        form = ClinicCapacityForm(request.POST)
        if form.is_valid():
            try:
                payload = {
                    'clinic code': form.cleaned_data['clinic_code'],
                    'reserved appointments': form.cleaned_data['reserved_appointments']
                }
                response = requests.post('https://localhost/slots', json=payload)

                if response.status_code == 200:
                    # Handle success
                    return render(request, 'adjust_capacity_success.html', {'response': response.json()})
                else:
                    # Handle failure
                    return render(request, 'adjust_capacity_failure.html', {'error': 'Failed to adjust clinic capacity.'})
            except Exception as e:
                # Handle exception
                return render(request, 'adjust_capacity_failure.html', {'error': f'An error occurred: {e}'})
    else:
        form = ClinicCapacityForm()

    return render(request, 'adjust_clinic_capacity.html', {'form': form})



@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = BookAppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('appointments_view')
    else:
        form = BookAppointmentForm(user=request.user)
    return render(request, 'book_appointment.html', {'form': form})

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_view')
    else:
        form = UpdateProfileForm(instance=request.user)
    return render(request, 'update_profile.html', {'form': form})

@login_required
def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', {'notifications': notifications})

@staff_member_required
def update_clinic_info(request, clinic_id):
    clinic = get_object_or_404(Clinic, pk=clinic_id)
    if request.method == 'POST':
        form = UpdateClinicInfoForm(request.POST, instance=clinic)
        if form.is_valid():
            form.save()
            return redirect('clinic_info_view')
    else:
        form = UpdateClinicInfoForm(instance=clinic)
    return render(request, 'update_clinic_info.html', {'form': form, 'clinic': clinic})

