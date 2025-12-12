# GASsstro - B2B Cookie Service

Sito web B2B per la generazione e l'ordine di biscotti personalizzati con logo aziendale.

## 🚀 Come andare Online (Deployment)

Il metodo più veloce e gratuito per pubblicare questo sito è usare **GitHub Pages**.

### Passo 1: GitHub
1. Crea un account su [GitHub.com](https://github.com).
2. Crea un **New Repository** (chiamalo ad esempio `gasstro-web`).
3. Seleziona "Public".

### Passo 2: Caricare i File
Tornando al tuo computer nella cartella del progetto:
1. Inizializza Git (se non l'hai fatto):
   ```bash
   git init
   git add .
   git commit -m "Primo commit"
   ```
2. Collega la repo (ti darà il comando GitHub, simile a questo):
   ```bash
   git remote add origin https://github.com/IL_TUO_USER/gasstro-web.git
   git push -u origin main
   ```
   *(Alternativa semplice: Carica i file trascinandoli nell'interfaccia web di GitHub)*

### Passo 3: Attivare il Sito
1. Vai su **Settings** del repository GitHub.
2. Clicca su **Pages** (nel menu a sinistra).
3. Sotto **Build and deployment > Branch**, seleziona `main` e salva.
4. Dopo 1 minuto, GitHub ti darà il link del tuo sito (es. `https://iltuouser.github.io/gasstro-web/`).

---

## 📧 Configurazione Email (Formspree)

Il modulo d'ordine usa Formspree per mandare le email senza bisogno di un server.

1. Vai su [Formspree.io](https://formspree.io) e registrati.
2. Crea un **New Form**.
3. Copia l'URL del form (es. `https://formspree.io/f/xyzyqwer`).
4. Apri `index.html` e sostituisci l'URL alla riga ~176:
   ```html
   <form id="order-form" action="INCOLLA_QUI_IL_TUO_URL" method="POST">
   ```
5. Fai un commit e pusha la modifica.

**Fatto!** Ora riceverai gli ordini via mail.

---

## 🍪 Tecnologie
- **Three.js**: Rendering 3D biscotto.
- **Canvas API**: Generazione texture procedurale.
- **Vanilla JS**: Logica frontend leggera.
