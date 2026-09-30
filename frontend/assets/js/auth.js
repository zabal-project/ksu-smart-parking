// ============================================
// KSU Smart Parking - Authentication Logic
// ============================================


// ============================================
// التهيئة العامة
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    // تسجيل الدخول
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        const token = localStorage.getItem("ksu_token");
        if (token && isTokenValid() && window.location.pathname.includes("login.html")) {
            redirectByRole();
            return;
        }
        loginForm.addEventListener("submit", handleLogin);
        setupPasswordToggle();
        loadRememberedUser();
    }

    // التسجيل
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", handleRegister);
    }

    // التحقق التلقائي من التوكن
    if (localStorage.getItem("ksu_token")) {
        autoLogoutOnExpiry();
    }
});


// ============================================
// تسجيل الدخول
// ============================================

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const rememberMe = document.getElementById("rememberMe")?.checked || false;
    const loginBtn = document.getElementById("loginBtn");

    if (!username || !password) {
        showAlert("يرجى إدخال اسم المستخدم وكلمة المرور", "danger");
        return;
    }

    loginBtn.disabled = true;
    loginBtn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i> جاري تسجيل الدخول...`;

    try {
        const response = await API.login(username, password);

        localStorage.setItem("ksu_token", response.token);
        localStorage.setItem("ksu_user", JSON.stringify(response.user));

        if (rememberMe) {
            localStorage.setItem("ksu_remember", username);
        } else {
            localStorage.removeItem("ksu_remember");
        }

        // رسالة ترحيب حسب الدور
        const role = response.user.role;
        let welcomeMsg = "✅ مرحباً بك!";

        if (role === "admin") {
            welcomeMsg = "✅ مرحباً بك (مدير النظام)! جاري تحويلك...";
        } else if (role === "staff") {
            welcomeMsg = "✅ مرحباً بك (موظف)! جاري تحويلك...";
        } else if (role === "host") {
            welcomeMsg = "✅ مرحباً بك (مضيف)! جاري تحويلك إلى لوحة المضيف...";
        } else if (role === "security") {
            welcomeMsg = "✅ مرحباً بك (أمن)! جاري تحويلك إلى لوحة الأمن...";
        } else if (role === "visitor") {
            welcomeMsg = "✅ مرحباً بك (زائر)! جاري تحويلك إلى صفحة المواقف...";
        }

        showAlert(welcomeMsg, "success");

        setTimeout(() => {
            redirectByRole();
        }, 1000);

    } catch (error) {
        console.error("Login Error:", error);

        let errorMsg = "فشل تسجيل الدخول";
        try {
            const errData = JSON.parse(error.message);
            errorMsg = errData.error || errorMsg;
        } catch (e) {
            errorMsg = "اسم المستخدم أو كلمة المرور غير صحيحة";
        }

        showAlert("❌ " + errorMsg, "danger");
        loginBtn.disabled = false;
        loginBtn.innerHTML = `<i class="fas fa-sign-in-alt me-2"></i> تسجيل الدخول`;
    }
}


// ============================================
// التوجيه حسب الدور
// ============================================

function redirectByRole() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = "login.html";
        return;
    }

    const role = user.role;

    if (role === "admin" || role === "staff") {
        window.location.href = "dashboard.html";
    } else if (role === "host") {
        window.location.href = "host-dashboard.html";
    } else if (role === "security") {
        window.location.href = "security-dashboard.html";
    } else if (role === "visitor") {
        window.location.href = "../visitor.html";
    } else {
        window.location.href = "../index.html";
    }
}


// ============================================
// إظهار/إخفاء كلمة المرور
// ============================================

function setupPasswordToggle() {
    const toggleBtn = document.getElementById("togglePassword");
    const passwordInput = document.getElementById("password");
    const eyeIcon = document.getElementById("eyeIcon");

    if (!toggleBtn) return;

    toggleBtn.addEventListener("click", () => {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            eyeIcon.classList.remove("fa-eye");
            eyeIcon.classList.add("fa-eye-slash");
        } else {
            passwordInput.type = "password";
            eyeIcon.classList.remove("fa-eye-slash");
            eyeIcon.classList.add("fa-eye");
        }
    });
}


// ============================================
// تذكر المستخدم
// ============================================

function loadRememberedUser() {
    const remembered = localStorage.getItem("ksu_remember");
    if (remembered) {
        const usernameInput = document.getElementById("username");
        const rememberCheckbox = document.getElementById("rememberMe");
        const passwordInput = document.getElementById("password");

        if (usernameInput) usernameInput.value = remembered;
        if (rememberCheckbox) rememberCheckbox.checked = true;
        if (passwordInput) passwordInput.focus();
    }
}


// ============================================
// التنبيهات
// ============================================

function showAlert(message, type) {
    const alert = document.getElementById("loginAlert");
    if (!alert) return;

    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.classList.remove("d-none");

    if (type === "danger") {
        setTimeout(() => alert.classList.add("d-none"), 5000);
    }
}


function showRegisterAlert(message, type) {
    const alert = document.getElementById("registerAlert");
    if (!alert) return;

    alert.className = `alert alert-${type}`;
    alert.innerHTML = message;
    alert.classList.remove("d-none");

    if (type === "danger") {
        setTimeout(() => alert.classList.add("d-none"), 5000);
    }
}


// ============================================
// تسجيل الخروج
// ============================================

function logout() {
    if (confirm("هل أنت متأكد من تسجيل الخروج؟")) {
        localStorage.removeItem("ksu_token");
        localStorage.removeItem("ksu_user");

        const path = window.location.pathname;
        if (path.includes("/admin/")) {
            window.location.href = "../index.html";
        } else {
            window.location.href = "index.html";
        }
    }
}


// ============================================
// أدوات المصادقة
// ============================================

function requireAuth() {
    const token = localStorage.getItem("ksu_token");
    if (!token || !isTokenValid()) {
        localStorage.removeItem("ksu_token");
        localStorage.removeItem("ksu_user");
        window.location.href = "login.html";
        return null;
    }
    return token;
}


function getCurrentUser() {
    const userStr = localStorage.getItem("ksu_user");
    if (!userStr) return null;
    try {
        return JSON.parse(userStr);
    } catch (e) {
        return null;
    }
}


function hasRole(role) {
    const user = getCurrentUser();
    return user && user.role === role;
}


function hasAnyRole(roles = []) {
    const user = getCurrentUser();
    return user && roles.includes(user.role);
}


function getRoleName(role) {
    const map = {
        "admin": "مدير النظام",
        "staff": "موظف",
        "host": "مضيف",
        "security": "أمن",
        "visitor": "زائر"
    };
    return map[role] || role;
}


// ============================================
// 🔒 حماية الصفحات
// ============================================

function protectPage(allowedRoles = ["admin", "staff"], redirectUrl = null) {
    const token = localStorage.getItem("ksu_token");
    const userStr = localStorage.getItem("ksu_user");

    if (!token || !userStr || !isTokenValid()) {
        localStorage.removeItem("ksu_token");
        localStorage.removeItem("ksu_user");
        window.location.href = "login.html";
        return false;
    }

    let user;
    try {
        user = JSON.parse(userStr);
    } catch (e) {
        window.location.href = "login.html";
        return false;
    }

    if (!allowedRoles.includes(user.role)) {
        console.warn(`🚫 الوصول مرفوض: دور "${user.role}" غير مسموح`);

        if (!redirectUrl) {
            if (user.role === "visitor") {
                redirectUrl = "../visitor.html";
            } else if (user.role === "host") {
                redirectUrl = "host-dashboard.html";
            } else if (user.role === "security") {
                redirectUrl = "security-dashboard.html";
            } else {
                redirectUrl = "dashboard.html";
            }
        }

        setTimeout(() => {
            alert("⚠️ هذه الصفحة غير مصرح لك بالدخول إليها.\nسيتم تحويلك إلى صفحة مناسبة.");
            window.location.href = redirectUrl;
        }, 100);

        return false;
    }

    return true;
}


// ============================================
// التحقق من صلاحية JWT
// ============================================

function decodeJWT(token) {
    try {
        const parts = token.split(".");
        if (parts.length !== 3) return null;

        const payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
        const decoded = JSON.parse(atob(payload));
        return decoded;
    } catch (e) {
        console.error("JWT Decode Error:", e);
        return null;
    }
}


function isTokenValid() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return false;

    const decoded = decodeJWT(token);
    if (!decoded || !decoded.exp) return false;

    const now = Math.floor(Date.now() / 1000);
    return decoded.exp > now;
}


function autoLogoutOnExpiry() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const decoded = decodeJWT(token);
    if (!decoded || !decoded.exp) return;

    const now = Math.floor(Date.now() / 1000);
    const secondsUntilExpiry = decoded.exp - now;

    if (secondsUntilExpiry <= 0) {
        localStorage.removeItem("ksu_token");
        localStorage.removeItem("ksu_user");

        const path = window.location.pathname;
        if (path.includes("/admin/")) {
            window.location.href = "login.html";
        } else {
            window.location.href = "admin/login.html";
        }
        return;
    }

    if (secondsUntilExpiry <= 300) {
        console.warn(`⚠️ سينتهي التوكن خلال ${Math.floor(secondsUntilExpiry / 60)} دقيقة`);
    }

    setTimeout(() => {
        console.warn("⚠️ انتهى التوكن — تسجيل خروج تلقائي...");
        localStorage.removeItem("ksu_token");
        localStorage.removeItem("ksu_user");

        const path = window.location.pathname;
        if (path.includes("/admin/")) {
            window.location.href = "login.html";
        } else {
            window.location.href = "admin/login.html";
        }
    }, secondsUntilExpiry * 1000);
}


// ============================================
// تسجيل حساب جديد
// ============================================

async function handleRegister(e) {
    e.preventDefault();

    const username = document.getElementById("regUsername").value.trim();
    const fullName = document.getElementById("regFullName").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value;
    const passwordConfirm = document.getElementById("regPasswordConfirm").value;
    const registerBtn = document.getElementById("registerBtn");

    if (!username || username.length < 3) {
        showRegisterAlert("اسم المستخدم يجب أن يكون 3 أحرف على الأقل", "danger");
        return;
    }

    if (!password || password.length < 6) {
        showRegisterAlert("كلمة المرور يجب أن تكون 6 أحرف على الأقل", "danger");
        return;
    }

    if (password !== passwordConfirm) {
        showRegisterAlert("كلمتا المرور غير متطابقتين", "danger");
        return;
    }

    if (email && !email.includes("@")) {
        showRegisterAlert("البريد الإلكتروني غير صحيح", "danger");
        return;
    }

    registerBtn.disabled = true;
    registerBtn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i> جاري إنشاء الحساب...`;

    try {
        await API.request("/auth/register", {
            method: "POST",
            body: JSON.stringify({
                username,
                password,
                full_name: fullName,
                email
            })
        });

        showRegisterAlert("✅ تم إنشاء الحساب بنجاح! جاري تحويلك لتسجيل الدخول...", "success");

        setTimeout(() => {
            window.location.href = "login.html";
        }, 1500);

    } catch (error) {
        console.error("Register Error:", error);

        let msg = "فشل إنشاء الحساب";
        try {
            const errData = JSON.parse(error.message);
            msg = errData.error || msg;
        } catch (e) {}

        showRegisterAlert("❌ " + msg, "danger");
        registerBtn.disabled = false;
        registerBtn.innerHTML = `<i class="fas fa-user-plus me-2"></i> إنشاء الحساب`;
    }
}


// ============================================
// إظهار/إخفاء كلمة المرور في التسجيل
// ============================================

function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;

    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    }
}