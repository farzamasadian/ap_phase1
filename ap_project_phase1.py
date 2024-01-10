import json
from datetime import datetime, timedelta
from enum import Enum
import re
import random
import requests

# Enums for clarity and safety
class UserType(Enum):
    PATIENT = "patient"
    STAFF = "clinic staff"

class AppointmentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"

# Dummy data storage as JSON-like structures (lists of dictionaries)
users = []
clinics = []
appointments = []
notifications = []
clinic_id_counter = 1
appointment_id_counter = 1

class User:
    """
    Represents a user of the Clinic Reservation System.
    Can be a patient or staff member.
    
    Attributes:
    - user_id: Unique identifier for the user.
    - username: Chosen username for the user.
    - email: Email address of the user.
    - password: Password for the user's account (should be hashed in a real-world scenario).
    - user_type: Type of user (patient or staff).
    - use_otp: Flag indicating if the user prefers One Time Password for login.
    - otp: Current One Time Password if generated.
    - otp_expiry: Expiration time for the OTP.
    """
    def __init__(self, user_id, username, email, password, user_type: UserType, use_otp=False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.user_type = user_type.value
        self.use_otp = use_otp
        self.otp = None
        self.otp_expiry = None

    def sign_up(self):
        """
        Registers the user in the system if the username is unique.
        """
        for user in users:
            if user['username'] == self.username:
                print("Username already exists.")
                return
        users.append(self.to_dict())
        print(f"User {self.username} signed up successfully.")

    def generate_otp(self):
        """
        Generates a One Time Password for the user and sets its expiry time.
        """
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = datetime.now() + timedelta(minutes=5)  # OTP expires in 5 minutes
        print(f"OTP for {self.username} is {self.otp} and will expire in 5 minutes.")

    def login(self, input_password):
        """
        Authenticates the user using either a fixed password or a One Time Password.
        
        Attributes:
        - input_password: The password or OTP provided by the user for authentication.
        """
        for user in users:
            if user['username'] == self.username:
                if self.use_otp:
                    if self.otp == input_password and datetime.now() < self.otp_expiry:
                        print(f"User {self.username} logged in successfully with OTP.")
                        return True
                    else:
                        print("Invalid or expired OTP.")
                        return False
                elif user['password'] == input_password:
                    print(f"User {self.username} logged in successfully.")
                    return True
        print("Invalid username or password.")
        return False

    def update_profile(self, new_email=None, new_password=None):
        """
        Updates the user's email or password.
        
        Attributes:
        - new_email: New email address to update.
        - new_password: New password to update.
        """
        for user in users:
            if user['user_id'] == self.user_id:
                if new_email:
                    user['email'] = new_email
                    print(f"{self.username}'s email updated successfully to {new_email}.")
                if new_password:
                    user['password'] = new_password  # In a real-world scenario, you'd hash the password
                    print(f"{self.username}'s password updated successfully.")
                return
        print("User not found. Profile update failed.")

    def view_appointments(self):
        """
        Displays all appointments associated with the user.
        """
        print(f"Appointments for {self.username}:")
        user_appointments = [appt for appt in appointments if appt['user_id'] == self.user_id]
        if not user_appointments:
            print("No appointments found.")
        for appt in user_appointments:
            status = appt['status']
            date_time = appt['date_time']
            clinic_info = next((clinic for clinic in clinics if clinic['clinic_id'] == appt['clinic_id']), None)
            clinic_name = clinic_info['name'] if clinic_info else 'Unknown Clinic'
            print(f"- Appointment {appt['appointment_id']} at {clinic_name} on {date_time} with status {status}.")

    def to_dict(self):
        """
        Converts the user object to a dictionary for easier handling and storage.
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'user_type': self.user_type,
            'use_otp': self.use_otp,
            'otp': self.otp,
            'otp_expiry': self.otp_expiry.isoformat() if self.otp_expiry else None
        }


class Clinic:
    """
    Represents a clinic in the Clinic Reservation System.
    
    Attributes:
    - clinic_id: Unique identifier for the clinic.
    - name: Name of the clinic.
    - address: Physical address of the clinic.
    - phone_info: Contact number for the clinic.
    - services: List of services provided by the clinic.
    - availability: Dictionary holding the availability status for different dates.
    """
    def __init__(self, clinic_id, name, address, phone_info, services):
        self.clinic_id = clinic_id
        self.name = name
        self.address = address
        self.phone_info = phone_info
        self.services = services
        self.availability = {}  # Dictionary to hold availability status

    def to_dict(self):
        """
        Converts the clinic object to a dictionary for easier handling and storage.
        """
        return {
            'clinic_id': self.clinic_id,
            'name': self.name,
            'address': self.address,
            'phone_info': self.phone_info,
            'services': self.services,
            'availability': self.availability
        }

    def update_clinic_info(self, new_address=None, new_phone=None):
        """
        Updates the clinic's address or phone information.
        
        Attributes:
        - new_address: New physical address to update.
        - new_phone: New contact number to update.
        """
        if new_address:
            self.address = new_address
        if new_phone:
            self.phone_info = new_phone
        print(f"Clinic {self.name}'s info updated successfully.")

    def set_availability(self, date, available):
        """
        Sets the clinic's availability for a specific date.
        
        Attributes:
        - date: The specific date for which to set the availability.
        - available: Boolean indicating if the clinic is available on that date.
        """
        self.availability[date] = available
        print(f"Clinic {self.name} set to {'available' if available else 'unavailable'} on {date}")


class Appointment:
    """
    Represents an appointment in the Clinic Reservation System.
    
    Attributes:
    - status: The status of the appointment (pending, confirmed, canceled).
    - date_time: The date and time of the appointment.
    - user_id: The ID of the user who made the appointment.
    - clinic_id: The ID of the clinic where the appointment is made.
    - appointment_id: Unique identifier for the appointment.
    """
    def __init__(self, status: AppointmentStatus, date_time, user_id, clinic_id):
        global appointment_id_counter
        self.status = status.value
        self.date_time = date_time
        self.user_id = user_id
        self.clinic_id = clinic_id
        self.appointment_id = appointment_id_counter
        appointment_id_counter += 1

    def to_dict(self):
        """
        Converts the appointment object to a dictionary for easier handling and storage.
        """
        return {
            'appointment_id': self.appointment_id,
            'status': self.status,
            'date_time': self.date_time,
            'user_id': self.user_id,
            'clinic_id': self.clinic_id
        }

    def register_patient_appointment(self):
        """
        Registers a new appointment for the patient if the time slot isn't already taken.
        """
        for appointment in appointments:
            if appointment['date_time'] == self.date_time and appointment['clinic_id'] == self.clinic_id:
                print("This time slot is already booked.")
                return
        appointments.append(self.to_dict())
        print(f"Appointment {self.appointment_id} registered successfully for user {self.user_id}.")

    def cancel_patient_appointment(self):
        """
        Cancels the appointment by changing its status to canceled.
        """
        for appointment in appointments:
            if appointment['appointment_id'] == self.appointment_id:
                appointment['status'] = AppointmentStatus.CANCELED.value
                print(f"Appointment {self.appointment_id} has been canceled.")
                break

    def reschedule_patient_appointment(self, new_time):
        """
        Reschedules the appointment to a new time and resets its status to pending.
        
        Attributes:
        - new_time: The new time to which the appointment is rescheduled.
        """
        for appointment in appointments:
            if appointment['appointment_id'] == self.appointment_id:
                appointment['date_time'] = new_time
                appointment['status'] = AppointmentStatus.PENDING.value
                print(f"Appointment {self.appointment_id} rescheduled to {new_time}.")
                break
