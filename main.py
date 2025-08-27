import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from services.auth_service import AuthService
from services.ride_service import RideService
from services.vehicle_service import VehicleService
from models.user import Rider, Driver, UserRole
from models.vehicle import Vehicle
from models.ride import RideStatus


class RideAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RideApp")

        # Services
        self.auth_service = AuthService()
        self.ride_service = RideService()
        self.vehicle_service = VehicleService()

        self.logged_in_user = None

        # Main Frame
        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack()

        self.show_main_menu()

    # ------------------- LOGIN / SIGNUP / RESET ---------------------
    def show_main_menu(self):
        self.clear_frame()
        tk.Label(self.frame, text="=== Welcome to RideApp ===", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self.frame, text="Login", width=20, command=self.login).pack(pady=5)
        tk.Button(self.frame, text="Signup", width=20, command=self.signup).pack(pady=5)
        tk.Button(self.frame, text="Update Password", width=20, command=self.update_password).pack(pady=5)
        tk.Button(self.frame, text="Exit", width=20, command=self.root.quit).pack(pady=5)

    def login(self):
        email = simpledialog.askstring("Login", "Enter Email:")
        pwd = simpledialog.askstring("Login", "Enter Password:", show="*")
        user = self.auth_service.login(email, pwd)
        if user:
            self.logged_in_user = user
            messagebox.showinfo("Login", "Login Successful")
            self.show_dashboard()
        else:
            messagebox.showerror("Login", "Invalid email or password")

    def signup(self):
        name = simpledialog.askstring("Signup", "Name:")
        email = simpledialog.askstring("Signup", "Email:")
        phone = simpledialog.askstring("Signup", "Phone (10 digits):")
        pwd = simpledialog.askstring("Signup", "Password:", show="*")
        role = simpledialog.askstring("Signup", "Role (rider/driver):").lower()

        next_id = self.auth_service.get_next_user_id()
        if role == "rider":
            user = Rider(next_id, name, email, phone, pwd, UserRole.RIDER)
        elif role == "driver":
            license_no = simpledialog.askstring("Signup", "License Number:")
            user = Driver(next_id, name, email, phone, pwd, license_no)
        else:
            messagebox.showerror("Signup", "Invalid role!")
            return

        try:
            user.validate_user()
            self.auth_service.register_user(user)
            messagebox.showinfo("Signup", "User registered successfully!")
        except ValueError as e:
            messagebox.showerror("Signup", f"{e}")

    def update_password(self):
        email = simpledialog.askstring("Update Password", "Enter registered email:")
        if email in self.auth_service.get_users():
            new_pwd = simpledialog.askstring("Update Password", "Enter new password:", show="*")
            self.auth_service.update_password(email, new_pwd)
            messagebox.showinfo("Password", " Password updated successfully")
        else:
            messagebox.showerror("Password", " No account found with this email.")

    # ------------------- DASHBOARD ---------------------
    def show_dashboard(self):
        self.clear_frame()
        if self.logged_in_user.role == UserRole.RIDER:
            tk.Label(self.frame, text="=== Rider Menu ===", font=("Arial", 14, "bold")).pack(pady=10)

            tk.Button(self.frame, text="Book Ride", width=25, command=self.book_ride).pack(pady=5)
            tk.Button(self.frame, text="Cancel Ride", width=25, command=self.cancel_ride).pack(pady=5)
            tk.Button(self.frame, text="Make Payment", width=25, command=self.make_payment).pack(pady=5)
            tk.Button(self.frame, text="Rate Ride", width=25, command=self.rate_ride).pack(pady=5)
            tk.Button(self.frame, text="Ride History", width=25, command=self.ride_history).pack(pady=5)
            tk.Button(self.frame, text="Update Password", width=25, command=self.update_password).pack(pady=5)
            tk.Button(self.frame, text="Logout", width=25, command=self.logout).pack(pady=5)

        else:  # Driver
            tk.Label(self.frame, text="=== Driver Menu ===", font=("Arial", 14, "bold")).pack(pady=10)

            tk.Button(self.frame, text="Accept Ride", width=25, command=self.accept_ride).pack(pady=5)
            tk.Button(self.frame, text="Change Ride Status", width=25, command=self.change_ride_status).pack(pady=5)
            tk.Button(self.frame, text="Register Vehicle", width=25, command=self.register_vehicle).pack(pady=5)
            tk.Button(self.frame, text="My Ride History", width=25, command=self.driver_history).pack(pady=5)
            tk.Button(self.frame, text="Update Password", width=25, command=self.update_password).pack(pady=5)
            tk.Button(self.frame, text="Logout", width=25, command=self.logout).pack(pady=5)

    # ------------------- RIDER FUNCTIONS ---------------------
    def book_ride(self):
        pickup = simpledialog.askstring("Book Ride", "Pickup:")
        drop = simpledialog.askstring("Book Ride", "Drop:")
        next_ride_id = self.ride_service.get_next_ride_id()
        ride_id = self.ride_service.request_ride(self.logged_in_user.user_id, pickup, drop, ride_id=next_ride_id)
        messagebox.showinfo("Book Ride", f" Ride booked with ID: {ride_id}")

    def cancel_ride(self):
        rid = simpledialog.askstring("Cancel Ride", "Enter Ride ID:")
        self.ride_service.cancel_ride(rid)
        messagebox.showinfo("Cancel Ride", f" Ride {rid} cancelled")

    def make_payment(self):
        rid = simpledialog.askstring("Payment", "Ride ID:")
        amt = float(simpledialog.askstring("Payment", "Amount:"))
        method = simpledialog.askstring("Payment", "Method (cash/card/upi):")
        self.ride_service.make_payment(rid, amt, method)
        messagebox.showinfo("Payment", f" Payment of {amt} done for Ride {rid}")

    def rate_ride(self):
        rid = simpledialog.askstring("Rate Ride", "Ride ID:")
        score = int(simpledialog.askstring("Rate Ride", "Score (1-5):"))
        comment = simpledialog.askstring("Rate Ride", "Comment:")
        self.ride_service.rate_ride(rid, self.logged_in_user.user_id, "driver1", score, comment)
        messagebox.showinfo("Rate Ride", f" Rated Ride {rid}")

    def ride_history(self):
        history = self.ride_service.get_rider_history(self.logged_in_user.user_id)
        if not history:
            messagebox.showinfo("History", "No rides found.")
        else:
            hist = "\n".join([f"Ride {r.get('ride_id')}: {r}" for r in history])
            messagebox.showinfo("History", hist)


    def accept_ride(self):
        rides = list(self.ride_service.load_rides())
        requested_rides = [r for r in rides if r.get("status") == RideStatus.REQUESTED.value]
        if not requested_rides:
            messagebox.showinfo("Accept Ride", "No requested rides available.")
            return

        # Choose first ride for simplicity
        ride_to_accept = requested_rides[0]
        vehicle_id = None
        for v in self.vehicle_service.load_vehicles().values():
            if v.get("driver_id") == self.logged_in_user.user_id:
                vehicle_id = v.get("vehicle_id")
                break
        if not vehicle_id:
            messagebox.showerror("Accept Ride", "You must register a vehicle first.")
            return
        update = {
            "driver_id": self.logged_in_user.user_id,
            "vehicle_id": vehicle_id,
            "status": "accepted"
        }
        updated_ride = {**ride_to_accept, **update}
        self.ride_service.save_ride(updated_ride)
        messagebox.showinfo("Accept Ride", f"✅ Ride {ride_to_accept['ride_id']} accepted!")

    def change_ride_status(self):
        rides = list(self.ride_service.load_rides())
        my_rides = [r for r in rides if r.get("driver_id") == self.logged_in_user.user_id and r.get("status") in ["accepted", "in_progress"]]
        if not my_rides:
            messagebox.showinfo("Change Status", "No rides to update.")
            return
        ride = my_rides[0]  # pick first for simplicity
        if ride["status"] == "accepted":
            ride["status"] = "in_progress"
        elif ride["status"] == "in_progress":
            ride["status"] = "completed"
        self.ride_service.save_ride(ride)
        messagebox.showinfo("Change Status", f" Ride {ride['ride_id']} updated to {ride['status']}")

    def register_vehicle(self):
        make = simpledialog.askstring("Vehicle", "Make:")
        model = simpledialog.askstring("Vehicle", "Model:")
        plate = simpledialog.askstring("Vehicle", "Plate Number:")
        color = simpledialog.askstring("Vehicle", "Color:")
        year = int(simpledialog.askstring("Vehicle", "Year:"))
        next_vid = self.vehicle_service.get_next_vehicle_id()
        v = Vehicle(make, model, plate, color, year)
        self.vehicle_service.register_vehicle(self.logged_in_user.user_id, v, next_vid)
        messagebox.showinfo("Vehicle", f" Vehicle {plate} registered successfully")

    def driver_history(self):
        my_rides = list(self.ride_service.load_rides())
        my_rides = [r for r in my_rides if r.get("driver_id") == self.logged_in_user.user_id]
        if not my_rides:
            messagebox.showinfo("History", "No rides found.")
        else:
            hist = "\n".join([f"Ride {r.get('ride_id')}: {r}" for r in my_rides])
            messagebox.showinfo("History", hist)

    def logout(self):
        self.logged_in_user = None
        self.show_main_menu()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RideAppGUI(root)
    root.mainloop()

