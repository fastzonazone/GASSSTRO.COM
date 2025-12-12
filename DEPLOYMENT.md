# 🚀 Deployment Guide - GASsstro Payment System

## Pre-Deployment Checklist

### 1. Environment Variables

Create a `.env` file with the following variables:

```bash
# Stripe (PRODUCTION KEYS!)
STRIPE_SECRET_KEY=sk_live_YOUR_LIVE_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Domain
DOMAIN=https://yourdomain.com

# Admin Security
ADMIN_TOKEN=GENERATE_STRONG_RANDOM_TOKEN_HERE

# Email (SMTP)
SMTP_EMAIL=orders@yourdomain.com
SMTP_PASSWORD=your_smtp_password
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587

# Optional: CORS (comma-separated domains)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional: 3D Printer
BAMBU_IP=192.168.1.108
BAMBU_ACCESS_CODE=your_printer_code
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize Database

The database will be created automatically on first run. To verify:

```bash
python3 -c "from server import init_db; init_db()"
```

### 4. Configure Stripe Webhook

1. Go to Stripe Dashboard → Developers → Webhooks
2. Add endpoint: `https://yourdomain.com/api/webhook`
3. Select event: `checkout.session.completed`
4. Copy the webhook secret to `.env` as `STRIPE_WEBHOOK_SECRET`

### 5. Test in Staging

Before going live, test with Stripe test keys:

```bash
# Use test keys in .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

Test the complete flow:
1. Upload file
2. Complete payment with test card `4242 4242 4242 4242`
3. Verify order appears in admin panel
4. Check email was sent

### 6. Deploy Backend

#### Option A: Gunicorn (Recommended)

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 server:app
```

#### Option B: Production Server (nginx + gunicorn)

```nginx
# nginx config
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

### 7. Deploy Frontend

Upload these files to your web server:
- `index.html`
- `style.css`
- `script.js`
- `success.html`
- `cancel.html`
- `privacy.html`

Update `script.js` to point to your production API:

```javascript
// Change from localhost to your domain
const API_URL = 'https://yourdomain.com/api';
```

### 8. Security Checklist

- [ ] `.env` is NOT committed to git
- [ ] HTTPS is enabled (required for Stripe)
- [ ] ADMIN_TOKEN is strong and random
- [ ] CORS is restricted to your domain
- [ ] Rate limiting is enabled
- [ ] Stripe webhook secret is configured

### 9. Monitoring

Monitor these logs:

```bash
# Server logs
tail -f /var/log/gunicorn/error.log

# Check for failed payments
sqlite3 orders.db "SELECT * FROM orders WHERE payment_status='Unpaid'"

# Check temp files
ls -lh exports/temp/
```

### 10. Cleanup Cron Job

Add to crontab to clean old temp files:

```bash
# Clean temp files older than 24 hours (daily at 3 AM)
0 3 * * * find /path/to/exports/temp -type f -mtime +1 -delete
```

## Post-Launch

### Admin Panel Access

Access at: `https://yourdomain.com/admin.html?token=YOUR_ADMIN_TOKEN`

### Stripe Dashboard

Monitor payments at: https://dashboard.stripe.com/payments

### Email Notifications

Verify emails are being sent by checking SMTP logs or testing an order.

## Troubleshooting

### Orders not appearing after payment

1. Check webhook is configured correctly
2. Verify `STRIPE_WEBHOOK_SECRET` is set
3. Check server logs for webhook errors

### Emails not sending

1. Verify SMTP credentials in `.env`
2. Check SMTP server allows connections
3. Test with: `python3 -c "from server import send_confirmation_email; send_confirmation_email('test@test.com', {'id': 1, 'name': 'Test', 'quantity': 50, 'total_price': 300, 'filename': 'test.png', 'payment_status': 'Paid'})"`

### File upload fails

1. Check `exports/` directory exists and is writable
2. Verify `MAX_CONTENT_LENGTH` is appropriate
3. Check disk space

## Support

For issues, check:
- Server logs
- Stripe dashboard
- Database: `sqlite3 orders.db`
