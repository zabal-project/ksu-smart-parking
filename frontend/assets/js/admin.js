// ============================================
// KSU Smart Parking - Admin Dashboard Logic
// ============================================

let refreshTimer = null;
let currentEditSpaceId = null;
const adminAnimations = {};
let allUsers = [];
let allLogs = [];


// ============================================
// التهيئة
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    const token = requireAuth();
    if (!token) return;

    const user = getCurrentUser();
    if (user) {
        const el = document.getElementById("currentUserName");
        if (el) el.textContent = user.full_name || user.username;
    }

    // لوحة التحكم
    if (document.getElementById("parkingMapContainer")) {
        loadDashboard();
        refreshTimer = setInterval(loadDashboard, 10000);
    }

    // إدارة المستخدمين
    if (document.getElementById("usersTableBody")) {
        loadUsers();
    }

    // سجلات النشاط
    if (document.getElementById("logsTableBody")) {
        loadLogs();
    }
});


// ============================================
// لوحة التحكم
// ============================================

async function loadDashboard() {
    const indicator = document.getElementById("refreshIndicator");
    if (indicator) indicator.style.display = "inline-block";

    try {
        const data = await API.getSpaces();
        const stats = await API.request("/parking/stats");

        renderStats(stats);
        renderSpacesMap(data.spaces);

        const el = document.getElementById("lastUpdate");
        if (el) el.textContent = new Date().toLocaleTimeString("ar-SA");

    } catch (error) {
        console.error("Dashboard Error:", error);
    } finally {
        if (indicator) {
            setTimeout(() => indicator.style.display = "none", 500);
        }
    }
}


function animateStat(elementId, target) {
    const el = document.getElementById(elementId);
    if (!el) return;

    if (adminAnimations[elementId]) {
        clearInterval(adminAnimations[elementId]);
        delete adminAnimations[elementId];
    }

    let current = parseInt(el.textContent) || 0;
    if (current === target) { el.textContent = target; return; }

    const diff = target - current;
    const step = diff > 0 ? Math.ceil(Math.abs(diff) / 8) : -Math.ceil(Math.abs(diff) / 8);

    adminAnimations[elementId] = setInterval(() => {
        current += step;
        if ((step > 0 && current >= target) || (step < 0 && current <= target)) {
            current = target;
            clearInterval(adminAnimations[elementId]);
            delete adminAnimations[elementId];
        }
        el.textContent = current;
    }, 30);
}


function renderStats(stats) {
    const overall = stats.overall;
    const total = parseInt(overall.total) || 0;
    const available = parseInt(overall.available) || 0;
    const occupied = parseInt(overall.occupied) || 0;

    animateStat("statTotal", total);
    animateStat("statAvailable", available);
    animateStat("statOccupied", occupied);

    const rate = total > 0 ? Math.round((occupied / total) * 100) : 0;
    const rateEl = document.getElementById("statRate");
    if (rateEl) rateEl.textContent = rate + "%";

    // شريط التقدم
    const bar = document.getElementById("rateBar");
    if (bar) {
        bar.style.width = rate + "%";
        bar.classList.remove("warning", "danger");
        if (rate >= 80) bar.classList.add("danger");
        else if (rate >= 50) bar.classList.add("warning");
    }

    // الصفوف
    if (stats.by_zone) {
        stats.by_zone.forEach(zone => {
            const el = document.getElementById(`zone${zone.row_zone}_available`);
            if (el) animateStat(`zone${zone.row_zone}_available`, parseInt(zone.available) || 0);
        });
    }
}


