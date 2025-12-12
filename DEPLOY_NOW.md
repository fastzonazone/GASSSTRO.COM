# 🚀 Render.com Deployment - Step by Step

## ✅ What You Have Ready

- ✅ Stripe Live Keys configured
- ✅ Admin Token generated: `71212734b925e9eef4835108c6b5c16368a1b0aec944c666307c566406be2cf8`

## ⚠️ What You Still Need

1. **SMTP Email Configuration** for orders@gassstro.com
   - Need: SMTP password
   - Server: smtp.gmail.com (or your provider)

2. **Render.com Account**
   - Sign up at: https://render.com

---

## 📝 Step 1: Configure Email (5 min)

### Option A: Gmail
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Go to App Passwords
4. Generate password for "Mail"
5. Copy the 16-character password

### Option B: Custom Email Provider
Contact your email provider for SMTP credentials.

---

## 🗄️ Step 2: Create PostgreSQL Database on Render

1. Go to https://render.com/dashboard
2. Click **New +** → **PostgreSQL**
3. Settings:
   - **Name:** `gassstro-db`
   - **Database:** `gassstro`
   - **Region:** **Frankfurt (EU)** ← IMPORTANT for GDPR
   - **Plan:** Free (or Starter $7/mo for production)
4. Click **Create Database**
5. Wait ~2 minutes for provisioning
6. **COPY THE INTERNAL DATABASE URL** (you'll need this in Step 3)
   - Format: `postgresql://user:password@host/database`
   - Find it under "Connections" → "Internal Database URL"

---

## 🌐 Step 3: Create Web Service on Render

1. Click **New +** → **Web Service**
2. Connect GitHub:
   - Click **Connect account** (if first time)
   - Select repository: `timbrobro`
   - Click **Connect**
3. Configure service:
   - **Name:** `gassstro-backend`
   - **Region:** **Frankfurt (EU)** ← Same as database
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --config gunicorn.conf.py server:app`
   - **Plan:** Free (or Starter $7/mo)

4. **Environment Variables** - Click "Advanced" → Add these:

```bash
DATABASE_URL=<PASTE INTERNAL URL FROM STEP 2>
STRIPE_SECRET_KEY=mk_1SdBzGCh7KWb2lYNdYBAUcpu
STRIPE_PUBLISHABLE_KEY=mk_1R6LnSCh7KWb2lYNvO5xLz8D
STRIPE_WEBHOOK_SECRET=whsec_TEMP_PLACEHOLDER
DOMAIN=https://gassstro-backend.onrender.com
ADMIN_TOKEN=71212734b925e9eef4835108c6b5c16368a1b0aec944c666307c566406be2cf8
SMTP_EMAIL=orders@gassstro.com
SMTP_PASSWORD=<YOUR SMTP PASSWORD FROM STEP 1>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
ALLOWED_ORIGINS=https://stefanonozza.github.io
```

5. Click **Create Web Service**
6. Wait ~5 minutes for deployment
7. **COPY YOUR BACKEND URL** (e.g., `https://gassstro-backend.onrender.com`)

---

## 🔗 Step 4: Configure Stripe Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Make sure you're in **LIVE MODE** (toggle in top right)
3. Click **Add endpoint**
4. Settings:
   - **Endpoint URL:** `https://gassstro-backend.onrender.com/api/webhook`
     (use YOUR URL from Step 3)
   - **Events to send:** Select `checkout.session.completed`
5. Click **Add endpoint**
6. Click on the webhook you just created
7. **COPY THE SIGNING SECRET** (starts with `whsec_...`)
8. Go back to Render → Your web service → **Environment**
9. Find `STRIPE_WEBHOOK_SECRET` and update it with the signing secret
10. Click **Save Changes** (this will trigger a redeploy)

---

## 🎨 Step 5: Update Frontend

1. Open `script.js` in your editor
2. Find line 228:
   ```javascript
   const paymentResp = await fetch('http://127.0.0.1:5000/api/create-payment', {
   ```
3. Replace with:
   ```javascript
   const paymentResp = await fetch('https://gassstro-backend.onrender.com/api/create-payment', {
   ```
   (use YOUR backend URL from Step 3)
4. Save the file

---

## 📤 Step 6: Deploy to GitHub Pages

1. Commit changes:
   ```bash
   git add script.js
   git commit -m "Update API URL for production"
   git push origin main
   ```

2. Go to GitHub repository → **Settings** → **Pages**
3. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main** / **(root)**
4. Click **Save**
5. Wait ~2 minutes
6. Your site will be live at: `https://stefanonozza.github.io/timbrobro/`

---

## ✅ Step 7: Test Everything

1. Open: `https://stefanonozza.github.io/timbrobro/`
2. Upload a test logo
3. Select quantity (12)
4. Fill in business details
5. Click "Invia Richiesta"
6. Complete payment with test card: `4242 4242 4242 4242`
7. Verify:
   - [ ] Redirected to success page
   - [ ] Email received at orders@gassstro.com
   - [ ] Order appears in admin panel: `https://gassstro-backend.onrender.com/admin.html?token=71212734b925e9eef4835108c6b5c16368a1b0aec944c666307c566406be2cf8`

---

## 🎉 You're Live!

### Important URLs

- **Frontend:** https://stefanonozza.github.io/timbrobro/
- **Backend:** https://gassstro-backend.onrender.com
- **Admin Panel:** https://gassstro-backend.onrender.com/admin.html?token=71212734b925e9eef4835108c6b5c16368a1b0aec944c666307c566406be2cf8
- **Stripe Dashboard:** https://dashboard.stripe.com

### Security Reminders

- ⚠️ **NEVER share your admin token publicly**
- ⚠️ **NEVER commit `.env.render` to Git** (it's protected by .gitignore)
- ✅ Your Stripe keys are LIVE - real payments will be processed
- ✅ Keep your SMTP password secure

---

## 🆘 Need Help?

If you get stuck, check:
- Render logs: Dashboard → Your service → Logs
- Stripe webhook status: Dashboard → Webhooks
- Email me: orders@gassstro.com

**Estimated Time:** 20-30 minutes total
