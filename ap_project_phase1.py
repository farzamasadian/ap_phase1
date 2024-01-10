import json
from datetime import datetime, timedelta
from enum import Enum
import re
import random
import requests


class Notification:
    """
    Represents a notification in the Clinic Reservation System.
    
    Attributes:
    - username: The username of the user to whom the notification is sent.
    - message: The content of the notification.
    - date_time: The date and time when the notification was created.
    """
    def __init__(self, username, message):
        self.username = username
        self.message = message
        self.date_time = datetime.now().isoformat()

    def to_dict(self):
        """
        Converts the notification object to a dictionary for easier handling and storage.
        """
        return {
            'username': self.username,
            'message': self.message,
            'date_time': self.date_time
        }

    def send_notification(self):
        """
        Simulates sending a notification by printing it to the console.
        """
        print(f"Notification sent to {self.username} at {self.date_time}: {self.message}")
        notifications.append(self.to_dict())

    @staticmethod
    def send_bulk_notifications(users, message):
        """
        Sends a notification to a list of users.
        
        Attributes:
        - users: List of users to whom the notification is to be sent.
        - message: The content of the notification.
        """
        for user in users:
            notification = Notification(user['username'], message)
            notification.send_notification()
            print(f"Sent notification to {user['username']}")


# Admin-specific functionalities
class Admin(User):
    """
    Represents an admin (secretary) in the Clinic Reservation System.
    Inherits from the User class and adds admin-specific functionalities.
    """
    def __init__(self, user_id, username, email, password, user_type: UserType):
        super().__init__(user_id, username, email, password, user_type)

    def admin_menu(self):
        """
        Displays the admin menu with options for admin-specific actions.
        """
        print("1. Current Appointments\n2. Remove Appointment\n3. Add Appointment Capacity\n4. Logout")
        choice = input("Enter your choice: ")
        self.handle_admin_command(choice)

    def handle_admin_command(self, choice):
        """
        Handles the admin's choice from the menu and directs to the appropriate functionality.
        
        Attributes:
        - choice: The choice made by the admin from the menu.
        """
        if choice == "1":
            # Show current appointments
            self.view_appointments()
        elif choice == "2":
            # Remove an appointment
            self.remove_appointment()
        elif choice == "3":
            # Add appointment capacity
            self.add_appointment_capacity()
        elif choice == "4":
            # Logout
            print("Logging out.")
        else:
            print("Invalid choice. Please try again.")

    def remove_appointment(self, appointment_id=None):
        """
        Allows the admin to remove an appointment from the system.
        If an appointment_id is not provided, it prompts the admin to enter one.
        """
        if appointment_id is None:
            self.view_appointments()
            try:
                appointment_id = int(input("Enter the appointment ID to remove: "))
            except ValueError:
                print("Invalid input. Please enter a valid appointment ID.")
                return
        
        global appointments
        appointments = [appt for appt in appointments if appt['appointment_id'] != appointment_id]
        print(f"Appointment {appointment_id} has been removed.")

    def add_appointment_capacity(self):
        """
        Allows the admin to add new appointment slots to the system.
        """
        date = input("Enter the date for the new appointment slot (YYYY-MM-DD): ")
        time = input("Enter the time for the new appointment slot (HH:MM): ")
        datetime_str = f"{date} {time}"
        try:
            # Simulate checking for existing slots before adding
            existing_slots = [appt for appt in appointments if appt['date_time'] == datetime_str]
            if existing_slots:
                print("An appointment slot already exists at this time.")
            else:
                global appointment_id_counter
                new_appointment = {
                    'appointment_id': appointment_id_counter,
                    'status': AppointmentStatus.PENDING.value,  # Use a valid status from the AppointmentStatus enum
                    'date_time': datetime_str,
                    'user_id': None,  # No user assigned yet
                    'clinic_id': self.clinic_id  # Assuming the admin is associated with a clinic
                }
                appointments.append(new_appointment)
                appointment_id_counter += 1
                print(f"Added new appointment slot on {datetime_str}.")
        except Exception as e:
            print(f"An error occurred: {e}")


