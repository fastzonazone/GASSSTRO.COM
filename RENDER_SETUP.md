# GASsstro - Render.com Setup Guide

Complete step-by-step guide to deploy GASsstro backend to Render.com with PostgreSQL database.

## Prerequisites

- GitHub account with timbrobro repository
- Stripe account with live API keys
- SMTP email credentials for orders@gassstro.com

## Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

## Step 2: Create PostgreSQL Database

1. From Render Dashboard, click **New +** → **PostgreSQL**
2. Configure database:
   - **Name:** `gassstro-db`
   - **Database:** `gassstro`
   - **User:** `gassstro_user` (auto-generated)
   - **Region:** Frankfurt (EU) - for GDPR compliance
   - **Plan:** Free tier (or Starter for production)
3. Click **Create Database**
4. Wait for database to be provisioned (~2 minutes)
5. **Copy the Internal Database URL** (starts with `postgresql://`)
   - Format: `postgresql://user:password@host:5432/database`
   - You'll need this for environment variables

## Step 3: Create Web Service

1. From Render Dashboard, click **New +** → **Web Service**
2. Connect your GitHub repository:
   - Select **stefanonozza/timbrobro** (or your repo name)
   - Click **Connect**
3. Configure web service:
   - **Name:** `gassstro-backend`
   - **Region:** Frankfurt (EU)
   - **Branch:** `main`
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --config gunicorn.conf.py server:app`
   - **Plan:** Free tier (or Starter for production)

## Step 4: Configure Environment Variables

In the web service settings, go to **Environment** tab and add these variables:

### Required Variables

```bash
# Database (from Step 2)
DATABASE_URL=postgresql://user:password@host:5432/database

# Stripe LIVE Keys (⚠️ IMPORTANT: Use LIVE keys, not test!)
STRIPE_SECRET_KEY=sk_live_YOUR_LIVE_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET

# Domain
DOMAIN=https://gassstro-backend.onrender.com

# Admin Security (Generate strong random token)
ADMIN_TOKEN=YOUR_SECURE_RANDOM_TOKEN_HERE

# Email (SMTP for orders@gassstro.com)
SMTP_EMAIL=orders@gassstro.com
SMTP_PASSWORD=your_smtp_password
SMTP_SERVER=mail.gassstro.com
SMTP_PORT=587

# CORS (Your frontend URL)
ALLOWED_ORIGINS=https://stefanonozza.github.io,https://gassstro.com
```

### How to Generate ADMIN_TOKEN

On your local terminal:
```bash
openssl rand -hex 32
```
Copy the output and paste it as `ADMIN_TOKEN`.

### SMTP Configuration

If using Gmail for orders@gassstro.com:
- **SMTP_SERVER:** `smtp.gmail.com`
- **SMTP_PORT:** `587`
- **SMTP_PASSWORD:** Use an App Password (not your regular password)
  - Go to Google Account → Security → 2-Step Verification → App Passwords

If using custom domain email, contact your hosting provider for SMTP credentials.

## Step 5: Deploy

1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start the server
3. Wait for deployment (~5 minutes)
4. Once deployed, you'll see: **"Your service is live at https://gassstro-backend.onrender.com"**

## Step 6: Configure Stripe Webhook

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Configure webhook:
   - **Endpoint URL:** `https://gassstro-backend.onrender.com/api/webhook`
   - **Events to send:** Select `checkout.session.completed`
   - **API Version:** Use latest
4. Click **Add endpoint**
5. Click on the newly created webhook
6. Copy the **Signing secret** (starts with `whsec_`)
7. Go back to Render → Environment Variables
8. Update `STRIPE_WEBHOOK_SECRET` with the copied secret
9. Click **Save Changes** (this will redeploy the service)

## Step 7: Test Backend

Test the health endpoint:
```bash
curl https://gassstro-backend.onrender.com/health
```

Expected response:
```json
{"status": "healthy"}
```

## Step 8: Update Frontend

Now you need to update the frontend to point to your production backend.

In `script.js`, change line 228:
```javascript
// FROM:
const paymentResp = await fetch('http://127.0.0.1:5000/api/create-payment', {

// TO:
const paymentResp = await fetch('https://gassstro-backend.onrender.com/api/create-payment', {
```

## Step 9: Deploy Frontend to GitHub Pages

1. In your repository, go to **Settings** → **Pages**
2. Under **Build and deployment**:
   - **Source:** Deploy from a branch
   - **Branch:** `main` / `(root)`
3. Click **Save**
4. Wait ~2 minutes
5. Your site will be live at: `https://stefanonozza.github.io/timbrobro/`

## Step 10: Custom Domain (Optional)

If you own `gassstro.com`:

### For Backend (Render):
1. In Render web service, go to **Settings** → **Custom Domain**
2. Add: `api.gassstro.com`
3. Follow DNS instructions to add CNAME record

### For Frontend (GitHub Pages):
1. In repository **Settings** → **Pages** → **Custom domain**
2. Add: `gassstro.com`
3. Add DNS records:
   - Type: `A`, Host: `@`, Value: GitHub IPs (see GitHub docs)
   - Type: `CNAME`, Host: `www`, Value: `stefanonozza.github.io`

## Troubleshooting

### Database Connection Errors
- Verify `DATABASE_URL` is correct (Internal URL, not External)
- Check database is in the same region as web service

### Stripe Webhook Not Working
- Ensure webhook URL is correct: `https://your-domain.onrender.com/api/webhook`
- Verify `STRIPE_WEBHOOK_SECRET` matches Stripe Dashboard
- Check Render logs for webhook errors

### Email Not Sending
- Verify SMTP credentials are correct
- For Gmail, ensure "Less secure app access" is enabled OR use App Password
- Check Render logs for SMTP errors

### CORS Errors
- Add your frontend URL to `ALLOWED_ORIGINS`
- Format: `https://stefanonozza.github.io` (no trailing slash)

### 502 Bad Gateway
- Check Render logs for startup errors
- Verify all environment variables are set
- Ensure `gunicorn.conf.py` exists in repository

## Monitoring

### Render Dashboard
- **Logs:** Real-time server logs
- **Metrics:** CPU, Memory, Request count
- **Events:** Deployment history

### Stripe Dashboard
- **Payments:** Monitor successful payments
- **Webhooks:** Check webhook delivery status

### Admin Panel
Access at: `https://gassstro-backend.onrender.com/admin.html?token=YOUR_ADMIN_TOKEN`

## Free Tier Limitations

Render Free Tier:
- ✅ 750 hours/month (enough for 1 service)
- ✅ Auto-sleep after 15 min inactivity
- ⚠️ First request after sleep takes ~30 seconds (cold start)
- ✅ PostgreSQL: 1GB storage, 97 hours/month compute

**For production:** Consider upgrading to Starter plan ($7/month) for:
- No auto-sleep
- Faster performance
- More database hours

## Security Checklist

- [ ] `.env` is in `.gitignore` (never commit secrets!)
- [ ] HTTPS is enabled (automatic on Render)
- [ ] `ADMIN_TOKEN` is strong and random
- [ ] Stripe LIVE keys are used (not test keys)
- [ ] CORS is restricted to your domain only
- [ ] Database is in EU region (GDPR compliance)

## Next Steps

1. Test complete payment flow end-to-end
2. Verify email notifications work
3. Check admin panel displays orders correctly
4. Monitor logs for any errors
5. Set up uptime monitoring (e.g., UptimeRobot)

## Support

- **Render Docs:** https://render.com/docs
- **Stripe Docs:** https://stripe.com/docs
- **GASsstro Issues:** Contact orders@gassstro.com
