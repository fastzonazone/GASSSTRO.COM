# 🚀 Final Pre-Launch Checklist

Complete this checklist before going live with GASsstro.

## ✅ Phase 1: Frontend Preparation

- [x] Contact information updated (orders@gassstro.com, no phone)
- [x] Legal pages created:
  - [x] `terms.html` - Termini e Condizioni
  - [x] `cookie-policy.html` - Cookie Policy
  - [x] `privacy.html` - Privacy Policy (already exists)
- [x] Footer links updated to point to legal pages
- [x] Product images verified (`images/cookie_texture.png`, `images/logo_detail.png`)
- [ ] **API URL updated in `script.js` (line 228)** - ⚠️ MUST DO AFTER BACKEND DEPLOYMENT

## ⚠️ Phase 2: Backend Deployment (Render.com)

### Database Setup
- [ ] PostgreSQL database created on Render
- [ ] Database URL copied and saved securely
- [ ] Database region set to EU (Frankfurt) for GDPR

### Web Service Setup
- [ ] Web service created and connected to GitHub
- [ ] Build command configured: `pip install -r requirements.txt`
- [ ] Start command configured: `gunicorn --config gunicorn.conf.py server:app`
- [ ] Service region set to EU (Frankfurt)

### Environment Variables
- [ ] `DATABASE_URL` - from Render PostgreSQL
- [ ] `STRIPE_SECRET_KEY` - **LIVE key** (sk_live_...)
- [ ] `STRIPE_PUBLISHABLE_KEY` - **LIVE key** (pk_live_...)
- [ ] `STRIPE_WEBHOOK_SECRET` - from Stripe Dashboard (after webhook setup)
- [ ] `DOMAIN` - your Render URL (https://gassstro-backend.onrender.com)
- [ ] `ADMIN_TOKEN` - generated with `openssl rand -hex 32`
- [ ] `SMTP_EMAIL` - orders@gassstro.com
- [ ] `SMTP_PASSWORD` - SMTP password for orders@gassstro.com
- [ ] `SMTP_SERVER` - SMTP server address
- [ ] `SMTP_PORT` - 587 (or your provider's port)
- [ ] `ALLOWED_ORIGINS` - your GitHub Pages URL

### SMTP Email Configuration
- [ ] Email account orders@gassstro.com created
- [ ] SMTP credentials obtained
- [ ] Test email sent successfully

## 🔴 Phase 3: Stripe Configuration

### Stripe Account
- [ ] Stripe account activated
- [ ] Business information completed
- [ ] Bank account connected for payouts
- [ ] **Switched from Test Mode to Live Mode** ⚠️ CRITICAL

### API Keys
- [ ] Live Secret Key copied (sk_live_...)
- [ ] Live Publishable Key copied (pk_live_...)
- [ ] Keys added to Render environment variables

### Webhook Setup
- [ ] Webhook endpoint added: `https://your-backend.onrender.com/api/webhook`
- [ ] Event `checkout.session.completed` selected
- [ ] Webhook signing secret copied
- [ ] `STRIPE_WEBHOOK_SECRET` updated in Render
- [ ] Webhook tested and verified

## 📦 Phase 4: Frontend Deployment (GitHub Pages)

- [ ] Repository pushed to GitHub
- [ ] GitHub Pages enabled in repository settings
- [ ] Branch set to `main` / `(root)`
- [ ] Site accessible at `https://stefanonozza.github.io/timbrobro/`
- [ ] **`script.js` updated with production backend URL** ⚠️ CRITICAL
- [ ] Changes committed and pushed

## 🧪 Phase 5: End-to-End Testing

### Payment Flow Test
- [ ] Open frontend in browser
- [ ] Upload a test logo file
- [ ] Select quantity (e.g., 12 pieces)
- [ ] Fill in test business details
- [ ] Accept privacy policy
- [ ] Click "Invia Richiesta"
- [ ] Redirected to Stripe Checkout
- [ ] Complete payment with test card: `4242 4242 4242 4242`
- [ ] Redirected to success page
- [ ] Order appears in admin panel
- [ ] Confirmation email received at provided address

### Admin Panel Test
- [ ] Access admin panel: `https://your-backend.onrender.com/admin.html?token=YOUR_TOKEN`
- [ ] Order list displays correctly
- [ ] Order details are complete
- [ ] STL file was generated
- [ ] Export functionality works

### Email Notifications
- [ ] Confirmation email received
- [ ] Email contains correct order details
- [ ] Email formatting is professional
- [ ] Links in email work correctly

## 🔒 Phase 6: Security Audit

### Code Security
- [ ] `.env` file is in `.gitignore`
- [ ] No secrets committed to GitHub
- [ ] `ADMIN_TOKEN` is strong (32+ characters)
- [ ] HTTPS enabled (automatic on Render & GitHub Pages)

### Stripe Security
- [ ] Using LIVE keys (not test keys)
- [ ] Webhook signature verification enabled
- [ ] Webhook secret is secure

### CORS Configuration
- [ ] `ALLOWED_ORIGINS` set to frontend URL only
- [ ] No wildcard (`*`) in CORS settings

### Rate Limiting
- [ ] Rate limiting active (check server.py)
- [ ] Limits appropriate for production

## 📊 Phase 7: Monitoring Setup

### Render Monitoring
- [ ] Logs accessible and readable
- [ ] No errors in deployment logs
- [ ] Service health check passing

### Stripe Monitoring
- [ ] Stripe Dashboard accessible
- [ ] Webhook delivery status: Success
- [ ] Payment notifications enabled

### Uptime Monitoring (Optional)
- [ ] UptimeRobot or similar service configured
- [ ] Alerts set up for downtime

## 📝 Phase 8: Documentation

- [ ] `RENDER_SETUP.md` reviewed
- [ ] `README.md` updated with live URLs
- [ ] Admin access documented securely
- [ ] Backup procedures documented

## 🎯 Phase 9: Business Readiness

### Legal Compliance
- [ ] Privacy Policy complete and accurate
- [ ] Terms & Conditions complete
- [ ] Cookie Policy complete
- [ ] GDPR compliance verified
- [ ] Business information in legal pages updated (P.IVA, address, etc.)

### Customer Support
- [ ] orders@gassstro.com monitored
- [ ] Response time policy defined
- [ ] FAQ prepared (if applicable)

### Pricing
- [ ] Pricing tiers confirmed:
  - Small (12-40): €4.00/piece
  - Medium (41-99): €3.70/piece
  - Corporate (100+): €3.40/piece
- [ ] Shipping costs calculated
- [ ] VAT handling configured

## 🚨 Critical Pre-Launch Actions

### MUST DO BEFORE LAUNCH:
1. [ ] **Switch Stripe from Test to Live Mode**
2. [ ] **Update `script.js` with production backend URL**
3. [ ] **Configure Stripe webhook with production URL**
4. [ ] **Test complete payment flow with real card**
5. [ ] **Verify email notifications work**

### NEVER DO:
- [ ] ❌ Commit `.env` file to GitHub
- [ ] ❌ Use test Stripe keys in production
- [ ] ❌ Leave CORS as wildcard (`*`)
- [ ] ❌ Use weak admin token

## ✨ Launch Day

- [ ] All checklist items completed
- [ ] Final end-to-end test successful
- [ ] Team notified of launch
- [ ] Monitoring active
- [ ] Support email monitored

## 📞 Emergency Contacts

- **Render Support:** https://render.com/docs/support
- **Stripe Support:** https://support.stripe.com
- **GitHub Support:** https://support.github.com

## 🎉 Post-Launch

- [ ] Monitor first 24 hours closely
- [ ] Check for any errors in logs
- [ ] Verify first real order processes correctly
- [ ] Collect customer feedback
- [ ] Plan improvements based on usage

---

**Last Updated:** 2024-12-12

**Status:** 🟡 In Progress

**Next Action:** Deploy backend to Render.com
