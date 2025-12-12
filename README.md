# GASsstro - B2B Cookie Customization Service

Professional B2B service for creating custom-branded cookies with company logos. Features automated 3D stamp generation, Stripe payment integration, and comprehensive order management.

## 🌐 Live Site

- **Frontend:** [https://stefanonozza.github.io/timbrobro/](https://stefanonozza.github.io/timbrobro/)
- **Backend API:** Deployed on Render.com
- **Admin Panel:** `/admin.html?token=YOUR_TOKEN`

## 🏗️ Architecture

### Frontend (GitHub Pages)
- Static HTML/CSS/JavaScript
- Swiss Design aesthetic
- Real-time file upload and validation
- Stripe Checkout integration

### Backend (Render.com)
- **Framework:** Flask (Python)
- **Database:** PostgreSQL
- **Payment:** Stripe API
- **Email:** SMTP notifications
- **3D Processing:** STL file generation from logos

## ✨ Features

- 🎨 **Logo Upload & Analysis** - Automatic geometry analysis and complexity scoring
- 💳 **Secure Payments** - Stripe Checkout with webhook confirmation
- 📧 **Email Notifications** - Automatic order confirmations
- 🔧 **Admin Dashboard** - Order management, analytics, and export
- 🍪 **3D Stamp Generation** - Automated STL file creation for cookie stamps
- 🔒 **GDPR Compliant** - EU-hosted, privacy-first architecture
- 📱 **Responsive Design** - Mobile-optimized Swiss minimalism

## 🚀 Deployment

### Prerequisites
- Stripe account (live API keys)
- SMTP email credentials for `orders@gassstro.com`
- GitHub account
- Render.com account

### Quick Start

1. **Deploy Backend to Render.com**
   ```bash
   # See RENDER_SETUP.md for detailed instructions
   ```

2. **Configure Environment Variables**
   ```bash
   # Copy template and fill in values
   cp .env.production.template .env.production
   ```

3. **Deploy Frontend to GitHub Pages**
   - Push to GitHub
   - Enable Pages in repository settings
   - Set branch to `main`

4. **Configure Stripe Webhook**
   - Add endpoint: `https://your-backend.onrender.com/api/webhook`
   - Select event: `checkout.session.completed`

### Detailed Guides
- 📘 [RENDER_SETUP.md](RENDER_SETUP.md) - Complete Render.com deployment guide
- ✅ [LAUNCH_CHECKLIST.md](LAUNCH_CHECKLIST.md) - Pre-launch verification checklist
- 🔧 [DEPLOYMENT.md](DEPLOYMENT.md) - General deployment information

## 🛠️ Local Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your test credentials
nano .env

# Initialize database
python3 -c "from server import init_db; init_db()"

# Run backend
python3 server.py

# In another terminal, run frontend
python3 -m http.server 8080
```

### Access
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000
- Admin Panel: http://localhost:5000/admin.html?token=YOUR_TOKEN

## 📁 Project Structure

```
timbrobro/
├── index.html              # Main landing page
├── style.css               # Swiss Design styles
├── script.js               # Frontend logic
├── server.py               # Flask backend
├── converter.py            # STL generation
├── admin.html              # Admin dashboard
├── privacy.html            # Privacy Policy
├── terms.html              # Terms & Conditions
├── cookie-policy.html      # Cookie Policy
├── success.html            # Payment success page
├── cancel.html             # Payment cancel page
├── requirements.txt        # Python dependencies
├── gunicorn.conf.py        # Production server config
├── Procfile                # Render deployment
├── render.yaml             # Render configuration
└── images/                 # Product images
```

## 🔒 Security

- ✅ HTTPS enforced (Render & GitHub Pages)
- ✅ Environment variables for secrets
- ✅ CORS restricted to frontend domain
- ✅ Rate limiting (2000/day, 500/hour)
- ✅ Stripe webhook signature verification
- ✅ Admin panel token authentication
- ✅ Automatic file cleanup (30 days)
- ✅ Input sanitization and validation

## 💰 Pricing Tiers

- **Small (12-40 pcs):** €4.00/piece
- **Medium (41-99 pcs):** €3.70/piece
- **Corporate (100+ pcs):** €3.40/piece

Minimum order: 12 pieces

## 📧 Support

- **Orders:** orders@gassstro.com
- **Privacy:** privacy@gassstro.com
- **Hours:** Mon-Fri 9:00-18:00 CET

## 📄 License

Proprietary - All rights reserved © 2024 GASsstro System

## 🙏 Credits

- **Design:** Swiss Minimalism principles
- **Typography:** Helvetica Neue
- **Payment:** Stripe
- **Hosting:** Render.com + GitHub Pages
