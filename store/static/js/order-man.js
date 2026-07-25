 document.getElementById('bulkAction').addEventListener('change', function() {
        const statusWrapper = document.getElementById('statusSelectWrapper');
        if (this.value === 'update_status') {
            statusWrapper.style.display = 'block';
        } else {
            statusWrapper.style.display = 'none';
        }
    });

    function executeBulkAction() {
        const action = document.getElementById('bulkAction').value;
        if (!action) {
            alert('Please select an action.');
            return;
        }
        
        const selectedOrders = document.querySelectorAll('.order-checkbox:checked');
        if (selectedOrders.length === 0) {
            alert('Please select at least one order.');
            return;
        }
        
        if (!confirm(`Are you sure you want to ${action} ${selectedOrders.length} orders?`)) {
            return;
        }
        
        const orderIds = Array.from(selectedOrders).map(cb => cb.value);
        const data = {
            action: action,
            order_ids: orderIds,
            csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value
        };
        
        if (action === 'update_status') {
            const status = document.getElementById('bulkStatus').value;
            if (!status) {
                alert('Please select a status.');
                return;
            }
            data.status = status;
        }
        
        fetch('/admin/orders/bulk-action/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error: ' + error);
        });
    }

    function selectAllOrders() {
        document.querySelectorAll('.order-checkbox').forEach(cb => cb.checked = true);
        document.getElementById('selectAll').checked = true;
    }

    function deselectAllOrders() {
        document.querySelectorAll('.order-checkbox').forEach(cb => cb.checked = false);
        document.getElementById('selectAll').checked = false;
    }

    function toggleAllOrders() {
        const checked = document.getElementById('selectAll').checked;
        document.querySelectorAll('.order-checkbox').forEach(cb => cb.checked = checked);
    }

    function quickCancelOrder(orderId) {
        if (!confirm('Are you sure you want to cancel this order?')) {
            return;
        }
        
        fetch(`/admin/order/${orderId}/cancel/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Order cancelled successfully.');
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        });
    }