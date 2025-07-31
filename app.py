from flask import Flask, render_template, request, redirect, session, url_for
import pyotp
import qrcode
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Setup a global secret key for OTP generation (this could be user-specific)
otp_secret = pyotp.random_base32()

@app.route('/')
def index():
    # Generate OTP URI and QR Code
    totp = pyotp.TOTP(otp_secret)
    uri = totp.provisioning_uri(name="user@example.com", issuer_name="My2FAApp")
    
    # Generate QR Code
    img = qrcode.make(uri)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode()

    # Render the OTP page with QR code
    return render_template("s3.html", qr_code=qr_code)


@app.route('/verify', methods=['POST'])
def verify():
    entered_otp = request.form.get('otp')
    totp = pyotp.TOTP(otp_secret)

    if totp.verify(entered_otp):
        session['authenticated'] = True
        return redirect(url_for('dashboard'))
    else:
        # Re-render the OTP page with error and regenerated QR
        uri = totp.provisioning_uri(name="user@example.com", issuer_name="My2FAApp")
        img = qrcode.make(uri)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code = base64.b64encode(buffer.getvalue()).decode()

        return render_template("s3.html", qr_code=qr_code, error="Invalid OTP. Please try again.")


@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template("dashboard.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