def fetch_available_appointments():
    """
    Fetches available appointments from an external API and displays them.
    """
    try:
        response = requests.get('http://127.0.0.1:5000/available')
        if response.status_code == 200:
            available_appointments = response.json()
            print("Available appointments:")
            for appt in available_appointments:
                print(appt)
        else:
            print("Failed to fetch available appointments.")
    except Exception as e:
        print(f"An error occurred: {e}")


def adjust_clinic_capacity(clinic_id, new_capacity):
    """
    Adjusts the capacity of a clinic by sending a POST request to an external API.

    This function aims to update the number of available appointments for a specific clinic.
    It sends a payload with the clinic ID and the new desired capacity to the external API endpoint.
    Upon success, it confirms the adjustment; otherwise, it reports a failure.

    Attributes:
    clinic_id: int
        The unique identifier of the clinic for which the capacity is being adjusted.
    new_capacity: int
        The new capacity (number of available appointments) to set for the clinic.

    The function catches and reports any exceptions that occur during the process,
    such as network issues or problems with the external API.
    """
    try:
        payload = {'clinic_id': clinic_id, 'new_capacity': new_capacity}
        response = requests.post('http://127.0.0.1:5000/adjust_capacity', json=payload)
        if response.status_code == 200:
            print(f"Clinic capacity adjusted successfully: {response.json()}")
        else:
            print("Failed to adjust clinic capacity.")
    except Exception as e:
        print(f"An error occurred: {e}")









# Mock function to simulate fetching available appointments from an external API
def mock_fetch_available_appointments():
    return [
        {'date_time': '2023-12-23 10:00', 'clinic_id': 1},
        {'date_time': '2023-12-24 11:00', 'clinic_id': 1}
    ]

def test_user_scenario():
    # Step 1: Create a Clinic and Services
    clinic = Clinic(clinic_id_counter, "Health Clinic", "123 Health St.", "123-456-7890", ["General Checkup"])
    clinics.append(clinic.to_dict())
    clinic.set_availability('2023-12-23', True)

    # Step 2: User Signup and Login
    user = User(1, "JohnDoe", "john@example.com", "password123", UserType.PATIENT)
    user.sign_up()
    user.login("password123")

    # Step 3: Fetch Available Appointments (mocked)
    available_appointments = mock_fetch_available_appointments()
    print("Available appointments:")
    for appt in available_appointments:
        print(appt)

    # Step 4: Book an Appointment
    chosen_appt = available_appointments[0]
    new_appointment = Appointment(AppointmentStatus.PENDING, chosen_appt['date_time'], user.user_id, chosen_appt['clinic_id'])
    new_appointment.register_patient_appointment()

    # Step 5: View Current Appointments
    user.view_appointments()


def test_admin_scenario():
    # Step 1: Admin Signup and Login
    # Assuming the admin 'AdminUser' is already created from the previous script
    admin = Admin(2, "AdminUser", "admin@example.com", "adminpassword", UserType.STAFF)
    admin.sign_up()
    admin.generate_otp()  # Simulate sending an OTP
    admin.login(admin.otp)  # Admin logs in with OTP

    # Step 2: View Current Appointments
    print("\n[Admin: Viewing Current Appointments]")
    admin.view_appointments()  # Admin views all appointments

    # Step 3: Remove an Appointment
    # For this test, we assume the admin knows the appointment ID to remove
    print("\n[Admin: Removing an Appointment]")
    appointment_to_remove = 1  # Assuming an appointment with this ID exists
    admin.remove_appointment(appointment_to_remove)  # Admin removes an appointment

    # Step 4: Add Appointment Capacity
    print("\n[Admin: Adding Appointment Capacity]")
    admin.clinic_id = 1  # Assuming the admin is associated with clinic 1
    admin.add_appointment_capacity()  # Admin adds a new appointment slot

    # View Current Appointments again to see the changes
    print("\n[Admin: Viewing Updated Appointments]")
    admin.view_appointments()  # Admin views all appointments again to see the changes


# Run the test scenario
test_user_scenario()

# Run the admin test scenario
test_admin_scenario()



