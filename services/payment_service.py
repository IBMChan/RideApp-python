from models.ride import Payment

class PaymentService:
    def __init__(self):
        self.payments = []

    def make_payment(self, ride_id, amount, method):
        payment = Payment(ride_id, amount, method)
        self.payments.append(payment)
        print(payment)
        return payment

    def get_payments_by_ride(self, ride_id):
        return [p for p in self.payments if p.ride_id == ride_id]

    def get_all_payments(self):
        return self.payments
