document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("salesChart");

    if (!canvas) {
        console.error("salesChart canvas not found");
        return;
    }

    const ctx = canvas.getContext("2d");

    const salesData = JSON.parse(
        document.getElementById("sales-data").textContent
    );

    new Chart(ctx, {
        type: "line",
        data: {
            labels: salesData.map(item => item.date),
            datasets: [{
                label: "Daily Sales (£)",
                data: salesData.map(item => item.total),
                borderColor: "#3498db",
                backgroundColor: "rgba(52, 152, 219, 0.2)",
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

});
