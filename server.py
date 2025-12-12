import os
import datetime
import logging
import sqlite3
import json
import ftplib
import ssl
import threading
import stripe
import csv
import io
from flask import Flask, request, jsonify, send_from_directory, abort, redirect, make_response
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

app = Flask(__name__)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Security Configuration ---
# 1. Externalize Secrets (Environment Variables)
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "CHANGE_ME_IN_PROD")
BAMBU_IP = os.environ.get("BAMBU_IP", "192.168.1.108")
BAMBU_ACCESS_CODE = os.environ.get("BAMBU_ACCESS_CODE", "CHANGE_ME")

# Stripe Configuration (loaded from .env)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "") # Optional for webhook verification
stripe.api_key = STRIPE_SECRET_KEY

# Email Configuration
# To use Gmail: Generate an App Password at https://myaccount.google.com/apppasswords
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "orders@gassstro.com") 
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")  # MUST be set in .env
SMTP_SERVER = os.environ.get("SMTP_SERVER", "mail.gassstro.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# 2. CORS Restriction
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

# 3. Rate Limiting (Prevent DDoS/Spam)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://"
)

# Configuration
EXPORT_DIR = "exports"
DB_FILE = "orders.db"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'stl', 'obj', 'step', '3mf', 'gcode'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
DOMAIN = os.environ.get("DOMAIN", "http://localhost:8080") # Frontend runs on port 8080

# Database Configuration - PostgreSQL or SQLite
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    logging.info("🐘 Using PostgreSQL database")
else:
    logging.info("📁 Using SQLite database (local dev)")

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Security Headers ---
@app.after_request
def add_security_headers(response):
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Force HTTPS (only in production with HTTPS enabled)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy - Prevent XSS attacks
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://js.stripe.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self' https://api.stripe.com; "
        "frame-src https://js.stripe.com https://checkout.stripe.com; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self' https://checkout.stripe.com"
    )
    
    # Referrer Policy - Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy - Disable unnecessary browser features
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

