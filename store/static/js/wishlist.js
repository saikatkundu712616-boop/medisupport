function addToWishlist(medicineId) {
    fetch(`/wishlist/add/${medicineId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Added to wishlist ❤️');
            // Update button icon
            const btn = document.querySelector(`button[onclick="addToWishlist(${medicineId})"] i`);
            if (btn) {
                btn.classList.remove('far');
                btn.classList.add('fas');
                btn.style.color = '#ef4444';
            }
        } else {
            showToast(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error adding to wishlist');
    });
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

    // Toggle Wishlist
    function toggleWishlist(medicineId) {
        const btn = event.currentTarget;
        const icon = btn.querySelector('i');
        
        if (icon.classList.contains('far')) {
            icon.classList.remove('far');
            icon.classList.add('fas');
            icon.style.color = '#ef4444';
            btn.style.background = '#fee2e2';
            btn.style.borderColor = '#ef4444';
            showToast('Added to wishlist ❤️');
        } else {
            icon.classList.remove('fas');
            icon.classList.add('far');
            icon.style.color = '#94a3b8';
            btn.style.background = 'white';
            btn.style.borderColor = '#e5e7eb';
            showToast('Removed from wishlist');
        }
    }
    
    // Sort Function
    document.getElementById('sortSelect')?.addEventListener('change', function() {
        const url = new URL(window.location.href);
        url.searchParams.set('sort', this.value);
        window.location.href = url.toString();
    });
    
    // View Toggle
    function setView(view) {
        const grid = document.getElementById('medicineGrid');
        const buttons = document.querySelectorAll('.view-options button');
        
        buttons.forEach(btn => btn.classList.remove('active'));
        
        if (view === 'list') {
            grid.style.gridTemplateColumns = '1fr';
            document.querySelector('.view-options button:last-child').classList.add('active');
        } else {
            grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))';
            document.querySelector('.view-options button:first-child').classList.add('active');
        }
    }
    
    // Toast Notification
    function showToast(message) {
        // Create toast if not exists
        let toast = document.getElementById('toastNotification');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toastNotification';
            toast.style.cssText = `
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: #0f172a;
                color: white;
                padding: 14px 24px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                font-weight: 600;
                z-index: 9999;
                transform: translateY(100px);
                opacity: 0;
                transition: all 0.4s ease;
                font-size: 14px;
            `;
            document.body.appendChild(toast);
        }
        
        toast.textContent = message;
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
        
        setTimeout(() => {
            toast.style.transform = 'translateY(100px)';
            toast.style.opacity = '0';
        }, 3000);
    }
    
    // Load More Function
    function loadMore() {
        const btn = event.currentTarget;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        btn.disabled = true;
        
        // Simulate loading
        setTimeout(() => {
            btn.innerHTML = '<i class="fas fa-check-circle"></i> Loaded!';
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-chevron-down"></i> Load More';
                btn.disabled = false;
            }, 2000);
        }, 1500);
    }