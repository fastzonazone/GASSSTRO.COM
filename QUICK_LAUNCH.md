# 🚀 GASsstro - Quick Start to Launch

**Everything is ready!** Follow these steps to go live.

## ⏱️ Time Estimate: ~30 minutes

---

## Step 1: Get Stripe Live Keys (5 min)

1. Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Click **"Activate your account"** (if not already activated)
3. Complete business information
4. Switch from **Test mode** to **Live mode** (toggle in top right)
5. Go to **Developers** → **API keys**
6. Copy these two keys:
   - **Secret key** (starts with `sk_live_...`)
   - **Publishable key** (starts with `pk_live_...`)
7. Save them somewhere secure (you'll need them in Step 3)

---

## Step 2: Set Up Email (5 min)

You need SMTP credentials for `orders@gassstro.com`.

### Option A: Using Gmail

1. Create/use Gmail account for orders@gassstro.com
2. Enable 2-Step Verification
3. Go to **Security** → **App Passwords**
4. Generate an App Password
5. Save the password (you'll need it in Step 3)

**SMTP Settings:**
- Server: `smtp.gmail.com`
- Port: `587`
- Email: `orders@gassstro.com`
- Password: `<your app password>`

### Option B: Custom Domain Email

Contact your domain/hosting provider for SMTP credentials.

---

## Step 3: Deploy Backend to Render.com (10 min)

1. Go to [https://render.com](https://render.com)
2. Sign up with GitHub
3. Click **New +** → **PostgreSQL**
   - Name: `gassstro-db`
   - Region: **Frankfurt (EU)**
   - Plan: Free (or Starter for production)
   - Click **Create Database**
   - **Copy the Internal Database URL** (you'll need this)

4. Click **New +** → **Web Service**
   - Connect your GitHub repository
   - Name: `gassstro-backend`
   - Region: **Frankfurt (EU)**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --config gunicorn.conf.py server:app`
   - Plan: Free (or Starter)

5. Add **Environment Variables** (click **Advanced** → **Add Environment Variable**):

```bash
DATABASE_URL=<paste the Internal Database URL from step 3>
STRIPE_SECRET_KEY=<your sk_live_... from Step 1>
STRIPE_PUBLISHABLE_KEY=<your pk_live_... from Step 1>
STRIPE_WEBHOOK_SECRET=whsec_temp_placeholder
DOMAIN=https://gassstro-backend.onrender.com
ADMIN_TOKEN=<generate with: openssl rand -hex 32>
SMTP_EMAIL=orders@gassstro.com
SMTP_PASSWORD=<your SMTP password from Step 2>
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
ALLOWED_ORIGINS=https://stefanonozza.github.io
```

6. Click **Create Web Service**
7. Wait ~5 minutes for deployment
8. **Copy your backend URL** (e.g., `https://gassstro-backend.onrender.com`)

---

## Step 4: Configure Stripe Webhook (3 min)

1. Go to [https://dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Endpoint URL: `https://gassstro-backend.onrender.com/api/webhook`
   (use YOUR backend URL from Step 3)
4. Events to send: Select **`checkout.session.completed`**
5. Click **Add endpoint**
6. Click on the webhook you just created
7. Copy the **Signing secret** (starts with `whsec_...`)
8. Go back to Render → Your web service → **Environment**
9. Update `STRIPE_WEBHOOK_SECRET` with the signing secret
10. Click **Save Changes** (this will redeploy)

---

## Step 5: Update Frontend (2 min)

1. Open `script.js` in your code editor
2. Find line 228:
   ```javascript
   const paymentResp = await fetch('http://127.0.0.1:5000/api/create-payment', {
   ```
3. Change to:
   ```javascript
   const paymentResp = await fetch('https://gassstro-backend.onrender.com/api/create-payment', {
   ```
   (use YOUR backend URL from Step 3)
4. Save the file

---

## Step 6: Deploy Frontend to GitHub Pages (3 min)

1. Commit and push your changes:
   ```bash
   git add .
   git commit -m "Ready for production launch"
   git push origin main
   ```

2. Go to your GitHub repository
3. Click **Settings** → **Pages**
4. Under **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **main** / **(root)**
5. Click **Save**
6. Wait ~2 minutes
7. Your site will be live at: `https://stefanonozza.github.io/timbrobro/`

---

## Step 7: Test Everything! (5 min)

1. Open your live site: `https://stefanonozza.github.io/timbrobro/`
2. Upload a test logo
3. Select quantity (e.g., 12)
4. Fill in business details
5. Click **"Invia Richiesta"**
6. You'll be redirected to Stripe Checkout
7. Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
8. Complete payment
9. Check if you received confirmation email
10. Access admin panel: `https://gassstro-backend.onrender.com/admin.html?token=YOUR_ADMIN_TOKEN`
11. Verify order appears in admin panel

---

## ✅ You're Live!

If all tests passed, your site is **production-ready**!

### What to Monitor

- **Stripe Dashboard:** [https://dashboard.stripe.com/payments](https://dashboard.stripe.com/payments)
- **Render Logs:** Render Dashboard → Your service → Logs
- **Email:** Check orders@gassstro.com for notifications

### Important URLs

- **Frontend:** https://stefanonozza.github.io/timbrobro/
- **Backend:** https://gassstro-backend.onrender.com
- **Admin Panel:** https://gassstro-backend.onrender.com/admin.html?token=YOUR_TOKEN
- **Stripe Dashboard:** https://dashboard.stripe.com

---

## 🆘 Troubleshooting

### Orders not appearing after payment
→ Check Stripe webhook is configured correctly  
→ Verify `STRIPE_WEBHOOK_SECRET` in Render matches Stripe Dashboard

### Emails not sending
→ Verify SMTP credentials in Render environment variables  
→ For Gmail, ensure App Password is used (not regular password)

### 502 Bad Gateway
→ Check Render logs for errors  
→ Verify all environment variables are set

### CORS errors
→ Ensure `ALLOWED_ORIGINS` includes your GitHub Pages URL  
→ No trailing slash in URL

---

## 📚 Need More Help?

- **Detailed Guide:** See `RENDER_SETUP.md`
- **Full Checklist:** See `LAUNCH_CHECKLIST.md`
- **Support:** orders@gassstro.com

---

## 🎉 Congratulations!

You've successfully launched GASsstro! 🚀🍪

**Next Steps:**
- Share your site with potential customers
- Monitor first orders closely
- Collect feedback and iterate

---

**Last Updated:** 2024-12-12  
**Estimated Total Time:** 30 minutes  
**Difficulty:** ⭐⭐ (Intermediate)