function renderSpacesMap(spaces) {
    const container = document.getElementById("parkingMapContainer");
    if (!container) return;

    const rows = {};
    spaces.forEach(space => {
        if (!rows[space.row_zone]) rows[space.row_zone] = [];
        rows[space.row_zone].push(space);
    });

    let html = "";
    for (const [zone, zoneSpaces] of Object.entries(rows)) {
        const availableCount = zoneSpaces.filter(s => s.status === "Available").length;
        const totalCount = zoneSpaces.length;

        html += `
            <div class="zone-section">
                <div class="zone-header">
                    <div class="d-flex align-items-center gap-2">
                        <div class="zone-badge">${zone}</div>
                        <div>
                            <strong>الصف ${zone}</strong>
                            <div><small class="text-muted">${availableCount} / ${totalCount} متاح</small></div>
                        </div>
                    </div>
                    <span class="badge ${availableCount > 0 ? 'bg-success' : 'bg-danger'}">
                        ${availableCount > 0 ? 'متاح' : 'مشغول'}
                    </span>
                </div>
                <div class="row g-2">
                    ${zoneSpaces.map(space => `
                        <div class="col-6 col-md-3 col-lg-2">
                            <div class="space-card ${space.status.toLowerCase()}"
                                 onclick="openEditModal(${space.space_id}, '${space.space_code}', '${space.status}')">
                                <div class="space-code">${space.space_code}</div>
                                <div class="space-status ${space.status === 'Available' ? 'text-success' : 'text-danger'}">
                                    <i class="fas fa-${space.status === 'Available' ? 'check' : 'times'}"></i>
                                    ${space.status === 'Available' ? 'متاح' : 'مشغول'}
                                </div>
                            </div>
                        </div>
                    `).join("")}
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
}


function openEditModal(spaceId, spaceCode, currentStatus) {
    currentEditSpaceId = spaceId;
    document.getElementById("editSpaceCode").textContent = spaceCode;
    document.getElementById("editStatus").value = currentStatus;
    new bootstrap.Modal(document.getElementById("editModal")).show();
}


async function saveStatus() {
    const newStatus = document.getElementById("editStatus").value;
    const token = localStorage.getItem("ksu_token");

    if (!currentEditSpaceId || !token) {
        alert("خطأ: لم يتم تحديد الموقف");
        return;
    }

    try {
        await API.updateSpace(currentEditSpaceId, newStatus, token);
        const modalEl = document.getElementById("editModal");
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        loadDashboard();
        showToast("تم تحديث حالة الموقف بنجاح", "success");
    } catch (error) {
        console.error("Update Error:", error);
        showToast("فشل تحديث الحالة", "danger");
    }
}


function refreshStats() {
    loadDashboard();
    showToast("تم تحديث البيانات", "info");
}


function toggleSidebar() {
    document.getElementById("adminSidebar").classList.toggle("show");
}


// ============================================
// إدارة المستخدمين
// ============================================

async function loadUsers() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const tbody = document.getElementById("usersTableBody");
    if (!tbody) return;

    try {
        const data = await API.request("/admin/users", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        allUsers = data.users || [];
        renderUsers(allUsers);

        const totalEl = document.getElementById("totalUsers");
        if (totalEl) totalEl.textContent = allUsers.length;

    } catch (error) {
        console.error("Load Users Error:", error);
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-danger">فشل تحميل المستخدمين</td></tr>`;
    }
}


