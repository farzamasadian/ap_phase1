from datetime import datetime, timedelta
from enum import Enum
import random
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _



class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('staff', 'Staff'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    use_otp = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.save()
        return self.otp

    def check_otp(self, input_otp):
        if self.use_otp and self.otp == input_otp and timezone.now() < self.otp_expiry:
            return True
        return False

    def update_profile(self, new_email=None, new_password=None):
        if new_email:
            self.email = new_email
        if new_password:
            self.set_password(new_password)
        self.save()

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_groups'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_permissions'
    )


class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_info = models.CharField(max_length=20, blank=True)

    def update_clinic_info(self, new_address=None, new_phone=None):
        """
        Updates the clinic's address or phone information.
        """
        if new_address:
            self.address = new_address
        if new_phone:
            self.phone_info = new_phone
        self.save()

# Moved outside of the Clinic class
class Availability(models.Model):
    clinic = models.ForeignKey(Clinic, related_name='availabilities', on_delete=models.CASCADE)
    date = models.DateField()
    is_available = models.BooleanField()

    class Meta:
        unique_together = ('clinic', 'date')

    @staticmethod
    def set_availability_for_clinic(clinic, date, available):
        """
        Sets the clinic's availability for a specific date.
        """
        availability, created = Availability.objects.get_or_create(clinic=clinic, date=date)
        availability.is_available = available
        availability.save()




class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date_time = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """
        Overrides the save method to check for appointment time slot availability before saving.
        """
        if not self.is_time_slot_available():
            raise ValidationError("This time slot is already booked.")
        super().save(*args, **kwargs)

    def is_time_slot_available(self):
        """
        Checks if the appointment time slot is available.
        """
        overlapping_appointments = Appointment.objects.filter(
            clinic=self.clinic, 
            date_time=self.date_time
        ).exclude(id=self.id)
        return not overlapping_appointments.exists()

    def cancel(self):
        """
        Cancels the appointment by changing its status to canceled.
        """
        self.status = 'canceled'
        self.save()

    def reschedule(self, new_time):
        """
        Reschedules the appointment to a new time and resets its status to pending.
        """
        self.date_time = new_time
        self.status = 'pending'
        self.save()



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='username')
    message = models.TextField()
    date_time = models.DateTimeField()

    @classmethod
    def send_notification(cls, user, message, date_time=None):
        """
        Sends a notification to a specific user.
        """
        if date_time is None:
            date_time = timezone.now()
        notification = cls.objects.create(user=user, message=message, date_time=date_time)
        # Here you can add logic to actually send the notification (e.g., email, SMS, etc.)
        print(f"Notification sent to {user.username} at {notification.date_time}: {notification.message}")

    @staticmethod
    def send_bulk_notifications(users, message):
        """
        Sends a notification to a list of users.
        """
        for user in users:
            Notification.objects.create(user=user, message=message, date_time=timezone.now())
            print(f"Sent notification to {user.username}")

