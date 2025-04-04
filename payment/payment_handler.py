class PaymentHandler:
    def __init__(self):
        # Remove Razorpay client since we're not using it
        pass

    def create_order(self, amount, currency="INR"):
        # Simply return a success response
        return {
            "status": "success",
            "amount": amount,
            "currency": currency,
            "order_id": "demo_order_123"  # dummy order id
        }