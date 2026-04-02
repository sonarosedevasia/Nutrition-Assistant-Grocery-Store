function togglePassword() {
    const passwordInput = document.getElementById("password");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
}

async function login() {
    const email = document.querySelector('input[type="email"]').value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    try {
        // IMPORTANT: OAuth2 expects form data, not JSON
        const formData = new URLSearchParams();
        formData.append("username", email);  // must be "username"
        formData.append("password", password);

        const response = await fetch("http://127.0.0.1:8000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Login failed");
            return;
        }

        // Save JWT token
        localStorage.setItem("token", data.access_token);

        // Redirect based on role
        if (data.role === "admin") {
            window.location.href = "admin/admin-dashboard.html";
        } else {
            window.location.href = "home.html";
        }

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server");
    }
}

function goToResetPassword() {
    window.location.href = "reset-password.html";
}
function toggleNewPassword() {
    const input = document.getElementById("newPassword");
    input.type = input.type === "password" ? "text" : "password";
}

function toggleConfirmPassword() {
    const input = document.getElementById("confirmPassword");
    input.type = input.type === "password" ? "text" : "password";
}

function updatePassword() {
    alert("Password updated successfully!\nBackend integration will be added later.");
    window.location.href = "login.html";
}
function toggleRegPassword() {
    const input = document.getElementById("regPassword");
    input.type = input.type === "password" ? "text" : "password";
}

function toggleRegConfirmPassword() {
    const input = document.getElementById("regConfirmPassword");
    input.type = input.type === "password" ? "text" : "password";
}

async function registerUser() {
    const name = document.querySelector('input[placeholder="Enter your full name"]').value;
    const email = document.querySelector('input[placeholder="Enter your email"]').value;
    const phone = document.querySelector('input[placeholder="Enter your contact number"]').value;
    const password = document.getElementById("regPassword").value;
    const confirmPassword = document.getElementById("regConfirmPassword").value;

    if (!name || !email || !phone || !password || !confirmPassword) {
        alert("Please fill all fields");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                email: email,
                phone: phone,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (Array.isArray(data.detail)) {
                alert(data.detail[0].msg);
             } else {
                alert(data.detail || "Registration failed");
             }
        return;
        }

        alert("Registration successful! Please login.");
        window.location.href = "login.html";

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server");
    }
}
async function forgotPassword() {
    const email = document.querySelector('input[type="email"]').value;

    if (!email) {
        alert("Please enter your email");
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/auth/forgot-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: email })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Email not found");
            return;
        }

        // Save email temporarily for reset page
        localStorage.setItem("resetEmail", email);

        window.location.href = "reset-password.html";

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server");
    }
}

async function resetPassword() {
    const newPassword = document.getElementById("newPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (!newPassword || !confirmPassword) {
        alert("Please fill all fields");
        return;
    }

    if (newPassword !== confirmPassword) {
        alert("Passwords do not match");
        return;
    }

    const email = localStorage.getItem("resetEmail");
    if (!email) {
        alert("Session expired. Please try again.");
        window.location.href = "forgot-password.html";
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/auth/reset-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Password reset failed");
            return;
        }

        alert("Password updated successfully. Please login.");
        localStorage.removeItem("resetEmail");
        window.location.href = "login.html";

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server");
    }
}