# from services.auth_service import AuthService
# from services.ride_service import RideService
# from services.vehicle_service import VehicleService
# from models.user import Rider, Driver, UserRole
# from models.vehicle import Vehicle
# from models.ride import RideStatus


# def main():
#     auth_service = AuthService()
#     ride_service = RideService()
#     vehicle_service = VehicleService()
#     logged_in_user = None
#     active_vehicle_id = None   # track driver's chosen vehicle

#     while True:   # keep looping back to main menu after logout
#         logged_in_user = None
#         active_vehicle_id = None

#         # --- Main Menu ---
#         while not logged_in_user:
#             print("\n=== Welcome to RideApp ===")
#             print("1. Login")
#             print("2. Signup")
#             print("3. Update Password")
#             print("4. Exit")
#             choice = input("Choose: ")

#             if choice == "1":
#                 email = input("Email: ")
#                 pwd = input("Password: ")
#                 logged_in_user = auth_service.login(email, pwd)

#                 # If driver logs in, check for multiple vehicles
#                 if logged_in_user and logged_in_user.role == UserRole.DRIVER:
#                     vehicles = vehicle_service.load_vehicles()
#                     my_vehicles = [v for v in vehicles.values() if v.get("driver_id") == logged_in_user.user_id]
#                     if not my_vehicles:
#                         print(" No vehicles registered. Please register before accepting rides.")
#                     elif len(my_vehicles) == 1:
#                         active_vehicle_id = my_vehicles[0]["vehicle_id"]
#                     else:
#                         print("\nYou have multiple vehicles. Please select one:")
#                         for idx, v in enumerate(my_vehicles, 1):
#                             print(f"{idx}. {v.get('make')} {v.get('model')} | Plate: {v.get('plate_number')}")
#                         sel = int(input("Enter choice: ")) - 1
#                         if 0 <= sel < len(my_vehicles):
#                             active_vehicle_id = my_vehicles[sel]["vehicle_id"]
#                         else:
#                             print("Invalid choice, defaulting to first vehicle.")
#                             active_vehicle_id = my_vehicles[0]["vehicle_id"]

