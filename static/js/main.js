// ═══════════════════════════════════════
// KORNIALLE — MAIN JS
// ═══════════════════════════════════════

// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transition = 'opacity 0.5s';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });

    // Set minimum check-in date to today
    const checkinInput = document.querySelector('input[name="check_in"]');
    const checkoutInput = document.querySelector('input[name="check_out"]');
    if (checkinInput) {
        const today = new Date().toISOString().split('T')[0];
        checkinInput.min = today;
        checkinInput.addEventListener('change', () => {
            if (checkoutInput) {
                checkoutInput.min = checkinInput.value;
            }
        });
    }
});
