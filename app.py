from flask import redirect, url_for

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Skip payment processing
    return redirect(url_for('success'))  # This will redirect to success.html

@app.route('/success')
def success():
    return render_template('success.html')