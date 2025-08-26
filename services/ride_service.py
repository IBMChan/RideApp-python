
from models.ride import Ride, RideStatus
from models.ride import Payment, Rating
from utils.distance import calculate_distance
from utils.decorators import log_action
from utils.db import rides_col, users_col, vehicles_col
import io
import os
from bson import ObjectId
import smtplib
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv





class RideService:
    def send_ride_accepted_email(self, ride_id: str):
                import smtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                from dotenv import load_dotenv
                import os
                # Load email credentials from .env
                load_dotenv(dotenv_path=r'C:/Users/ChandanaG/OneDrive - IBM/Desktop/Ride_app/env/.env')
                SENDER_EMAIL = os.getenv("sender_email")
                SENDER_PASSWORD = os.getenv("app_password")
                SMTP_SERVER = "smtp.gmail.com"
                SMTP_PORT = 587

                # Fetch ride (status must be 'accepted')
                ride = rides_col.find_one({"ride_id": ride_id, "status": "accepted"})
                if not ride:
                        print("❌ Ride not found or not accepted.")
                        return

                # Fetch rider and driver from users collection
                rider = users_col.find_one({"user_id": ride["rider_id"]})
                driver = users_col.find_one({"user_id": ride["driver_id"]})
                vehicle = vehicles_col.find_one({"vehicle_id": ride["vehicle_id"]})

                if not (rider and driver and vehicle):
                        print("❌ Missing rider/driver/vehicle details.")
                        return

                # Build Email
                msg = MIMEMultipart("alternative")
                msg["From"] = SENDER_EMAIL
                msg["To"] = rider["email"]
                msg["Subject"] = f"IBM Ride App - Your Ride Has Been Accepted (Ride ID {ride['ride_id']})"

                html = f"""
                <html>
                    <body style='font-family: Arial, sans-serif;'>
                        <h2 style='color: #003366;'>✅ Your Ride has been accepted!</h2>
                        <h3>Ride Details</h3>
                        <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
                            <tr><th>Ride ID</th><td>{ride['ride_id']}</td></tr>
                            <tr><th>Rider Name</th><td>{rider.get('full_name', 'N/A')}</td></tr>
                            <tr><th>Phone</th><td>{rider.get('phone', 'N/A')}</td></tr>
                            <tr><th>Pickup Location</th><td>{ride.get('pickup_location', 'N/A')}</td></tr>
                            <tr><th>Drop Location</th><td>{ride.get('drop_location', 'N/A')}</td></tr>
                            <tr><th>Fare</th><td>₹{ride.get('fare', 'N/A')}</td></tr>
                            <tr><th>Status</th><td>{ride.get('status', 'N/A')}</td></tr>
                            <tr><th>Ride Date</th><td>{ride.get('ride_date', 'N/A')}</td></tr>
                        </table>
                        <h3>Driver & Vehicle Details</h3>
                        <table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse; width: 100%;'>
                            <tr><th>Driver Name</th><td>{driver.get('full_name', 'N/A')}</td></tr>
                            <tr><th>Phone</th><td>{driver.get('phone', 'N/A')}</td></tr>
                            <tr><th>License Number</th><td>{driver.get('license_number', 'N/A')}</td></tr>
                            <tr><th>Vehicle</th><td>{vehicle.get('make', '')} {vehicle.get('model', '')} ({vehicle.get('year', '')})</td></tr>
                            <tr><th>Registration No.</th><td>{vehicle.get('registration_number', 'N/A')}</td></tr>
                            <tr><th>Color</th><td>{vehicle.get('color', 'N/A')}</td></tr>
                        </table>
                    </body>
                </html>
                """
                msg.attach(MIMEText(html, "html"))

                # Send Email
                try:
                        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                                server.starttls()
                                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                                server.send_message(msg)
                        print(f"📩 Email sent to {rider['email']} for Ride ID {ride['ride_id']}")
                except Exception as e:
                        print(f"❌ Failed to send acceptance email: {e}")
    def send_ride_acceptance_email(self, ride_doc):
        load_dotenv(dotenv_path=r'C:/Users/ChandanaG/OneDrive - IBM/Desktop/Ride_app/env/.env')
        sender_email = os.getenv("sender_email")
        app_password = os.getenv("app_password")
        # Fetch rider info
        rider = users_col.find_one({"user_id": ride_doc["rider_id"]})
        driver = users_col.find_one({"user_id": ride_doc.get("driver_id")})
        vehicle = vehicles_col.find_one({"vehicle_id": ride_doc.get("vehicle_id")})
        receiver_email = rider["email"] if rider else None
        if not receiver_email:
            print("Rider email not found, cannot send completion email.")
            return

        # PDF 1: Completed Ride Details (Beautified key-value pairs)
        pdf1_buffer = io.BytesIO()
        doc1 = SimpleDocTemplate(pdf1_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story1 = []
        title1 = Paragraph("<b><font size=16 color='#003366'>IBM Ride App - Ride Completed</font></b>", styles["Title"])
        story1.append(title1)
        story1.append(Spacer(1, 20))

        # Beautified Ride Details
        ride_details = [
            ("<b>Ride ID:</b>", str(ride_doc.get("ride_id", "ND"))),
            ("<b>Rider Name:</b>", rider.get("full_name", "ND") if rider else "ND"),
            ("<b>Rider Phone:</b>", rider.get("phone", "ND") if rider else "ND"),
            ("<b>Pickup Location:</b>", ride_doc.get("pickup_location", "ND")),
            ("<b>Drop Location:</b>", ride_doc.get("drop_location", "ND")),
            ("<b>Total Distance (km):</b>", str(ride_doc.get("distance_km", "ND"))),
            ("<b>Fare (₹):</b>", str(ride_doc.get("fare", "ND"))),
            ("<b>Estimated Time:</b>", "~30 min"),
            ("<b>Status:</b>", ride_doc.get("status", "ND")),
        ]
        for label, value in ride_details:
            story1.append(Paragraph(f"{label} <font color='#333333'>{value}</font>", styles["Normal"]))
            story1.append(Spacer(1, 6))

        story1.append(Spacer(1, 16))
        story1.append(Paragraph("<b><font size=14 color='#003366'>Driver & Vehicle Details</font></b>", styles["Heading2"]))
        story1.append(Spacer(1, 10))
        driver_details = [
            ("<b>Driver ID:</b>", str(driver.get("user_id", "ND")) if driver else "ND"),
            ("<b>Vehicle ID:</b>", str(vehicle.get("vehicle_id", "ND")) if vehicle else "ND"),
            ("<b>License Number:</b>", driver.get("license_number", "ND") if driver else "ND"),
            ("<b>Driver Phone:</b>", driver.get("phone", "ND") if driver else "ND"),
            ("<b>Completed At:</b>", str(ride_doc.get("completed_at", ride_doc.get("accepted_at", "ND")))),
        ]
        for label, value in driver_details:
            story1.append(Paragraph(f"{label} <font color='#333333'>{value}</font>", styles["Normal"]))
            story1.append(Spacer(1, 6))

        doc1.build(story1)
        pdf1_buffer.seek(0)

        # PDF 2: Past Ride Details
        pdf2_buffer = io.BytesIO()
        doc2 = SimpleDocTemplate(pdf2_buffer, pagesize=letter)
        story2 = []
        title2 = Paragraph("<b><font size=16 color='#003366'>IBM Ride App - Past Ride Details</font></b>", styles["Title"])
        story2.append(title2)
        story2.append(Spacer(1, 20))
        # Fetch all past rides for this rider
        past_rides = list(rides_col.find({"rider_id": ride_doc["rider_id"]}))
        headers2 = ["Ride ID", "Pickup", "Drop", "Status", "Fare", "Ride Date"]
        table_data2 = [headers2]
        for r in past_rides:
            row = [
                str(r.get("ride_id", "ND")),
                r.get("pickup_location", "ND"),
                r.get("drop_location", "ND"),
                r.get("status", "ND"),
                str(r.get("fare", r.get("fair", "ND"))),
                str(r.get("ride_date", "ND"))[:19].replace("T", " ") if r.get("ride_date") else "ND"
            ]
            table_data2.append(row)
        table2 = Table(table_data2, repeatRows=1, colWidths=[60, 80, 80, 60, 60, 120])
        table2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story2.append(table2)
        doc2.build(story2)
        pdf2_buffer.seek(0)

        # Compose email
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = "IBM Ride App - Ride Completed & Past Ride Details"
        html_body = f"""
        <html>
          <body style='font-family: Arial, sans-serif; line-height: 1.6;'>
            <h2 style='color: #003366;'>Your Ride Has Been Completed!</h2>
            <p>Hello {rider.get('full_name', 'Rider') if rider else ''},</p>
            <p>Thank you for riding with us! Your ride <b>{ride_doc.get('ride_id')}</b> has been successfully completed. Please find attached:</p>
            <ul>
              <li><b>Completed Ride Details</b></li>
              <li><b>Your Ride History</b></li>
            </ul>
            <p>We hope you had a pleasant experience. We look forward to serving you again!</p>
            <p>Best Regards,<br>
            <b>IBM Ride App - Notification Service</b></p>
            <hr>
            <p style='font-size: 12px; color: grey;'>This is an automated email. Please do not reply.</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html_body, "html"))
        # Attach PDFs
        part1 = MIMEBase("application", "octet-stream")
        part1.set_payload(pdf1_buffer.read())
        encoders.encode_base64(part1)
        part1.add_header("Content-Disposition", "attachment; filename=Ride_Completed.pdf")
        msg.attach(part1)
        part2 = MIMEBase("application", "octet-stream")
        part2.set_payload(pdf2_buffer.read())
        encoders.encode_base64(part2)
        part2.add_header("Content-Disposition", "attachment; filename=Ride_History.pdf")
        msg.attach(part2)
        # Send Email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
        print(f"Completion email sent to {receiver_email}")

    def get_next_ride_id(self) -> str:
        rides = list(rides_col.find())
        max_id = 0
        for r in rides:
            rid = r.get("ride_id", "")
            rid_str = str(rid)
            if rid_str and rid_str[0].upper() == 'R' and rid_str[1:].isdigit():
                max_id = max(max_id, int(rid_str[1:]))
        return f"R{max_id+1:03d}"
    def __init__(self):
        pass


    def load_rides(self):
        return list(rides_col.find())


    def save_ride(self, ride_doc):
        rides_col.update_one({"ride_id": ride_doc["ride_id"]}, {"$set": ride_doc}, upsert=True)

    @log_action("Request Ride")
    def request_ride(self, rider_id: str, pickup: str, drop: str, ride_id: str = None,
                     lat1: float = 12.9, lon1: float = 77.6,
                     lat2: float = 13.0, lon2: float = 77.7):
        if not ride_id:
            ride_id = self.get_next_ride_id()
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        price = distance * 10
        new_ride = {
            "ride_id": ride_id,
            "rider_id": rider_id,
            "pickup_location": pickup,
            "drop_location": drop,
            "status": RideStatus.REQUESTED.value,
            "distance_km": distance,
            "fare": price,
            "payment": None,
            "ratings": []
        }
        self.save_ride(new_ride)
        print(f"Ride {ride_id}: {pickup} → {drop}, {distance} km, ₹{price}")
        return ride_id

    def cancel_ride(self, ride_id: str):
        result = rides_col.update_one({"ride_id": ride_id}, {"$set": {"status": RideStatus.CANCELLED.value}})
        if result.matched_count:
            print(f"Ride {ride_id} cancelled")
        else:
            print("Ride not found.")

    def make_payment(self, ride_id: str, amount: float, method: str):
        payment = {
            "amount": amount,
            "method": method,
            "status": "completed"
        }
        result = rides_col.update_one({"ride_id": ride_id}, {"$set": {"payment": payment, "status": RideStatus.COMPLETED.value}})
        if result.matched_count:
            print(f"Payment successful for {ride_id}: {amount} via {method}")
            print(f"Ride {ride_id} status updated to COMPLETED.")
        else:
            print("Ride not found.")

    def rate_ride(self, ride_id: str, given_by: str, given_to: str, score: int, comment: str):
        rating = {
            "given_by": given_by,
            "given_to": given_to,
            "score": score,
            "comment": comment
        }
        result = rides_col.update_one({"ride_id": ride_id}, {"$push": {"ratings": rating}})
        if result.matched_count:
            print(f"Ride {ride_id} rated {score}/5")
        else:
            print("Ride not found.")

    def get_rider_history(self, rider_id: str):
        return list(rides_col.find({"rider_id": rider_id}))
