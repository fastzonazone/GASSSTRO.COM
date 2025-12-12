// GASsstro B2B - Interaction Logic

document.addEventListener('DOMContentLoaded', () => {
    setupInteractions();
    setupPricing();
    setupForm();
});

function setupInteractions() {
    // Workbench & Scanning Logic
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('logo-upload');
    const scanningOverlay = document.getElementById('scanning-overlay');
    const scanPercent = document.getElementById('scan-percent');
    const fileStatusPanel = document.getElementById('file-status');
    const fileNameDisplay = document.getElementById('file-name-display');
    const complexityScore = document.getElementById('complexity-score');

    // Cookie Banner Logic
    const cookieBanner = document.getElementById('cookie-banner');
    const acceptCookiesBtn = document.getElementById('accept-cookies');

    if (cookieBanner && !localStorage.getItem('cookiesAccepted')) {
        cookieBanner.style.display = 'block';
    }

    if (acceptCookiesBtn) {
        acceptCookiesBtn.addEventListener('click', () => {
            localStorage.setItem('cookiesAccepted', 'true');
            cookieBanner.style.display = 'none';
        });
    }

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');

            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                startScanningSequence(fileInput.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                startScanningSequence(fileInput.files[0]);
            }
        });
    }

    function startScanningSequence(file) {
        // Reset UI if needed
        if (fileStatusPanel) fileStatusPanel.style.display = 'none';

        // Show Overlay
        scanningOverlay.style.display = 'flex';

        // Simulate Scan Progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.floor(Math.random() * 5) + 2; // Random increment
            if (progress > 100) progress = 100;

            scanPercent.textContent = `${progress}%`;

            if (progress >= 100) {
                clearInterval(interval);
                finalizeScan(file);
            }
        }, 50); // approx 2-3 seconds total
    }

    function finalizeScan(file) {
        setTimeout(() => {
            scanningOverlay.style.display = 'none';

            // Populate Status
            if (fileNameDisplay) fileNameDisplay.textContent = file.name;
            if (complexityScore) complexityScore.textContent = calculateFakeComplexity();

            if (fileStatusPanel) {
                fileStatusPanel.style.display = 'block';
                // Slight animation for the panel
                fileStatusPanel.style.opacity = '0';
                setTimeout(() => fileStatusPanel.style.opacity = '1', 10);
                fileStatusPanel.style.transition = 'opacity 0.5s';
            }

            // Reveal pricing section
            const pricingSection = document.getElementById('pricing-section');
            if (pricingSection) {
                pricingSection.style.display = 'block';
                // Smooth scroll to results
                setTimeout(() => {
                    pricingSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        }, 500); // Small pause at 100%
    }

    function calculateFakeComplexity() {
        const scores = ['BASSA (FAST)', 'MEDIA (STANDARD)', 'ALTA (PRECISION)'];
        return scores[Math.floor(Math.random() * scores.length)];
    }

    // Smooth Scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

function setupPricing() {
    const quantitySlider = document.getElementById('quantity-slider');
    const quantityDisplay = document.getElementById('quantity-display');
    const totalPriceDisplay = document.getElementById('total-price');
    const pricingRows = document.querySelectorAll('.pricing-row');

    // Pricing Tiers Configuration
    const TIERS = [
        { id: 'tier-small', min: 12, max: 40, price: 4.00 },
        { id: 'tier-medium', min: 41, max: 99, price: 3.70 },
        { id: 'tier-corporate', min: 100, max: 10000, price: 3.40 }
    ];

    function updatePrice() {
        let qty = parseInt(quantityDisplay.value);
        if (isNaN(qty) || qty < 12) qty = 12;

        // Find active tier
        const activeTier = TIERS.find(tier => qty >= tier.min && qty <= tier.max) || TIERS[TIERS.length - 1];

        // Calculate Total
        let total = qty * activeTier.price;

        // Update UI
        totalPriceDisplay.textContent = `€${total.toLocaleString('it-IT')}`;

        // Update Rows Visual State
        pricingRows.forEach(row => {
            row.classList.remove('active');
            if (row.id === activeTier.id) {
                row.classList.add('active');
            }
        });
    }

    if (quantitySlider && quantityDisplay) {
        quantitySlider.addEventListener('input', (e) => {
            quantityDisplay.value = e.target.value;
            updatePrice();
        });

        quantityDisplay.addEventListener('change', (e) => {
            let val = parseInt(e.target.value);
            if (val < 12) val = 12;
            if (val > 1000) val = 1000;

            quantityDisplay.value = val;
            quantitySlider.value = val;
            updatePrice();
        });

        // Initialize
        updatePrice();
    }
}

function setupForm() {
    const form = document.getElementById("order-form");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.textContent;
        const status = document.getElementById("form-status");

        // Validation: Check if file is uploaded
        const fileInput = document.getElementById('logo-upload');
        if (!fileInput || fileInput.files.length === 0) {
            status.textContent = "ERRORE: Carica prima il tuo logo";
            status.style.color = "var(--swiss-red)";
            return;
        }

        // Validation: Check if pricing section is visible (file was scanned)
        const pricingSection = document.getElementById('pricing-section');
        if (!pricingSection || pricingSection.style.display === 'none') {
            status.textContent = "ERRORE: Attendi la scansione del file";
            status.style.color = "var(--swiss-red)";
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = "INIZIALIZZAZIONE PAGAMENTO...";
        status.textContent = "";

        const formData = new FormData(event.target);

        // Add File manually if needed
        formData.append('file', fileInput.files[0]);

        const priceText = document.getElementById('total-price').textContent.replace('€', '').replace('.', '').replace(',', '.');
        formData.append('total_price', priceText);

        try {
            // 1. Create Payment Session (saves file + creates Stripe session)
            // Use 127.0.0.1 instead of localhost to avoid IPv6 resolution issues on macOS
            const paymentResp = await fetch('https://timbrobro-backend.onrender.com/api/create-payment', {
                method: 'POST',
                body: formData
            });

            if (!paymentResp.ok) {
                const errData = await paymentResp.json();
                throw new Error(errData.error || "Errore creazione pagamento");
            }

            const paymentData = await paymentResp.json();

            status.textContent = "REINDIRIZZAMENTO A CHECKOUT SICURO...";

            // 2. Redirect to Stripe Checkout URL
            if (paymentData.checkout_url) {
                window.location.href = paymentData.checkout_url;
            } else {
                throw new Error("Nessun URL di pagamento ricevuto");
            }

        } catch (error) {
            console.error(error);
            let msg = "ERRORE.";
            if (error.message) msg += " " + error.message;
            status.innerHTML = msg;
            status.style.color = "var(--swiss-red)";
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtnText;
        }
    });
}
