const API = "http://127.0.0.1:8000/orders";

let allOrders = [];

async function loadOrders(){

const res = await fetch(`${API}/admin/all`);
allOrders = await res.json();

renderOrders(allOrders);

}

function renderOrders(orders){

const table = document.querySelector("#ordersTable tbody");
table.innerHTML="";

orders.forEach(order=>{

table.innerHTML+=`

<tr>

<td>ORD${order.id}</td>

<td>${order.customer_name}</td>

<td>${order.phone}</td>

<td>${new Date(order.date).toLocaleDateString()}</td>

<td>₹${order.total}</td>
<td>${order.payment_method.toUpperCase()}</td>
<td>

<select class="status-select ${order.status}" 
onchange="updateStatus(${order.id},this.value)">

<option ${order.status=="placed"?"selected":""}>placed</option>

<option ${order.status=="packed"?"selected":""}>packed</option>

<option ${order.status=="delivered"?"selected":""}>delivered</option>

</select>

</td>

<td>

<button onclick="viewOrder(${order.id})">👁</button>

</td>

</tr>

`;

});

}

function searchOrders(){

const query = document
.getElementById("searchInput")
.value
.toLowerCase();

const filtered = allOrders.filter(order =>
order.customer_name.toLowerCase().includes(query) ||
("ord"+order.id).includes(query)
);

renderOrders(filtered);

}

document
.getElementById("searchInput")
.addEventListener("keyup", searchOrders);

async function viewOrder(id){

const res = await fetch(`${API}/admin/${id}`);
const order = await res.json();

let subtotal = 0;

let html = `

<h3>Customer</h3>

<div class="customer-box">
<p><strong>${order.customer_name}</strong></p>
<p>${order.phone}</p>
<p>${order.address}</p>
</div>

<h3>Items</h3>

<div class="items-list">

`;

order.items.forEach(item=>{

subtotal += item.subtotal;

html += `

<div class="order-item">

<img src="http://127.0.0.1:8000/${item.image}" class="order-item-img">

<div class="order-item-info">

<div class="item-name">${item.name}</div>
<div class="item-qty">Qty: ${item.quantity}</div>

</div>

<div class="item-price">
₹${item.subtotal.toFixed(2)}
</div>

</div>

`;

});

const tax = subtotal * 0.10;
const total = subtotal + tax;

html += `

</div>

<div class="order-total">

<div>Subtotal : ₹${subtotal.toFixed(2)}</div>
<div>Tax (10%) : ₹${tax.toFixed(2)}</div>

<div class="total-final">
Total = Subtotal + Tax = ₹${total.toFixed(2)}
</div>

</div>

`;
document.getElementById("orderDetails").innerHTML=html;

document.getElementById("orderModal").style.display="flex";

}

function closeModal(){

document.getElementById("orderModal").style.display="none";

}

async function updateStatus(id,status){

await fetch(`${API}/admin/${id}/status?status=${status}`,{
method:"PUT"
});

loadOrders();

}

loadOrders();