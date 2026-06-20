document.addEventListener("DOMContentLoaded", () => {
    // 1. Dynamic Clock and Date Display
    const clockElement = document.getElementById("clock-display");
    const dateElement = document.getElementById("current-date-display");
    
    function updateDateTime() {
        const now = new Date();
        
        // Time format: e.g. 09:40 am
        if (clockElement) {
            let hours = now.getHours();
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const ampm = hours >= 12 ? 'pm' : 'am';
            hours = hours % 12;
            hours = hours ? hours : 12; // the hour '0' should be '12'
            clockElement.textContent = `${hours}:${minutes} ${ampm}`;
        }
        
        // Date format: e.g. June 20, 2026
        if (dateElement) {
            const options = { month: 'long', day: 'numeric', year: 'numeric' };
            dateElement.textContent = now.toLocaleDateString('en-US', options);
        }
    }
    
    // Initial run and repeat every minute
    updateDateTime();
    setInterval(updateDateTime, 60000);
    
    // 2. Auto-close alert notifications after 5 seconds
    const alerts = document.querySelectorAll('.custom-alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
