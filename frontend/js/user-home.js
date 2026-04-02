function searchProducts() {
    const query = document.getElementById("searchInput").value;

    if (!query.trim()) return;

    window.location.href = `shop-products.html?search=${query}`;
}


document.getElementById("searchInput").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        searchProducts();
    }
});
/* ================= TOP SELLING PRODUCTS ================= */

const API_BASE = "http://127.0.0.1:8000";

async function loadTopSelling() {

    const container = document.getElementById("topSellingProducts");

    if (!container) return;

    try {

        const response = await fetch(`${API_BASE}/orders/top-selling`);

        const products = await response.json();

        container.innerHTML = "";

        products.forEach(product => {

            container.innerHTML += `
                <div class="product-card">

                    <img src="${API_BASE}/${product.image_path}">

                    <h4>${product.name}</h4>

                    <p>₹${product.price} per ${product.package_size} ${product.unit}</p>

                    <button onclick="addToCart(${product.id}, event)">
                        Add to Cart
                    </button>

                </div>
            `;

        });

    } catch (error) {
        console.error("Failed to load products", error);
    }
}

/* ================= ADD TO CART ================= */

async function addToCart(id, event) {

    if(event) event.stopPropagation();

    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please login first");
        window.location.href = "login.html";
        return;
    }

    try {

        const response = await fetch(
            `${API_BASE}/cart/add/${id}?quantity=1`,
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Failed to add to cart");
            return;
        }

        showToast("Item added to cart");

        loadCartCount(); // update cart counter

    } catch (error) {
        console.error(error);
    }
}


/* LOAD PRODUCTS WHEN PAGE OPENS */

loadTopSelling();
function showToast(message) {

    const toast = document.getElementById("toast");

    if (!toast) return;

    toast.innerText = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2000);
}
async function loadCartCount() {

    const token = localStorage.getItem("token");

    if (!token) return;

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/cart/my",
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const cartItems = await response.json();

        let totalItems = 0;

        cartItems.forEach(item => {
            totalItems += item.quantity;
        });

        const badge = document.getElementById("cartCount");

        if (!badge) return;

        if (totalItems === 0) {
            badge.style.display = "none";
        } else {
            badge.style.display = "flex";
            badge.innerText = totalItems;
        }

    } catch (error) {
        console.error("Cart count error:", error);
    }
}
loadCartCount();