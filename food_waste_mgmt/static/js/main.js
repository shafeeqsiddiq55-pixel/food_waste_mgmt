// ============================================================
// main.js - FoodBridge Frontend JavaScript
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

  // ============================================================
  // AUTO-DISMISS ALERTS after 5 seconds
  // ============================================================
  document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ============================================================
  // CONFIRM DELETE forms
  // ============================================================
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', function (e) {
      if (!confirm(this.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // ============================================================
  // PASSWORD STRENGTH INDICATOR
  // ============================================================
  const pwInput = document.querySelector('input[name="password"]');
  if (pwInput) {
    let bar = document.createElement('div');
    bar.className = 'pw-strength-bar mt-1';
    bar.innerHTML = `<div class="pw-bar-inner" id="pwBar" style="height:3px;border-radius:2px;width:0;transition:width .3s,background .3s"></div>`;
    bar.style.background = '#eee';
    bar.style.borderRadius = '2px';
    bar.style.marginTop = '6px';
    pwInput.parentNode.appendChild(bar);

    pwInput.addEventListener('input', function () {
      const val = this.value;
      let score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val)) score++;
      if (/[0-9]/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;
      const colors = ['#e74c3c', '#e67e22', '#f1c40f', '#27ae60'];
      const widths = ['25%', '50%', '75%', '100%'];
      const pwBar = document.getElementById('pwBar');
      if (pwBar && score > 0) {
        pwBar.style.width = widths[score - 1];
        pwBar.style.background = colors[score - 1];
      } else if (pwBar) {
        pwBar.style.width = '0';
      }
    });
  }

  // ============================================================
  // PASSWORD CONFIRM MATCH
  // ============================================================
  const confirmPw = document.querySelector('input[name="confirm_password"]');
  const origPw = document.querySelector('input[name="password"]');
  if (confirmPw && origPw) {
    confirmPw.addEventListener('input', function () {
      if (this.value && this.value !== origPw.value) {
        this.style.borderColor = '#e74c3c';
      } else {
        this.style.borderColor = '';
      }
    });
  }

  // ============================================================
  // FOOD SAFETY TIMER — warn if expiry is too soon
  // ============================================================
  const expiryInput = document.querySelector('input[name="expiry_time"]');
  if (expiryInput) {
    expiryInput.addEventListener('change', function () {
      const selected = new Date(this.value);
      const now = new Date();
      const diffHours = (selected - now) / (1000 * 60 * 60);
      let warning = document.getElementById('expiryWarning');
      if (!warning) {
        warning = document.createElement('small');
        warning.id = 'expiryWarning';
        this.parentNode.appendChild(warning);
      }
      if (diffHours < 2) {
        warning.textContent = '⚠️ Warning: Less than 2 hours until expiry. NGOs may not be able to collect in time.';
        warning.style.color = '#e74c3c';
        warning.style.fontWeight = '600';
      } else if (diffHours < 4) {
        warning.textContent = '⚡ Tip: Food expires soon. Post this quickly so NGOs can act fast.';
        warning.style.color = '#e67e22';
        warning.style.fontWeight = '500';
      } else {
        warning.textContent = '✅ Good pickup window.';
        warning.style.color = '#27ae60';
        warning.style.fontWeight = '500';
      }
    });
  }

  // ============================================================
  // LIVE SEARCH on admin user/donation tables
  // ============================================================
  const searchInput = document.getElementById('liveSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const query = this.value.toLowerCase();
      document.querySelectorAll('tbody tr').forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
      });
    });
  }

  // ============================================================
  // QUANTITY SLIDER → Label sync
  // ============================================================
  const qtySlider = document.getElementById('qtySlider');
  const qtyLabel = document.getElementById('qtyLabel');
  if (qtySlider && qtyLabel) {
    qtySlider.addEventListener('input', function () {
      qtyLabel.textContent = this.value + ' people';
    });
  }

  // ============================================================
  // DONATION STATUS COUNTDOWN TIMERS
  // ============================================================
  document.querySelectorAll('[data-expiry]').forEach(el => {
    const expiry = new Date(el.dataset.expiry);
    function update() {
      const now = new Date();
      const diff = expiry - now;
      if (diff <= 0) {
        el.textContent = 'Expired';
        el.style.color = '#e74c3c';
        return;
      }
      const h = Math.floor(diff / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      el.textContent = `${h}h ${m}m left`;
      if (diff < 2 * 3600000) el.style.color = '#e74c3c';
      else if (diff < 4 * 3600000) el.style.color = '#e67e22';
    }
    update();
    setInterval(update, 60000);
  });

  // ============================================================
  // IMAGE PREVIEW before upload
  // ============================================================
  const fileInput = document.querySelector('input[type="file"][name="food_image"]');
  if (fileInput) {
    fileInput.addEventListener('change', function () {
      let preview = document.getElementById('imagePreview');
      if (!preview) {
        preview = document.createElement('img');
        preview.id = 'imagePreview';
        preview.style.cssText = 'max-height:120px;border-radius:10px;margin-top:8px;border:2px solid #e8f5e9;';
        this.parentNode.appendChild(preview);
      }
      if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
        reader.readAsDataURL(this.files[0]);
      }
    });
  }

  // ============================================================
  // TOOLTIP INIT
  // ============================================================
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

});


// ============================================================
// Notification helpers (used by base.html inline scripts)
// ============================================================
function readNotif(id, el) {
  fetch(`/api/notifications/read/${id}`, { method: 'POST' })
    .then(() => {
      if (el) {
        el.classList.remove('unread');
        if (el.classList.contains('alert')) el.remove();
      }
      loadNotifications();
    });
}

// ============================================================
// Copy to clipboard helper
// ============================================================
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied!', 'success');
  });
}

// ============================================================
// Toast Notification (lightweight)
// ============================================================
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast-msg toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px;
    background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
    color: white; padding: 12px 20px; border-radius: 10px;
    font-size: 14px; font-weight: 600;
    box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    z-index: 9999; animation: slideUp .3s ease;
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