# --- Database Setup ---
def get_db_connection():
    """Get database connection (PostgreSQL or SQLite)"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        conn = get_db_connection()
        
        return conn

def init_db():
    """Initialize database tables"""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT,
                quantity INTEGER,
                total_price REAL,
                date_event TEXT,
                message TEXT,
                filename TEXT,
                filepath TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                stripe_session_id TEXT,
                payment_status TEXT DEFAULT 'Unpaid',
                original_filepath TEXT,
                notes TEXT
            )
        ''')
        
        # Add notes column if missing
        try:
            c.execute('SELECT notes FROM orders LIMIT 1')
        except:
            c.execute('ALTER TABLE orders ADD COLUMN notes TEXT')
            
        conn.commit()
        conn.close()
    else:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                quantity INTEGER,
                total_price REAL,
                date_event TEXT,
                message TEXT,
                filename TEXT,
                filepath TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                stripe_session_id TEXT,
                payment_status TEXT DEFAULT 'Unpaid',
                original_filepath TEXT,
                notes TEXT
            )
        ''')
        
        # Simple migration: check if columns exist, if not add them
        try:
            c.execute('SELECT stripe_session_id FROM orders LIMIT 1')
        except sqlite3.OperationalError:
            print("Migrating DB: Adding stripe_session_id")
            c.execute('ALTER TABLE orders ADD COLUMN stripe_session_id TEXT')
            
        try:
            c.execute('SELECT payment_status FROM orders LIMIT 1')
        except sqlite3.OperationalError:
            print("Migrating DB: Adding payment_status")
            c.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'Unpaid'")

        try:
            c.execute('SELECT original_filepath FROM orders LIMIT 1')
        except sqlite3.OperationalError:
            print("Migrating DB: Adding original_filepath")
            c.execute("ALTER TABLE orders ADD COLUMN original_filepath TEXT")
            
        try:
            c.execute('SELECT notes FROM orders LIMIT 1')
        except sqlite3.OperationalError:
            print("Migrating DB: Adding notes")
            c.execute("ALTER TABLE orders ADD COLUMN notes TEXT")

        conn.commit()
        conn.close()

init_db()

from converter import LogoConverter

# Initialize Converter
converter = LogoConverter()

# --- Helpers ---
def send_confirmation_email(to_email, order_data):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        logging.warning("Email not configured. Skipping confirmation email.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = f"GASsstro System <{SMTP_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = f"COMMISSIONE ACCETTATA: Ordine #{order_data['id']}"

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ border-bottom: 2px solid #FF0000; padding-bottom: 10px; margin-bottom: 30px; }}
                .brand {{ font-size: 24px; font-weight: bold; letter-spacing: -1px; color: #000; }}
                .status-track {{ display: flex; margin: 30px 0; font-size: 12px; color: #999; }}
                .step {{ margin-right: 20px; color: #000; font-weight: bold; }}
                .step.active {{ color: #FF0000; }}
                .order-card {{ background: #f4f4f4; padding: 25px; border-radius: 4px; margin: 30px 0; border-left: 4px solid #FF0000; }}
                .footer {{ margin-top: 50px; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 20px; }}
                .button {{ display: inline-block; background: #000; color: #fff; padding: 10px 20px; text-decoration: none; font-size: 14px; margin-top: 20px; border-radius: 2px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="brand">GASsstro.</div>
            </div>

            <p style="font-size: 18px;">Gentile {order_data['name']},</p>
            <p>La tua commissione è stata ufficialmente registrata nei nostri sistemi.</p>

            <div class="status-track">
                <span class="step active">● RICEVUTO</span>
                <span class="step">○ PAGAMENTO</span>
                <span class="step">○ PRODUZIONE</span>
                <span class="step">○ SPEDIZIONE</span>
            </div>

            <p>Abbiamo preso in carico il file <strong>{order_data['filename']}</strong>.</p>
            
            <p>Stato Pagamento: <strong>{order_data.get('payment_status', 'Pending')}</strong></p>

            <div class="order-card">
                <h3 style="margin-top:0; font-size:14px; text-transform:uppercase; letter-spacing:1px; color:#666;">Dettagli Commissione</h3>
                <p style="margin: 5px 0;"><strong>ID Progetto:</strong> #{order_data['id']}</p>
                <p style="margin: 5px 0;"><strong>Quantità:</strong> {order_data['quantity']} unità</p>
                <p style="margin: 5px 0;"><strong>Totale Stimato:</strong> €{order_data['total_price']}</p>
            </div>

            <p>Se il file supera i controlli di qualità e il pagamento è confermato, la produzione inizierà entro 24 ore.</p>

            <br>
            <p>Saluti,</p>
            <p><strong>Il Team di GASsstro</strong><br>
            <span style="font-size: 12px; color: #666;">Swiss Precision, Italian Taste.</span></p>

            <div class="footer">
                &copy; 2025 GASsstro Inc. | Milano, Italia<br>
                Questa è una notifica automatica. Non rispondere direttamente a questa email.
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmessage(msg)
        server.quit()
        logging.info(f"Confirmation email sent to {to_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_auth(req):
    token = req.headers.get('X-Admin-Token')
    if not token or token != ADMIN_TOKEN:
        if req.args.get('token') == ADMIN_TOKEN:
            return True
        return False
    return True

# --- Routes ---

# --- Background Tasks ---
def cleanup_old_files():
    """Deletes files in exports/ older than 30 days."""
    try:
        cutoff = datetime.datetime.now() - datetime.timedelta(days=30)
        cutoff_timestamp = cutoff.timestamp()
        
        # Traverse exports directory
        for root, dirs, files in os.walk(EXPORT_DIR):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    if os.path.getmtime(filepath) < cutoff_timestamp:
                        os.remove(filepath)
                        logging.info(f"Deleted old file: {filepath}")
                except Exception as e:
                    logging.warning(f"Error deleting {filepath}: {e}")
                    
        logging.info("Cleanup complete.")
    except Exception as e:
        logging.error(f"Cleanup failed: {e}")

def process_order_background(order_id, original_filepath, stl_filepath, email_info):
    """Handles STL conversion and Email sending in background."""
    logging.info(f"Background processing started for Order #{order_id}")
    
    conversion_success = False
    final_filepath = original_filepath # Default to original if fails
    final_filename = os.path.basename(original_filepath)

    # 1. STL Conversion
    try:
        # Check if it needs conversion (png/jpg)
        ext = final_filename.rsplit('.', 1)[1].lower()
        if ext in ['png', 'jpg', 'jpeg']:
            logging.info(f"Converting {final_filename} to STL...")
            converter.generate_stl(original_filepath, stl_filepath)
            
            # If successful, update DB to point to STL
            if os.path.exists(stl_filepath):
                final_filepath = stl_filepath
                final_filename = os.path.basename(stl_filepath)
                conversion_success = True
                
                # Update DB
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('UPDATE orders SET filename = ?, filepath = ? WHERE id = ?', 
                         (final_filename, final_filepath, order_id))
                conn.commit()
                conn.close()
                logging.info(f"Conversion successful: {final_filename}")
            else:
                logging.error("Conversion ran but file missing.")
    except Exception as e:
        logging.error(f"Conversion failed for Order #{order_id}: {e}")

    # 2. Send Email (Only if everything is ready - or strictly speaking, we confirmed receipt)
    # The email template says "Commission Accepted". We send it regardless of conversion outcome?
    # Yes, manual review will catch bad files.
    
    # Update email info with final filename (if changed)
    email_info['filename'] = final_filename
    
    # We send the "Receipt" email immediately now. 
    # Or maybe we wait for payment? 
    # Let's keep sending "Receipt" email but maybe mark as unpaid.
    send_confirmation_email(email_info['email'], email_info)

# --- Routes ---

@app.route('/api/create-payment', methods=['POST'])
@limiter.limit("20 per minute")
def create_payment():
    if 'file' not in request.files:
        return jsonify({"error": "No file attached"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Input Sanitization
    name = str(request.form.get('name', 'Unknown'))[:100] 
    email = str(request.form.get('email', 'Unknown'))[:100]
    message = str(request.form.get('message', ''))[:500]
    
    try:
        quantity = int(request.form.get('quantity', 0))
        total_price = float(request.form.get('total_price', 0))
    except ValueError:
        return jsonify({"error": "Invalid number format"}), 400

    date_event = request.form.get('date', '')

    try:
        # Save file TEMPORARILY (not creating order yet!)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        temp_dir = os.path.join(EXPORT_DIR, "temp", today)
        os.makedirs(temp_dir, exist_ok=True)
        
        clean_name = secure_filename(file.filename)
        timestamp = int(datetime.datetime.now().timestamp())
        temp_filename = f"{timestamp}_{clean_name}"
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        file.save(temp_filepath)
        
        logging.info(f"File saved temporarily at {temp_filepath}. Creating Stripe session...")

        # Create Stripe Checkout Session IMMEDIATELY
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Servizio Stampa Timbro GASsstro',
                        'description': f"{name} - {quantity} pz",
                    },
                    'unit_amount': int(total_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=DOMAIN + '/success.html?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=DOMAIN + '/cancel.html',
            metadata={
                'temp_file_path': temp_filepath,
                'temp_filename': temp_filename,
                'name': name,
                'email': email,
                'quantity': str(quantity),
                'total_price': str(total_price),
                'message': message,
                'date_event': date_event
            },
            shipping_address_collection={
                'allowed_countries': ['IT', 'CH', 'FR', 'DE', 'AT'],
            }
        )
        
        logging.info(f"Stripe session created: {checkout_session.id}. Awaiting payment to create order.")
        
        return jsonify({
            "message": "Payment session created",
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }), 200

    except Exception as e:
        logging.error(f"Error creating payment session: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400
        
    try:
        conn = get_db_connection()
        
        c = conn.cursor()
        c.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = c.fetchone()
        conn.close()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
            
        # Calculate amount in cents
        amount = int(order['total_price'] * 100)
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'], # Add 'paypal' if needed and enabled in Stripe Dashboard
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': 'Servizio Stampa Timbro GASsstro',
                        'description': f"Ordine #{order_id} - {order['quantity']} pz",
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=DOMAIN + '/success.html?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=DOMAIN + '/cancel.html',
            metadata={
                'order_id': order_id
            },
            shipping_address_collection={
                'allowed_countries': ['IT', 'CH', 'FR', 'DE', 'AT'],
            }
        )
        
        # Save session ID
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE orders SET stripe_session_id = ? WHERE id = ?', (checkout_session.id, order_id))
        conn.commit()
        conn.close()
        
        return jsonify({'url': checkout_session.url})
        
    except Exception as e:
        logging.error(f"Stripe Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # If you have a webhook secret, verify it. For now, in dev, we might skip strict verification if secret is empty
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        else:
            event = json.loads(payload)
            
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Retrieve order data from metadata
        metadata = session.get('metadata', {})
        temp_file_path = metadata.get('temp_file_path')
        temp_filename = metadata.get('temp_filename')
        name = metadata.get('name')
        email = metadata.get('email')
        quantity = int(metadata.get('quantity', 0))
        total_price = float(metadata.get('total_price', 0))
        message = metadata.get('message', '')
        date_event = metadata.get('date_event', '')
        
        if temp_file_path and os.path.exists(temp_file_path):
            logging.info(f"Payment successful! Creating order for {name}...")
            
            try:
                # Move file from temp to permanent location
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                final_dir = os.path.join(EXPORT_DIR, today)
                os.makedirs(final_dir, exist_ok=True)
                
                final_filepath = os.path.join(final_dir, temp_filename)
                os.rename(temp_file_path, final_filepath)
                
                # Prepare STL path for background job
                stl_filename = f"{temp_filename.rsplit('.', 1)[0]}.stl"
                stl_filepath = os.path.join(final_dir, stl_filename)
                
                # NOW create the order in DB (ONLY after payment!)
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('''
                    INSERT INTO orders (name, email, quantity, total_price, date_event, message, filename, filepath, original_filepath, payment_status, stripe_session_id, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid', ?, 'Processing')
                ''', (name, email, quantity, total_price, date_event, message, temp_filename, final_filepath, final_filepath, session['id']))
                order_id = c.lastrowid
                conn.commit()
                conn.close()
                
                logging.info(f"Order #{order_id} created AFTER payment for {name}. Starting file processing...")
                
                # Prepare Email Data
                email_info = {
                    "id": order_id,
                    "name": name,
                    "email": email,
                    "filename": temp_filename,
                    "quantity": quantity,
                    "total_price": total_price,
                    "payment_status": "Paid"
                }
                
                # Start Background Thread for STL conversion and email
                t = threading.Thread(target=process_order_background, args=(order_id, final_filepath, stl_filepath, email_info))
                t.start()
                
                logging.info(f"Order #{order_id} processing started in background.")
                
            except Exception as e:
                logging.error(f"Error creating order after payment: {e}")
        else:
            logging.warning(f"Payment received but temp file not found: {temp_file_path}")
            
    return 'Success', 200


@app.route('/api/orders', methods=['GET'])
def get_orders():
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = get_db_connection()
        
        c = conn.cursor()
        c.execute('SELECT * FROM orders ORDER BY created_at DESC')
        rows = c.fetchall()
        orders = [dict(row) for row in rows]
        conn.close()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({"error": "Missing status"}), 400

    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Status updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/printer/upload/<int:order_id>', methods=['POST'])
def upload_to_printer(order_id):
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        conn = get_db_connection()
        
        c = conn.cursor()
        c.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = c.fetchone()
        conn.close()

        if not order:
            return jsonify({"error": "Order not found"}), 404
            
        filepath = order['filepath']
        if not os.path.exists(filepath):
            return jsonify({"error": "File missing locally"}), 404

        filename = os.path.basename(filepath)

        logging.info(f"Connecting to Printer at {BAMBU_IP}...")
        
        ftps = ftplib.FTP_TLS()
        ftps.timeout = 10
        ftps.connect(BAMBU_IP, 990)
        ftps.login('bblp', BAMBU_ACCESS_CODE)
        ftps.prot_p()
        
        with open(filepath, 'rb') as file:
            ftps.storbinary(f'STOR {filename}', file)
            
        ftps.quit()
        
        logging.info(f"Successfully uploaded {filename} to printer")
        return jsonify({"message": "File sent to printer!"}), 200

    except Exception as e:
        logging.error(f"Printer Error: {e}")
        return jsonify({"error": f"Printer Connection Failed: {str(e)}"}), 500

@app.route('/api/download', methods=['GET'])
def download():
    # Protected Endpoint
    if not check_auth(request):
        return "Unauthorized", 401

    path = request.args.get('path')
    if not path:
        return "Missing path", 400
    
    path = os.path.normpath(path)
    if not path.startswith(EXPORT_DIR) or '..' in path:
        return "Access denied", 403
        
    return send_from_directory('.', path, as_attachment=True)

# --- NEW ADMIN API ENDPOINTS ---

@app.route('/api/admin/login', methods=['POST'])
@limiter.limit("10 per minute")
def admin_login():
    """Admin authentication endpoint"""
    data = request.get_json()
    password = data.get('password')
    
    if password == ADMIN_TOKEN:
        # In production, use JWT tokens
        return jsonify({
            "success": True,
            "token": ADMIN_TOKEN,
            "message": "Login successful"
        }), 200
    else:
        return jsonify({"error": "Invalid password"}), 401

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get dashboard statistics"""
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Total orders
        c.execute('SELECT COUNT(*) as count FROM orders')
        total_orders = dict(c.fetchone())['count']
        
        # Total revenue
        c.execute('SELECT SUM(total_price) as revenue FROM orders WHERE payment_status = %s' if USE_POSTGRES else 'SELECT SUM(total_price) as revenue FROM orders WHERE payment_status = ?', ('Paid',))
        total_revenue = dict(c.fetchone())['revenue'] or 0
        
        # Orders by status
        c.execute('SELECT status, COUNT(*) as count FROM orders GROUP BY status')
        orders_by_status = {dict(row)['status']: dict(row)['count'] for row in c.fetchall()}
        
        # Orders by payment status
        c.execute('SELECT payment_status, COUNT(*) as count FROM orders GROUP BY payment_status')
        orders_by_payment = {dict(row)['payment_status']: dict(row)['count'] for row in c.fetchall()}
        
        # Recent orders (last 7 days)
        c.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as count, SUM(total_price) as revenue
            FROM orders
            WHERE created_at >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''' if USE_POSTGRES else '''
            SELECT DATE(created_at) as date, COUNT(*) as count, SUM(total_price) as revenue
            FROM orders
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''')
        recent_activity = [dict(row) for row in c.fetchall()]
        
        # Today's orders
        c.execute('''
            SELECT COUNT(*) as count FROM orders
            WHERE DATE(created_at) = CURRENT_DATE
        ''' if USE_POSTGRES else '''
            SELECT COUNT(*) as count FROM orders
            WHERE DATE(created_at) = DATE('now')
        ''')
        today_orders = dict(c.fetchone())['count']
        
        conn.close()
        
        return jsonify({
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "orders_by_status": orders_by_status,
            "orders_by_payment": orders_by_payment,
            "recent_activity": recent_activity,
            "today_orders": today_orders
        }), 200
        
    except Exception as e:
        logging.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/search', methods=['GET'])
def search_orders():
    """Search and filter orders"""
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get query parameters
        query = request.args.get('q', '')
        status = request.args.get('status', '')
        payment_status = request.args.get('payment_status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Build dynamic query
        sql = 'SELECT * FROM orders WHERE 1=1'
        params = []
        
        if query:
            sql += ' AND (name LIKE %s OR email LIKE %s OR CAST(id AS TEXT) LIKE %s)' if USE_POSTGRES else ' AND (name LIKE ? OR email LIKE ? OR CAST(id AS TEXT) LIKE ?)'
            search_term = f'%{query}%'
            params.extend([search_term, search_term, search_term])
        
        if status:
            sql += ' AND status = %s' if USE_POSTGRES else ' AND status = ?'
            params.append(status)
        
        if payment_status:
            sql += ' AND payment_status = %s' if USE_POSTGRES else ' AND payment_status = ?'
            params.append(payment_status)
        
        if date_from:
            sql += ' AND DATE(created_at) >= %s' if USE_POSTGRES else ' AND DATE(created_at) >= ?'
            params.append(date_from)
        
        if date_to:
            sql += ' AND DATE(created_at) <= %s' if USE_POSTGRES else ' AND DATE(created_at) <= ?'
            params.append(date_to)
        
        sql += ' ORDER BY created_at DESC'
        
        c.execute(sql, params)
        rows = c.fetchall()
        orders = [dict(row) for row in rows]
        conn.close()
        
        return jsonify(orders), 200
        
    except Exception as e:
        logging.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/<int:order_id>/notes', methods=['GET', 'POST'])
def manage_order_notes(order_id):
    """Get or update order notes"""
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        if request.method == 'GET':
            c.execute('SELECT notes FROM orders WHERE id = %s' if USE_POSTGRES else 'SELECT notes FROM orders WHERE id = ?', (order_id,))
            row = c.fetchone()
            conn.close()
            
            if not row:
                return jsonify({"error": "Order not found"}), 404
            
            return jsonify({"notes": dict(row)['notes']}), 200
        
        else:  # POST
            data = request.get_json()
            notes = data.get('notes', '')
            
            c.execute('UPDATE orders SET notes = %s WHERE id = %s' if USE_POSTGRES else 'UPDATE orders SET notes = ? WHERE id = ?', (notes, order_id))
            conn.commit()
            conn.close()
            
            return jsonify({"message": "Notes updated"}), 200
            
    except Exception as e:
        logging.error(f"Notes error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/export', methods=['GET'])
def export_orders():
    """Export orders to CSV"""
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM orders ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['ID', 'Name', 'Email', 'Quantity', 'Total Price', 'Date Event', 
                        'Status', 'Payment Status', 'Created At', 'Message', 'Filename'])
        
        # Data
        for row in rows:
            row_dict = dict(row)
            writer.writerow([
                row_dict['id'],
                row_dict['name'],
                row_dict['email'],
                row_dict['quantity'],
                row_dict['total_price'],
                row_dict.get('date_event', ''),
                row_dict['status'],
                row_dict['payment_status'],
                row_dict['created_at'],
                row_dict.get('message', ''),
                row_dict.get('filename', '')
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=orders_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv'
        
        return response
        
    except Exception as e:
        logging.error(f"Export error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/new-count', methods=['GET'])
def get_new_orders_count():
    """Get count of new orders since last check"""
    if not check_auth(request):
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Get timestamp from query param (last check time)
        last_check = request.args.get('since', '')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        if last_check:
            c.execute('''
                SELECT COUNT(*) as count FROM orders
                WHERE created_at > %s
            ''' if USE_POSTGRES else '''
                SELECT COUNT(*) as count FROM orders
                WHERE created_at > ?
            ''', (last_check,))
        else:
            # Return orders from last hour
            c.execute('''
                SELECT COUNT(*) as count FROM orders
                WHERE created_at >= NOW() - INTERVAL '1 hour'
            ''' if USE_POSTGRES else '''
                SELECT COUNT(*) as count FROM orders
                WHERE created_at >= datetime('now', '-1 hour')
            ''')
        
        count = dict(c.fetchone())['count']
        conn.close()
        
        return jsonify({"new_orders": count}), 200
        
    except Exception as e:
        logging.error(f"New count error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    return jsonify({"status": "ok", "db": db_type}), 200


if __name__ == '__main__':
    # Startup tasks
    cleanup_thread = threading.Thread(target=cleanup_old_files)
    cleanup_thread.start()

    # WARNING: This is a development server. 
    # For production, use: gunicorn -w 4 -b 0.0.0.0:5000 server:app
    print("⚠️  Starting in Development Mode")
    print("🔒 Debug mode: DISABLED for security")
    print("📝 For production, use Gunicorn or uWSGI")
    app.run(debug=False, port=5000)

