const API = "http://127.0.0.1:8000";

let allUsers = [];

async function loadUsers(){

const res = await fetch(`${API}/users/admin/all-users`);
allUsers = await res.json();

renderUsers(allUsers);

}

function renderUsers(users){

const table = document.querySelector("#usersTable tbody");
table.innerHTML="";

users.forEach(user=>{

table.innerHTML+=`

<tr>

<td>USR${user.id}</td>

<td>${user.name}</td>

<td>${user.email}</td>

<td>${user.phone}</td>

<td>${user.orders}</td>

</tr>

`;

});

}

function searchUsers(){

const query = document
.getElementById("searchInput")
.value
.toLowerCase();

const filtered = allUsers.filter(user =>
user.name.toLowerCase().includes(query) ||
user.email.toLowerCase().includes(query)
);

renderUsers(filtered);

}

document
.getElementById("searchInput")
.addEventListener("keyup", searchUsers);



loadUsers();