#             elif choice == "2":
#                 name = input("Name: ")
#                 email = input("Email: ")
#                 phone = input("Phone (10 digits): ")
#                 pwd = input("Password: ")
#                 role = input("Role (rider/driver): ").lower()

#                 next_id = auth_service.get_next_user_id()
#                 if role == "rider":
#                     user = Rider(next_id, name, email, phone, pwd, UserRole.RIDER)
#                 elif role == "driver":
#                     license_no = input("License Number: ")
#                     user = Driver(next_id, name, email, phone, pwd, license_no)
#                 else:
#                     print("Invalid role!")
#                     continue

#                 try:
#                     user.validate_user()
#                     auth_service.register_user(user)
#                 except ValueError as e:
#                     print(f" {e}")

#             elif choice == "3":
#                 email = input("Enter your registered email: ")
#                 if email in auth_service.get_users():
#                     new_pwd = input("Enter new password: ")
#                     auth_service.update_password(email, new_pwd)
#                 else:
#                     print("No account found with this email.")

#             elif choice == "4":
#                 print("Goodbye!")
#                 return

#         # --- Rider Menu ---
#         while logged_in_user and logged_in_user.role == UserRole.RIDER:
#             print("\n=== Rider Menu ===")
#             print("1. Book Ride")
#             print("2. Cancel Ride")
#             print("3. Make Payment")
#             print("4. Rate Ride")
#             print("5. Ride History")
#             print("6. Update Password")
#             print("7. Logout")
#             c = input("Choose: ")

