import json
from datetime import datetime, timedelta
from enum import Enum
import re
import random
import requests
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('clinic_reservation_system.db')
    return conn

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
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (username, email, password, user_type) VALUES (?, ?, ?, ?)", 
                           (self.username, self.email, self.password, self.user_type))
            conn.commit()
            print(f"User {self.username} signed up successfully.")
        except sqlite3.IntegrityError:
            print("Username already exists.")
        finally:
            conn.close()
   
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
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                if new_address:
                    cursor.execute("UPDATE Clinics SET address = ? WHERE clinic_id = ?", (new_address, self.clinic_id))
                if new_phone:
                    cursor.execute("UPDATE Clinics SET phone_info = ? WHERE clinic_id = ?", (new_phone, self.clinic_id))
                conn.commit()
                print(f"Clinic {self.name}'s info updated successfully.")
            except sqlite3.Error as e:
                print(f"Clinic Error")

        
        

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
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Appointments WHERE date_time = ? AND clinic_id = ?", 
                           (self.date_time, self.clinic_id))
            if cursor.fetchone():
                print("This time slot is already booked.")
            else:
                cursor.execute("INSERT INTO Appointments (status, date_time, user_id, clinic_id) VALUES (?, ?, ?, ?)", 
                               (self.status, self.date_time, self.user_id, self.clinic_id))
                conn.commit()
                print(f"Appointment registered successfully for user")
        except:
            print(f"Appointment Error")
    def cancel_patient_appointment(self):
        """
        Cancels the appointment by changing its status to canceled.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Appointments SET status = ? WHERE appointment_id = ?", 
                        (AppointmentStatus.CANCELED.value, self.appointment_id))
            if cursor.rowcount == 0:
                print("Appointment not found.")
            else:
                conn.commit()
                print(f"Appointment {self.appointment_id} has been canceled.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()


    def reschedule_patient_appointment(self, new_time):
        """
        Reschedules the appointment to a new time and resets its status to pending.
        
        Attributes:
        - new_time: The new time to which the appointment is rescheduled.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Appointments SET date_time = ?, status = ? WHERE appointment_id = ?", 
                        (new_time, AppointmentStatus.PENDING.value, self.appointment_id))
            if cursor.rowcount == 0:
                print("Appointment not found.")
            else:
                conn.commit()
                print(f"Appointment {self.appointment_id} rescheduled to {new_time}.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()


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
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for user in users:
                notification = Notification(user['username'], message)
                cursor.execute("INSERT INTO Notifications (username, message, date_time) VALUES (?, ?, ?)", 
                            (notification.username, notification.message, notification.date_time))
                print(f"Sent notification to {user['username']}")
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()


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



def adjust_clinic_capacity(code, reserved):
    """
    Adjusts the capacity of a clinic by sending a POST request to an external API.

    This function aims to update the number of reserved appointments for a specific clinic.
    It sends a payload with the clinic code and the number of reserved appointments to the external API endpoint.
    Upon success, it confirms the adjustment; otherwise, it reports a failure.

    Attributes:
    code: int
        The unique code of the clinic for which the reserved appointments are being updated.
    reserved: int
        The number of reserved appointments to set for the clinic.

    The function catches and reports any exceptions that occur during the process,
    such as network issues or problems with the external API.
    """
    try:
        payload = {'clinic code': code, 'reserved appointments': reserved}
        response = requests.post('https://localhost/slots', json=payload)
   
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
















            

    
                    
 










