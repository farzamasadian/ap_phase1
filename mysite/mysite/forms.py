from django import forms
from django.contrib.auth.models import User
from .models import Appointment, Clinic

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date_time', 'clinic', 'user', 'status']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'status': forms.HiddenInput()  # Hide status field if it's always going to be 'pending'
        }

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['status'].initial = 'pending'  # Set default status to 'pending'


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = [('patient', 'Patient'), ('staff', 'Staff')]
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    email = forms.EmailField(required=False)  # Optional, based on user type

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']



class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        # Add any other user fields that you want to be updatable

class BookAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['clinic', 'date_time']
        # Include any other fields that are needed for booking an appointment

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BookAppointmentForm, self).__init__(*args, **kwargs)
        # Additional initialization can go here (e.g., setting querysets for dropdowns)

class UpdateClinicInfoForm(forms.ModelForm):
    class Meta:
        model = Clinic
        fields = ['name', 'address', 'phone_info']
        # Include any other fields that you want admins to be able to update
