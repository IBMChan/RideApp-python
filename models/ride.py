
from enum import Enum

class Payment:
    def __init__(self, ride_id, amount, method):
        self.ride_id = ride_id
        self.amount = amount
        self.method = method

    def __str__(self):
        return f"Payment of ₹{self.amount} via {self.method} for Ride {self.ride_id} is successful"

class Rating:
    def __init__(self, ride_id, rider_id, driver_id, score, comment=""):
        self.ride_id = ride_id
        self.rider_id = rider_id
        self.driver_id = driver_id
        self.score = score
        self.comment = comment

    def __str__(self):
        return f"Rating {self.score}/5 - {self.comment}"

class RideStatus(Enum):
    REQUESTED = "Requested"
    ONGOING = "Ongoing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Ride:
    ride_counter = 1

    def __init__(self, rider_id, pickup, drop):
        self.ride_id = f"R{Ride.ride_counter}"
        Ride.ride_counter += 1
        self.rider_id = rider_id
        self.driver_id = None
        self.pickup = pickup
        self.drop = drop
        self.status = RideStatus.REQUESTED
        self.payment = None  # Will be set to Payment instance after payment
        self.rating = None   # Will be set to Rating instance after rating

    def add_payment(self, amount, method):
        self.payment = Payment(self.ride_id, amount, method)
        return self.payment

    def add_rating(self, rider_id, driver_id, score, comment=""):
        self.rating = Rating(self.ride_id, rider_id, driver_id, score, comment)
        return self.rating

    def __str__(self):
        base = f"Ride {self.ride_id}: {self.pickup} -> {self.drop} | {self.status.value}"
        if self.payment:
            base += f"\n  {self.payment}"
        if self.rating:
            base += f"\n  {self.rating}"
        return base