function renderUsers(users) {
    const tbody = document.getElementById("usersTableBody");
    if (!tbody) return;

    if (!users || users.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">لا يوجد مستخدمون</td></tr>`;
        return;
    }

    tbody.innerHTML = users.map((user, index) => {
        const roleClass = user.role_name || "visitor";
        const roleText = { "admin": "مدير", "staff": "موظف", "visitor": "زائر" }[roleClass] || roleClass;
        const statusBadge = user.is_active 
            ? `<span class="badge bg-success"><i class="fas fa-check me-1"></i>مفعل</span>`
            : `<span class="badge bg-danger"><i class="fas fa-times me-1"></i>معطل</span>`;
        const lastLogin = user.last_login ? new Date(user.last_login).toLocaleString("ar-SA") : "لم يسجل بعد";

        return `
            <tr data-user-id="${user.user_id}" data-role="${roleClass}" data-status="${user.is_active ? 'active' : 'inactive'}">
                <td>${index + 1}</td>
                <td><strong>${user.username}</strong></td>
                <td>${user.full_name || "-"}</td>
                <td><small>${user.email || "-"}</small></td>
                <td><span class="badge-role ${roleClass}">${roleText}</span></td>
                <td>${statusBadge}</td>
                <td><small class="text-muted">${lastLogin}</small></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-warning" onclick="openEditUserModal(${user.user_id})" title="تعديل"><i class="fas fa-edit"></i></button>
                        <button class="btn btn-info" onclick="toggleUserActive(${user.user_id})" title="تفعيل/تعطيل"><i class="fas fa-power-off"></i></button>
                        <button class="btn btn-secondary" onclick="resetUserPassword(${user.user_id})" title="إعادة تعيين كلمة المرور"><i class="fas fa-key"></i></button>
                        <button class="btn btn-danger" onclick="deleteUser(${user.user_id}, '${user.username}')" title="حذف"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}


function filterUsers() {
    const search = document.getElementById("searchInput")?.value.toLowerCase() || "";
    const role = document.getElementById("filterRole")?.value || "";
    const status = document.getElementById("filterStatus")?.value || "";

    const filtered = allUsers.filter(user => {
        const matchesSearch = !search ||
            user.username.toLowerCase().includes(search) ||
            (user.full_name || "").toLowerCase().includes(search) ||
            (user.email || "").toLowerCase().includes(search);
        const matchesRole = !role || user.role_name === role;
        const matchesStatus = !status ||
            (status === "active" && user.is_active) ||
            (status === "inactive" && !user.is_active);
        return matchesSearch && matchesRole && matchesStatus;
    });

    renderUsers(filtered);
}


function openAddUserModal() {
    document.getElementById("userModalTitle").innerHTML = `<i class="fas fa-user-plus me-2"></i> إضافة مستخدم جديد`;
    document.getElementById("userForm").reset();
    document.getElementById("editUserId").value = "";
    document.getElementById("userUsername").disabled = false;
    document.getElementById("passwordField").style.display = "block";
    document.getElementById("userPassword").required = true;
    document.getElementById("activeField").style.display = "none";
    new bootstrap.Modal(document.getElementById("userModal")).show();
}


function openEditUserModal(userId) {
    const user = allUsers.find(u => u.user_id === userId);
    if (!user) return;

    document.getElementById("userModalTitle").innerHTML = `<i class="fas fa-user-edit me-2"></i> تعديل: ${user.username}`;
    document.getElementById("editUserId").value = userId;
    document.getElementById("userUsername").value = user.username;
    document.getElementById("userUsername").disabled = true;
    document.getElementById("userFullName").value = user.full_name || "";
    document.getElementById("userEmail").value = user.email || "";
    document.getElementById("passwordField").style.display = "none";
    document.getElementById("userPassword").required = false;
    document.getElementById("activeField").style.display = "block";
    document.getElementById("userActive").checked = user.is_active;

    const roleMap = { "admin": "1", "staff": "2", "visitor": "3" };
    document.getElementById("userRole").value = roleMap[user.role_name] || "3";

    new bootstrap.Modal(document.getElementById("userModal")).show();
}


async function saveUser() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const userId = document.getElementById("editUserId").value;
    const isEdit = userId && userId !== "";

    const data = {
        username: document.getElementById("userUsername").value.trim(),
        full_name: document.getElementById("userFullName").value.trim(),
        email: document.getElementById("userEmail").value.trim(),
        role_id: parseInt(document.getElementById("userRole").value)
    };

    if (!data.username) { showToast("اسم المستخدم مطلوب", "danger"); return; }

    if (!isEdit) {
        const password = document.getElementById("userPassword").value;
        if (!password || password.length < 6) {
            showToast("كلمة المرور يجب أن تكون 6 أحرف على الأقل", "danger");
            return;
        }
        data.password = password;
    } else {
        data.is_active = document.getElementById("userActive").checked;
    }

    try {
        if (isEdit) {
            await API.request(`/admin/users/${userId}`, {
                method: "PUT",
                headers: { "Authorization": `Bearer ${token}` },
                body: JSON.stringify(data)
            });
            showToast("تم تحديث المستخدم بنجاح", "success");
        } else {
            await API.request("/admin/users", {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` },
                body: JSON.stringify(data)
            });
            showToast("تم إضافة المستخدم بنجاح", "success");
        }

        const modalEl = document.getElementById("userModal");
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
        loadUsers();
    } catch (error) {
        console.error("Save User Error:", error);
        let msg = "فشل حفظ المستخدم";
        try { const errData = JSON.parse(error.message); msg = errData.error || msg; } catch (e) {}
        showToast(msg, "danger");
    }
}


async function deleteUser(userId, username) {
    if (!confirm(`هل أنت متأكد من حذف المستخدم "${username}"؟`)) return;
    const token = localStorage.getItem("ksu_token");
    try {
        await API.request(`/admin/users/${userId}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
        showToast("تم حذف المستخدم بنجاح", "success");
        loadUsers();
    } catch (error) {
        console.error("Delete Error:", error);
        showToast("فشل حذف المستخدم", "danger");
    }
}


async function toggleUserActive(userId) {
    const token = localStorage.getItem("ksu_token");
    try {
        await API.request(`/admin/users/${userId}/toggle-active`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${token}` }
        });
        showToast("تم تغيير حالة المستخدم", "success");
        loadUsers();
    } catch (error) {
        console.error("Toggle Error:", error);
        showToast("فشل تغيير الحالة", "danger");
    }
}


async function resetUserPassword(userId) {
    const newPassword = prompt("أدخل كلمة المرور الجديدة (6 أحرف على الأقل):");
    if (!newPassword) return;
    if (newPassword.length < 6) { showToast("كلمة المرور يجب أن تكون 6 أحرف على الأقل", "danger"); return; }

    const token = localStorage.getItem("ksu_token");
    try {
        await API.request(`/admin/users/${userId}/reset-password`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ new_password: newPassword })
        });
        showToast("تم إعادة تعيين كلمة المرور", "success");
    } catch (error) {
        console.error("Reset Password Error:", error);
        showToast("فشل إعادة تعيين كلمة المرور", "danger");
    }
}


