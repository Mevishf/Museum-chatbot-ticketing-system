from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from chatbot import get_chatbot_response
import uuid
import json
from datetime import datetime
from pathlib import Path
import qrcode
from io import BytesIO
import base64

app = Flask(__name__, 
    template_folder='.', # Look for templates in root directory
    static_folder='static', # For CSS and JS files
    static_url_path='/static' # URL prefix for static files
)
CORS(app)

BOOKINGS_DIR = Path("bookings")
BOOKINGS_DIR.mkdir(exist_ok=True)

def calculate_price(people_data):
    total_price = 0
    for person in people_data:
        if person.lower() == 'india' or person.lower() == 'indian':
            total_price += 20  # Price for Indian citizens
        else:
            total_price += 500  # Price for non-Indian citizens
    return total_price

def generate_qr_code(booking_data):
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction
        box_size=10,
        border=4,
    )
    
    # Format booking data for QR code
    qr_data = {
        'booking_id': booking_data['booking_id'],
        'museum': booking_data['museum'],
        'date': booking_data['date'],
        'time': booking_data['time'],
        'tickets': booking_data['tickets'],
        'nationality': booking_data['nationality'],
        'timestamp': booking_data['timestamp'],
        'status': booking_data['status']
    }
    
    # Convert to JSON string for QR code
    qr_json = json.dumps(qr_data)
    qr.add_data(qr_json)
    qr.make(fit=True)

    # Create QR code image with custom styling
    img = qr.make_image(
        fill_color="black", 
        back_color="white"
    )
    
    # Add logo or watermark if needed
    # img = add_logo_to_qr(img)  # Optional: Add museum logo to QR
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return qr_base64

def verify_qr_code(qr_data):
    try:
        # Parse QR data
        booking_data = json.loads(qr_data)
        
        # Check if booking exists
        booking_file = BOOKINGS_DIR / f"{booking_data['booking_id']}.json"
        if not booking_file.exists():
            return False
            
        # Verify booking details
        with open(booking_file) as f:
            stored_booking = json.load(f)
            
        # Check if booking is valid
        return (
            stored_booking['status'] == 'completed' and
            stored_booking['booking_id'] == booking_data['booking_id'] and
            stored_booking['date'] == booking_data['date'] and
            stored_booking['time'] == booking_data['time']
        )
    except:
        return False

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/chat')
def chat():
    return render_template('index.html')

@app.route('/payment')
def payment():
    # Get all parameters
    museum_name = request.args.get('museum_name')
    number_of_people = request.args.get('number_of_people', 1, type=int)
    nationality = request.args.get('nationality', 'indian')
    date = request.args.get('date')
    time = request.args.get('time')
    total_price = request.args.get('price', calculate_price([nationality] * number_of_people))

    print(f"Payment page parameters: {request.args}")  # Debug log
    
    return render_template('payment/index.html', 
                         museum_name=museum_name,
                         number_of_people=number_of_people,
                         nationality=nationality,
                         date=date,
                         time=time,
                         total_price=total_price)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_input = data.get('message')
    response = get_chatbot_response(user_input, "user1")
    return jsonify({'response': response})

@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        print("Received form data:", request.form)  # Debug log
        
        # Generate a unique booking ID
        booking_id = str(uuid.uuid4())
        
        # Get form data
        museum = request.form.get('museum')
        tickets = request.form.get('tickets')
        date = request.form.get('date')
        time = request.form.get('time')
        price = request.form.get('price')
        nationality = request.form.get('nationality')
        payment_method = request.form.get('payment_method')
        
        # Validate required fields
        if not all([museum, tickets, date, time, price, nationality, payment_method]):
            missing_fields = [field for field in ['museum', 'tickets', 'date', 'time', 'price', 'nationality', 'payment_method'] 
                            if not request.form.get(field)]
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Create booking data
        booking_data = {
            'booking_id': booking_id,
            'museum': museum,
            'tickets': tickets,
            'date': date,
            'time': time,
            'price': price,
            'nationality': nationality,
            'payment_method': payment_method,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        print("Created booking data:", booking_data)  # Debug log
        
        # Save booking data to a file
        booking_file = BOOKINGS_DIR / f"{booking_id}.json"
        with open(booking_file, 'w') as f:
            json.dump(booking_data, f, indent=4)
        
        return jsonify({
            'success': True,
            'booking_id': booking_id,
            'message': 'Payment processed successfully'
        })
        
    except Exception as e:
        print(f"Payment processing error: {str(e)}")  # Debug log
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/payment/success')
def payment_success():
    booking_id = request.args.get('booking_id')
    if not booking_id:
        return redirect(url_for('welcome'))
    
    try:
        # Read booking data
        booking_file = BOOKINGS_DIR / f"{booking_id}.json"
        with open(booking_file) as f:
            booking_data = json.load(f)
        
        # Generate QR code
        qr_code = generate_qr_code(booking_data)
        
        return render_template('payment/success.html', 
                             booking=booking_data,
                             qr_code=qr_code)
    except:
        return redirect(url_for('welcome'))

@app.route('/verify_ticket/<booking_id>')
def verify_ticket(booking_id):
    try:
        booking_file = BOOKINGS_DIR / f"{booking_id}.json"
        with open(booking_file) as f:
            booking_data = json.load(f)
        return jsonify({
            'valid': True,
            'booking': booking_data
        })
    except:
        return jsonify({
            'valid': False,
            'message': 'Invalid ticket'
        })

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Get response from chatbot (including Gemini)
        response = get_chatbot_response(user_message)
        
        return jsonify({
            'response': response
        })
    except Exception as e:
        print(f"Error getting response: {str(e)}")
        return jsonify({
            'response': "Sorry, I'm having trouble responding right now."
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