#             if c == "1":
#                 #  Restriction: check if rider has unfinished rides
#                 history = ride_service.get_rider_history(logged_in_user.user_id)
#                 unfinished = [r for r in history if r.get("status") != "completed"]
#                 if unfinished:
#                     print("You cannot book a new ride until all your previous rides are completed.")
#                     continue

#                 pickup = input("Pickup: ")
#                 drop = input("Drop: ")
#                 next_ride_id = ride_service.get_next_ride_id()
#                 ride_id = ride_service.request_ride(logged_in_user.user_id, pickup, drop, ride_id=next_ride_id)
#                 print(f"Ride booked with ID: {ride_id}")

#             elif c == "2":
#                 rid = input("Ride ID: ")
#                 ride_service.cancel_ride(rid)

#             elif c == "3":
#                 rid = input("Ride ID: ")
#                 amt = float(input("Amount: "))
#                 method = input("Method (cash/card/upi): ")
#                 ride_service.make_payment(rid, amt, method)

#             elif c == "4":
#                 rid = input("Ride ID: ")
#                 score = int(input("Score (1-5): "))
#                 comment = input("Comment: ")
#                 ride_service.rate_ride(rid, logged_in_user.user_id, "driver1", score, comment)

#             elif c == "5":
#                 history = ride_service.get_rider_history(logged_in_user.user_id)
#                 if not history:
#                     print("No rides found.")
#                 else:
#                     for ride in history:
#                         ride_id = ride.get("ride_id", "N/A")
#                         print(f"\nRide {ride_id}: {ride}")

#             elif c == "6":
#                 new_pwd = input("Enter new password: ")
#                 auth_service.update_password(logged_in_user.email, new_pwd)
#                 logged_in_user.password = new_pwd

#             elif c == "7":
#                 print("Logging out...")
#                 break   # return to main menu

#         # --- Driver Menu ---
#         while logged_in_user and logged_in_user.role == UserRole.DRIVER:
#             print("\n=== Driver Menu ===")
#             print("1. Accept a Ride")
#             print("2. Change Ride Status")
#             print("3. Register Vehicle")
#             print("4. My Ride History")
#             print("5. Update Password")
#             print("6. Logout")
#             c = input("Choose: ")

#             if c == "1":
#                 #  Restriction: driver can only accept 1 active ride
#                 rides = list(ride_service.load_rides())
#                 active_rides = [r for r in rides if r.get("driver_id") == logged_in_user.user_id and r.get("status") in ["accepted", "in_progress"]]
#                 if active_rides:
#                     print(" You already have an active ride. Complete it before accepting another.")
#                     continue

#                 requested_rides = [r for r in rides if r.get("status") == RideStatus.REQUESTED.value]
#                 requested_rides = sorted(requested_rides, key=lambda x: x.get("ride_date", ""), reverse=True)[:5]
#                 if not requested_rides:
#                     print("No requested rides available.")
#                 else:
#                     print("\n--- Recent Requested Rides ---")
#                     for idx, ride in enumerate(requested_rides, 1):
#                         print(f"{idx}. Ride ID: {ride.get('ride_id')} | Pickup: {ride.get('pickup_location')} | Drop: {ride.get('drop_location')} | Fare: {ride.get('fare')}")
#                     sel = input("Select a ride to accept (1-5): ")
#                     try:
#                         sel_idx = int(sel) - 1
#                         if 0 <= sel_idx < len(requested_rides):
#                             ride_to_accept = requested_rides[sel_idx]
#                             ride_id = ride_to_accept["ride_id"]