// ============================================
// سجلات النشاط
// ============================================

async function loadLogs() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const tbody = document.getElementById("logsTableBody");
    if (!tbody) return;

    const limit = document.getElementById("filterLimit")?.value || 100;

    try {
        const data = await API.request(`/logs/?limit=${limit}`, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        allLogs = data.logs || [];
        renderLogs(allLogs);
        updateLogsStats(allLogs);

        const totalEl = document.getElementById("totalLogs");
        if (totalEl) totalEl.textContent = data.total || allLogs.length;

    } catch (error) {
        console.error("Load Logs Error:", error);
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-danger">
            فشل تحميل السجلات: ${error.message}
        </td></tr>`;
    }
}


function renderLogs(logs) {
    const tbody = document.getElementById("logsTableBody");
    if (!tbody) return;

    if (!logs || logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">
            <i class="fas fa-inbox fa-2x mb-2"></i>
            <p class="mb-0">لا توجد سجلات</p>
        </td></tr>`;
        return;
    }

    tbody.innerHTML = logs.map((log, index) => {
        const actionInfo = getActionInfo(log.action);
        const dateTime = log.created_at ? new Date(log.created_at).toLocaleString("ar-SA") : "-";

        return `
            <tr data-action="${log.action}">
                <td>${index + 1}</td>
                <td><i class="fas fa-user-circle me-1 text-muted"></i><strong>${log.username || "نظام"}</strong></td>
                <td><span class="badge ${actionInfo.color}"><i class="fas ${actionInfo.icon} me-1"></i>${actionInfo.label}</span></td>
                <td><small>${log.details || "-"}</small></td>
                <td><small class="text-muted">${log.ip_address || "-"}</small></td>
                <td><small class="text-muted">${dateTime}</small></td>
            </tr>
        `;
    }).join("");
}


function getActionInfo(action) {
    const map = {
        "LOGIN": { label: "تسجيل دخول", icon: "fa-sign-in-alt", color: "bg-success" },
        "LOGOUT": { label: "تسجيل خروج", icon: "fa-sign-out-alt", color: "bg-secondary" },
        "UPDATE_STATUS": { label: "تحديث موقف", icon: "fa-edit", color: "bg-info" },
        "BULK_UPDATE": { label: "تحديث جماعي", icon: "fa-layer-group", color: "bg-info" },
        "CREATE_USER": { label: "إضافة مستخدم", icon: "fa-user-plus", color: "bg-primary" },
        "UPDATE_USER": { label: "تعديل مستخدم", icon: "fa-user-edit", color: "bg-warning" },
        "DELETE_USER": { label: "حذف مستخدم", icon: "fa-user-minus", color: "bg-danger" },
        "TOGGLE_USER": { label: "تفعيل/تعطيل", icon: "fa-power-off", color: "bg-warning" },
        "RESET_PASSWORD": { label: "إعادة تعيين", icon: "fa-key", color: "bg-warning" },
        "CHANGE_PASSWORD": { label: "تغيير كلمة المرور", icon: "fa-lock", color: "bg-warning" }
    };
    return map[action] || { label: action, icon: "fa-info-circle", color: "bg-secondary" };
}


function updateLogsStats(logs) {
    const loginCount = logs.filter(l => l.action === "LOGIN").length;
    const updateCount = logs.filter(l => l.action === "UPDATE_STATUS" || l.action === "BULK_UPDATE").length;
    const userCount = logs.filter(l => l.action?.includes("USER")).length;

    const loginEl = document.getElementById("loginLogs");
    const updateEl = document.getElementById("updateLogs");
    const userEl = document.getElementById("userLogs");

    if (loginEl) loginEl.textContent = loginCount;
    if (updateEl) updateEl.textContent = updateCount;
    if (userEl) userEl.textContent = userCount;
}


function filterLogs() {
    const search = document.getElementById("searchInput")?.value.toLowerCase() || "";
    const action = document.getElementById("filterAction")?.value || "";

    const filtered = allLogs.filter(log => {
        const matchesSearch = !search ||
            (log.username || "").toLowerCase().includes(search) ||
            (log.details || "").toLowerCase().includes(search) ||
            (log.action || "").toLowerCase().includes(search);
        const matchesAction = !action || log.action === action;
        return matchesSearch && matchesAction;
    });

    renderLogs(filtered);
}


// ============================================
// أدوات مساعدة
// ============================================

function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = "top: 20px; left: 20px; z-index: 9999; min-width: 250px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); border-radius: 12px;";
    toast.innerHTML = `<i class="fas fa-info-circle me-2"></i>${message}`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.5s";
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}