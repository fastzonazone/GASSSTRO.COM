# 🚀 Deployment Render.com - Guida Passo-Passo

## ✅ Cosa Hai Già Fatto
- ✅ Repository GitHub pubblico (gassstro.com)
- ✅ Account Render.com creato
- ✅ Chiavi Stripe Live configurate

---

## 📋 PASSO 1: Crea Database PostgreSQL (5 min)

1. Vai su: **https://dashboard.render.com**
2. Clicca **"New +"** (in alto a destra)
3. Seleziona **"PostgreSQL"**
4. Compila il form:
   ```
   Name: gassstro-db
   Database: gassstro
   User: (lascia auto-generato)
   Region: Frankfurt (EU)  ← IMPORTANTE per GDPR!
   PostgreSQL Version: 16 (o latest)
   Datadog API Key: (lascia vuoto)
   Instance Type: Free
   ```
5. Clicca **"Create Database"**
6. Aspetta ~2 minuti (vedrai "Creating...")
7. Quando è pronto, vai alla sezione **"Connections"**
8. **COPIA "Internal Database URL"** (inizia con `postgresql://`)
   - Esempio: `postgresql://gassstro_user:abc123@dpg-xxx.frankfurt-postgres.render.com/gassstro`
   - **IMPORTANTE:** Usa "Internal" NON "External"!

📝 **Incolla qui l'URL che hai copiato** (lo useremo nel prossimo passo)

---

## 📋 PASSO 2: Crea Web Service (10 min)

1. Torna alla Dashboard: **https://dashboard.render.com**
2. Clicca **"New +"** → **"Web Service"**
3. Clicca **"Build and deploy from a Git repository"** → **"Next"**
4. Se è la prima volta:
   - Clicca **"Connect GitHub"**
   - Autorizza Render ad accedere ai tuoi repository
5. Trova il repository **"gassstro.com"** (o come l'hai chiamato)
6. Clicca **"Connect"** accanto al repository

7. Compila il form:
   ```
   Name: gassstro-backend
   Region: Frankfurt (EU)  ← STESSO del database!
   Branch: main
   Root Directory: (lascia vuoto)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --config gunicorn.conf.py server:app
   Instance Type: Free
   ```

8. **NON cliccare ancora "Create Web Service"!**

---

## 📋 PASSO 3: Aggiungi Variabili d'Ambiente

Prima di creare il servizio, scorri in basso e clicca **"Advanced"**.

Nella sezione **"Environment Variables"**, clicca **"Add Environment Variable"** per ognuna di queste:

### Variabile 1: DATABASE_URL
```
Key: DATABASE_URL
Value: <INCOLLA L'URL DEL DATABASE CHE HAI COPIATO AL PASSO 1>
```

### Variabile 2: STRIPE_SECRET_KEY
```
Key: STRIPE_SECRET_KEY
Value: mk_1SdBzGCh7KWb2lYNdYBAUcpu
```

### Variabile 3: STRIPE_PUBLISHABLE_KEY
```
Key: STRIPE_PUBLISHABLE_KEY
Value: mk_1R6LnSCh7KWb2lYNvO5xLz8D
```

### Variabile 4: STRIPE_WEBHOOK_SECRET
```
Key: STRIPE_WEBHOOK_SECRET
Value: whsec_TEMP_PLACEHOLDER
```
(Aggiorneremo questa dopo aver creato il webhook)

### Variabile 5: DOMAIN
```
Key: DOMAIN
Value: https://gassstro-backend.onrender.com
```

### Variabile 6: ADMIN_TOKEN
```
Key: ADMIN_TOKEN
Value: 71212734b925e9eef4835108c6b5c16368a1b0aec944c666307c566406be2cf8
```

### Variabile 7: SMTP_EMAIL
```
Key: SMTP_EMAIL
Value: orders@gassstro.com
```

### Variabile 8: SMTP_PASSWORD
```
Key: SMTP_PASSWORD
Value: <LA TUA PASSWORD EMAIL ARUBA per orders@gassstro.com>
```

### Variabile 9: SMTP_SERVER
```
Key: SMTP_SERVER
Value: smtps.aruba.it
```
(Server SMTP Aruba per domini personalizzati)

### Variabile 10: SMTP_PORT
```
Key: SMTP_PORT
Value: 465
```
(Porta SSL/TLS per Aruba)

### Variabile 11: ALLOWED_ORIGINS
```
Key: ALLOWED_ORIGINS
Value: https://stefanonozza.github.io
```

---

## 📋 PASSO 4: Crea il Servizio

1. Dopo aver aggiunto TUTTE le variabili, clicca **"Create Web Service"**
2. Render inizierà il deployment (vedrai i logs in tempo reale)
3. Aspetta ~5-7 minuti
4. Quando vedi **"Your service is live at https://gassstro-backend.onrender.com"** → ✅ FATTO!

📝 **Copia l'URL del tuo backend** (lo useremo per il webhook Stripe)

---

## ❓ Dove Sei Adesso?

Dimmi:
1. **Hai già configurato l'email SMTP?** (Gmail con App Password o altro provider?)
2. **Sei pronto per iniziare dal PASSO 1?**

Ti guido passo-passo! 🚀
