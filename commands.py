def main():
    print("Welcome to the Clinic Reservation System!")

    current_user = None

    while True:
        print("\nAvailable commands:")
        print("1. Sign Up")
        print("2. Log In")
        print("3. View Profile")
        print("4. View Appointments")
        print("5. Book Appointment")
        print("6. Cancel Appointment")
        print("7. View Notifications")
        print("8. Update Profile")
        print("9. Logout")

        choice = input("Enter the number of the command you want to execute: ")

        if choice == "1":
            # Sign Up
            username = input("Enter your username: ")
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            user_type = UserType.PATIENT  # You can modify this based on your requirements
            new_user = User(user_id=len(users) + 1, username=username, email=email, password=password, user_type=user_type)
            new_user.sign_up()
        elif choice == "2":
            # Log In
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            user_found = next((user for user in users if user['username'] == username), None)
            if user_found:
                current_user = User(user_id=user_found['user_id'], username=user_found['username'], email=user_found['email'], password=user_found['password'], user_type=UserType(user_found['user_type']))
                if current_user.login(password):
                    print(f"Welcome back, {current_user.username}!")
                else:
                    print("Login failed.")
            else:
                print("User not found.")
        elif choice == "3":
            # View Profile
            if current_user:
                print("User Profile:")
                print(current_user.to_dict())
            else:
                print("Please log in first.")
        elif choice == "4":
            # View Appointments
            if current_user:
                current_user.view_appointments()
            else:
                print("Please log in first.")
        elif choice == "5":
            # Book Appointment
            if current_user:
                date_time = input("Enter the date and time for the appointment (YYYY-MM-DD HH:MM): ")
                clinic_id = int(input("Enter the clinic ID for the appointment: "))
                new_appointment = Appointment(status=AppointmentStatus.PENDING, date_time=date_time, user_id=current_user.user_id, clinic_id=clinic_id)
                new_appointment.register_patient_appointment()
            else:
                print("Please log in first.")
        elif choice == "6":
            # Cancel Appointment
            if current_user:
                appointment_id = int(input("Enter the appointment ID to cancel: "))
                appointment_to_cancel = next((appt for appt in appointments if appt['appointment_id'] == appointment_id), None)
                if appointment_to_cancel:
                    cancel_appointment = Appointment(AppointmentStatus.PENDING, appointment_to_cancel['date_time'], current_user.user_id, appointment_to_cancel['clinic_id'])
                    cancel_appointment.cancel_patient_appointment()
                else:
                    print("Appointment not found.")
            else:
                print("Please log in first.")
        elif choice == "7":
            # View Notifications
            if current_user:
                current_user.view_notifications()
            else:
                print("Please log in first.")
        elif choice == "8":
            # Update Profile
            if current_user:
                new_email = input("Enter your new email (leave empty to keep current): ")
                new_password = input("Enter your new password (leave empty to keep current): ")
                current_user.update_profile(new_email=new_email, new_password=new_password)
            else:
                print("Please log in first.")
        elif choice == "9":
            print("Logging out.")
            current_user = None
        else:
            print("Invalid command. Please enter a valid command number.")

if __name__ == "__main__":
    main()