#                             if not active_vehicle_id:
#                                 print(" You must register/select a vehicle before accepting rides.")
#                                 continue

#                             update = {
#                                 "driver_id": logged_in_user.user_id,
#                                 "vehicle_id": active_vehicle_id,
#                                 "status": "accepted"
#                             }
#                             updated_ride = {**ride_to_accept, **update}
#                             ride_service.save_ride(updated_ride)
#                             print(f"Ride {ride_id} accepted!")
#                             try:
#                                 ride_service.send_ride_accepted_email(ride_id)
#                             except Exception as e:
#                                 print(f"Failed to send acceptance email: {e}")
#                         else:
#                             print("Invalid selection.")
#                     except Exception as e:
#                         print(f"Error: {e}")

#             elif c == "2":
#                 rides = list(ride_service.load_rides())
#                 my_rides = [r for r in rides if r.get("driver_id") == logged_in_user.user_id and r.get("status") in ["accepted", "in_progress"]]
#                 if not my_rides:
#                     print("No rides to update.")
#                 else:
#                     print("\n--- My Active Rides ---")
#                     for idx, ride in enumerate(my_rides, 1):
#                         print(f"{idx}. Ride ID: {ride.get('ride_id')} | Status: {ride.get('status')} | Pickup: {ride.get('pickup_location')} | Drop: {ride.get('drop_location')}")
#                     sel = input("Select a ride to update status (1-N): ")
#                     try:
#                         sel_idx = int(sel) - 1
#                         if 0 <= sel_idx < len(my_rides):
#                             ride = my_rides[sel_idx]
#                             current_status = ride.get("status")
#                             print("Choose new status:")
#                             if current_status == "accepted":
#                                 print("1. in_progress")
#                                 print("2. completed")
#                                 valid_status = ["in_progress", "completed"]
#                             elif current_status == "in_progress":
#                                 print("1. completed")
#                                 valid_status = ["completed"]
#                             else:
#                                 print("Status cannot be changed.")
#                                 continue
#                             status_choice = input("Enter option: ")
#                             try:
#                                 status_idx = int(status_choice) - 1
#                                 if 0 <= status_idx < len(valid_status):
#                                     new_status = valid_status[status_idx]
#                                     ride["status"] = new_status
#                                     ride_service.save_ride(ride)
#                                     print(f"Ride {ride.get('ride_id')} status updated to {new_status}.")
#                                     if new_status == "completed":
#                                         try:
#                                             ride_service.send_ride_acceptance_email(ride)
#                                             print("Email sent to rider after ride completed.")
#                                         except Exception as e:
#                                             print(f"Failed to send completion email: {e}")
#                                 else:
#                                     print("Invalid status selection.")
#                             except Exception as e:
#                                 print(f"Error: {e}")
#                         else:
#                             print("Invalid selection.")
#                     except Exception as e:
#                         print(f"Error: {e}")

#             elif c == "3":
#                 make = input("Vehicle Make: ")
#                 model = input("Vehicle Model: ")
#                 plate = input("Plate Number: ")
#                 color = input("Color: ")
#                 year = int(input("Year: "))
#                 next_vid = vehicle_service.get_next_vehicle_id()
#                 v = Vehicle(make, model, plate, color, year)
#                 vehicle_service.register_vehicle(logged_in_user.user_id, v, next_vid)
#                 print("Vehicle registered successfully.")

#             elif c == "4":
#                 my_rides = list(ride_service.load_rides())
#                 my_rides = [r for r in my_rides if r.get("driver_id") == logged_in_user.user_id]
#                 if not my_rides:
#                     print("No rides found.")
#                 else:
#                     print("\n--- My Ride History ---")
#                     for ride in my_rides:
#                         print(f"Ride {ride.get('ride_id')}: {ride}")

#             elif c == "5":
#                 new_pwd = input("Enter new password: ")
#                 auth_service.update_password(logged_in_user.email, new_pwd)
#                 logged_in_user.password = new_pwd

#             elif c == "6":
#                 print("Logging out...")
#                 break   # return to main menu


# if __name__ == "__main__":
#     main()

