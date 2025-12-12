# 🚀 Quick Start Guide

## Per Testare Localmente (ADESSO)

### 1. Il server è già in esecuzione!
Hai già `python3 server.py` attivo sulla porta 5000.

### 2. Apri il nuovo Admin Panel
```bash
open http://127.0.0.1:5000/admin.html
```

### 3. Login
- **Password**: Usa il valore di `ADMIN_TOKEN` dal tuo file `.env`
- Se non lo ricordi, controlla con: `cat .env | grep ADMIN_TOKEN`

### 4. Esplora le nuove features
- ✅ Dashboard con statistiche e grafici
- ✅ Filtri per stato e pagamento
- ✅ Ricerca per nome/email
- ✅ Export CSV
- ✅ Note interne per ordini
- ✅ Notifiche real-time

---

## Per Deployare su Render.com

### Opzione A: Deploy Automatico con render.yaml

1. **Push su GitHub**
   ```bash
   cd /Users/stefanonozza/Documents/timbrobro
   
   # Se non hai ancora inizializzato git:
   git init
   git add .
   git commit -m "Backend ready for Render"
   git branch -M main
   
   # Aggiungi il tuo repository GitHub
   git remote add origin https://github.com/YOUR_USERNAME/timbrobro.git
   git push -u origin main
   ```

2. **Deploy su Render**
   - Vai su https://dashboard.render.com
   - Click **"New +" → "Blueprint"**
   - Connetti il tuo repository GitHub
   - Render rileverà automaticamente `render.yaml`
   - Click **"Apply"**
   - ✅ Done! Il database PostgreSQL e il web service saranno creati automaticamente

3. **Configura Variabili Ambiente**
   
   Nel dashboard Render → Your Service → Environment, aggiungi:
   
   ```bash
   ADMIN_TOKEN=<genera-token-sicuro>
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   SMTP_EMAIL=orders@gassstro.com
   SMTP_PASSWORD=<your-smtp-password>
   ALLOWED_ORIGINS=https://stefanonozza.github.io
   DOMAIN=https://stefanonozza.github.io/timbrobro
   ```
   
   **Genera ADMIN_TOKEN sicuro**:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Configura Stripe Webhooks**
   - Vai su https://dashboard.stripe.com/webhooks
   - Click "Add endpoint"
   - URL: `https://your-app.onrender.com/api/webhook`
   - Events: `checkout.session.completed`
   - Copia il signing secret e aggiungilo come `STRIPE_WEBHOOK_SECRET`

5. **Aggiorna Frontend**
   
   In `script.js` e `admin.html`, cambia:
   ```javascript
   const API_URL = 'https://your-app.onrender.com/api';
   ```

6. **Deploy Frontend su GitHub Pages**
   - Repository Settings → Pages
   - Source: main branch
   - ✅ Il tuo sito sarà su `https://stefanonozza.github.io/timbrobro`

---

## Verifica che Tutto Funzioni

### Test Backend
```bash
# Health check
curl https://your-app.onrender.com/api/health

# Dovrebbe ritornare:
# {"status":"ok","db":"PostgreSQL"}
```

### Test Admin
1. Apri `https://your-app.onrender.com/admin.html`
2. Login con il tuo `ADMIN_TOKEN`
3. Verifica che vedi gli ordini esistenti

### Test Ordine Completo
1. Vai sul tuo sito GitHub Pages
2. Carica un logo
3. Completa il checkout con carta test Stripe: `4242 4242 4242 4242`
4. Verifica che l'ordine appaia nell'admin
5. Controlla che ricevi l'email di conferma

---

## Troubleshooting

### "Database connection failed"
- Verifica che `DATABASE_URL` sia impostato correttamente
- Controlla che il database PostgreSQL sia stato creato su Render

### "Stripe webhook failing"
- Verifica che `STRIPE_WEBHOOK_SECRET` sia corretto
- Controlla che l'URL del webhook sia `https://your-app.onrender.com/api/webhook`
- Testa il webhook da Stripe Dashboard

### "File uploads not working"
Il tier gratuito di Render ha filesystem effimero. I file caricati vengono eliminati al riavvio del server.

**Soluzioni**:
1. Upgrade a Render Starter plan ($7/mese) con persistent disk
2. Usa AWS S3 per storage file (richiede modifiche al codice)
3. Accetta che i file vengano eliminati periodicamente (ok per testing)

### "Admin panel non si connette"
- Verifica che `ALLOWED_ORIGINS` includa il tuo dominio GitHub Pages
- Controlla la console browser per errori CORS
- Verifica che l'URL API sia corretto in `admin.html`

---

## Costi Previsti

### Render.com Free Tier
- ✅ **Web Service**: Gratis (con sleep dopo 15 min inattività)
- ✅ **PostgreSQL**: Gratis (1GB storage)
- ✅ **Bandwidth**: 100GB/mese gratis
- ⚠️ **Limitazioni**: 
  - Server si addormenta dopo 15 min
  - Primo caricamento lento (~30 sec)
  - Filesystem effimero

### Render.com Starter ($7/mese)
- ✅ Sempre attivo (no sleep)
- ✅ Risposta veloce
- ✅ Persistent disk disponibile
- 💰 **Costo**: $7/mese

### Raccomandazione
- **Inizia con Free tier** per testare
- **Upgrade a Starter** quando hai clienti reali

---

## Prossimi Step Consigliati

1. ✅ Testa tutto in locale
2. ✅ Deploy su Render (free tier)
3. ✅ Testa flow completo
4. ✅ Configura dominio custom (opzionale)
5. ✅ Upgrade a Starter quando necessario

---

## Supporto

- **Render Docs**: https://render.com/docs
- **Stripe Docs**: https://stripe.com/docs
- **Render Community**: https://community.render.com

---

## 🎉 Sei pronto!

Tutto il codice è preparato. Ora devi solo:
1. Testare in locale (già funzionante!)
2. Fare push su GitHub
3. Deployare su Render
4. Configurare le variabili ambiente
5. Testare il flow completo

Buon deployment! 🚀
