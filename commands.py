def sign_up():
    print("Sign Up:")
    # Get user details from the user
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    user_type = input("Enter your user type (Patient/Staff): ")

    # Validate user type
    if user_type.lower() not in [UserType.PATIENT.lower(), UserType.STAFF.lower()]:
        print("Invalid user type. Please choose either Patient or Staff.")
        return None

    # Create a new User object
    new_user = User(username=username, password=password, user_type=user_type)

    # Add additional details if needed
    if user_type.lower() == UserType.PATIENT.lower():
        # Additional details for patients
        new_user.email = input("Enter your email: ")

    # Add logic for storing the user details in a database or list
    # For example, you might have a list like this:
    users.append(new_user)

    print("Sign up successful!")
    return new_user

def log_in():
    print("Log In:")
    # Get user credentials from the user
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    # Find the user in the list or database
    user = next((u for u in users if u.username == username and u.password == password), None)

    if user:
        print("Login successful!")
        return user
    else:
        print("Invalid username or password. Please try again.")
        return None

def handle_patient_command(user, choice):
    if choice == "1":
        # View Profile
        user.view_profile()
    elif choice == "2":
        # View Appointments
        user.view_appointments()
    elif choice == "3":
        # Book Appointment
        date_time = input("Enter the date and time for the appointment (YYYY-MM-DD HH:MM): ")
        clinic_id = int(input("Enter the clinic ID for the appointment: "))
        new_appointment = Appointment(status=AppointmentStatus.PENDING, date_time=date_time, user_id=user.user_id, clinic_id=clinic_id)
        new_appointment.register_patient_appointment()
    elif choice == "4":
        # Cancel Appointment
        appointment_id = int(input("Enter the appointment ID to cancel: "))
        appointment_to_cancel = next((appt for appt in appointments if appt['appointment_id'] == appointment_id), None)
        if appointment_to_cancel:
            cancel_appointment = Appointment(AppointmentStatus.PENDING, appointment_to_cancel['date_time'], user.user_id, appointment_to_cancel['clinic_id'])
            cancel_appointment.cancel_patient_appointment()
        else:
            print("Appointment not found.")
    elif choice == "5":
        # View Notifications
        user.view_notifications()
    elif choice == "6":
        # Update Profile
        new_email = input("Enter your new email (leave empty to keep current): ")
        new_password = input("Enter your new password (leave empty to keep current): ")
        user.update_profile(new_email=new_email, new_password=new_password)
    elif choice == "7":
        print("Logging out.")
        user = None
    else:
        print("Invalid command. Please enter a valid command number.")

def handle_admin_command(user, choice):
    if choice == "1":
        # Current Appointments
        user.view_appointments()
    elif choice == "2":
        # Remove Appointment
        appointment_id = int(input("Enter the appointment ID to remove: "))
        user.remove_appointment(appointment_id)
    elif choice == "3":
        # Add Appointment Capacity
        user.add_appointment_capacity()
    elif choice == "4":
        # Update Clinic Info
        new_address = input("Enter the new address for the clinic: ")
        new_phone = input("Enter the new phone number for the clinic: ")
        user.update_clinic_info(new_address=new_address, new_phone=new_phone)
    elif choice == "5":
        print("Logging out.")
        user = None
    else:
        print("Invalid command. Please enter a valid command number.")

def main():
    print("Welcome to the Clinic Reservation System!")

    current_user = None

    while True:
        if current_user:
            if current_user.user_type == UserType.PATIENT:
                print("\nPatient Commands:")
                print("1. View Profile")
                print("2. View Appointments")
                print("3. Book Appointment")
                print("4. Cancel Appointment")
                print("5. View Notifications")
                print("6. Update Profile")
                print("7. Logout")

                choice = input("Enter the number of the command you want to execute: ")

                handle_patient_command(current_user, choice)

            elif current_user.user_type == UserType.STAFF:
                print("\nAdmin Commands:")
                print("1. Current Appointments")
                print("2. Remove Appointment")
                print("3. Add Appointment Capacity")
                print("4. Update Clinic Info")
                print("5. Logout")

                choice = input("Enter the number of the command you want to execute: ")

                handle_admin_command(current_user, choice)

if __name__ == "__main__":
    main()