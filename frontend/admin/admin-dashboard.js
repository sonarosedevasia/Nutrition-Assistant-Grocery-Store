const API_BASE = "http://127.0.0.1:8000";

async function loadDashboardStats() {

    try {

        const response = await fetch(`${API_BASE}/admin/dashboard-stats`);
        const data = await response.json();

        document.getElementById("totalUsers").innerText = data.total_users;
        document.getElementById("totalProducts").innerText = data.total_products;
        document.getElementById("totalCategories").innerText = data.total_categories;
        document.getElementById("totalOrders").innerText = data.total_orders;
        document.getElementById("pendingOrders").innerText = data.pending_orders;
        document.getElementById("totalRevenue").innerText = "₹" + data.revenue;

    } catch (error) {
        console.error("Dashboard stats error:", error);
    }

}

loadDashboardStats();