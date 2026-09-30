// ============================================
// KSU Visitor Parking - Security Dashboard
// ============================================

let currentVisit = null;


// ============================================
// التحقق من الكود
// ============================================

async function verifyCode() {
    const code = document.getElementById("permitCode").value.trim();
    if (!code) {
        alert("أدخل كود الزيارة أو التصريح");
        return;
    }

    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const resultBox = document.getElementById("resultBox");
    resultBox.className = "result-box";
    resultBox.innerHTML = `
        <div class="text-center">
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <p class="mt-2 mb-0">جاري التحقق...</p>
        </div>
    `;

    try {
        // جلب الزيارة بالكود
        const data = await API.request(`/visits/code/${code}`, {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        currentVisit = data.visit;
        renderVisitResult(data.visit);

    } catch (error) {
        console.error("Verify Error:", error);
        resultBox.className = "result-box danger";
        resultBox.innerHTML = `
            <div class="text-center">
                <i class="fas fa-times-circle fa-3x text-danger mb-2"></i>
                <h5 class="fw-bold text-danger">تصريح غير صحيح</h5>
                <p class="mb-0">${getErrorMessage(error)}</p>
            </div>
        `;
    }
}


function renderVisitResult(visit) {
    const resultBox = document.getElementById("resultBox");

    // التحقق من الحالة
    if (visit.status !== "Approved" && visit.status !== "Completed") {
        resultBox.className = "result-box danger";
        resultBox.innerHTML = `
            <div class="text-center">
                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-2"></i>
                <h5 class="fw-bold">الزيارة غير مصرح بها</h5>
                <p class="mb-2">الحالة: <strong>${getStatusText(visit.status)}</strong></p>
            </div>
        `;
        return;
    }

    // إذا كان قد دخل بالفعل
    if (visit.entry_time && !visit.exit_time) {
        resultBox.className = "result-box success";
        resultBox.innerHTML = `
            <div class="row align-items-center">
                <div class="col-md-8 text-md-start text-center">
                    <i class="fas fa-check-circle fa-3x text-success mb-2"></i>
                    <h5 class="fw-bold text-success">مسجل دخول</h5>
                    <p class="mb-1"><strong>${visit.visitor_name}</strong></p>
                    <p class="mb-1"><i class="fas fa-car me-1"></i>${visit.vehicle_plate}</p>
                    <p class="mb-1"><i class="fas fa-clock me-1"></i>دخل: ${formatDateTime(visit.entry_time)}</p>
                    <p class="mb-0"><i class="fas fa-building me-1"></i>${visit.building_name || "-"}</p>
                </div>
                <div class="col-md-4 text-center">
                    <button class="btn btn-info btn-lg w-100" onclick="logExit()">
                        <i class="fas fa-sign-out-alt me-2"></i> تسجيل خروج
                    </button>
                </div>
            </div>
        `;
        return;
    }

    // إذا خرج بالفعل
    if (visit.exit_time) {
        resultBox.className = "result-box danger";
        resultBox.innerHTML = `
            <div class="text-center">
                <i class="fas fa-flag-checkered fa-3x text-info mb-2"></i>
                <h5 class="fw-bold">الزيارة مكتملة</h5>
                <p class="mb-0">خرج في: ${formatDateTime(visit.exit_time)}</p>
            </div>
        `;
        return;
    }

    // تصريح ساري - لم يدخل بعد
    resultBox.className = "result-box success";
    resultBox.innerHTML = `
        <div class="row align-items-center">
            <div class="col-md-8 text-md-start text-center">
                <i class="fas fa-check-circle fa-3x text-success mb-2"></i>
                <h5 class="fw-bold text-success">تصريح ساري ✅</h5>
                <div class="row text-start mt-3">
                    <div class="col-6">
                        <small class="text-muted">الزائر:</small>
                        <p class="fw-bold mb-1">${visit.visitor_name}</p>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">اللوحة:</small>
                        <p class="fw-bold mb-1">${visit.vehicle_plate || "-"}</p>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">المضيف:</small>
                        <p class="fw-bold mb-1">${visit.host_name || "-"}</p>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">المبنى:</small>
                        <p class="fw-bold mb-1">${visit.building_name || "-"}</p>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">التاريخ:</small>
                        <p class="fw-bold mb-1">${visit.scheduled_date}</p>
                    </div>
                    <div class="col-6">
                        <small class="text-muted">الوقت:</small>
                        <p class="fw-bold mb-1">${visit.scheduled_time}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 text-center">
                <button class="btn btn-success btn-lg w-100" onclick="logEntry()">
                    <i class="fas fa-sign-in-alt me-2"></i> تسجيل دخول
                </button>
            </div>
        </div>
    `;
}


// ============================================
// تسجيل دخول
// ============================================

async function logEntry() {
    if (!currentVisit) return;

    if (!confirm(`تسجيل دخول للزائر: ${currentVisit.visitor_name}؟`)) return;

    const token = localStorage.getItem("ksu_token");
    try {
        await API.request("/security/entry", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: JSON.stringify({
                visit_id: currentVisit.visit_id,
                gate_number: "Main Gate"
            })
        });

        alert("✅ تم تسجيل الدخول بنجاح");
        document.getElementById("permitCode").value = "";
        document.getElementById("resultBox").className = "result-box";
        currentVisit = null;
        loadTodayLogs();

    } catch (error) {
        console.error("Entry Error:", error);
        alert("فشل تسجيل الدخول: " + getErrorMessage(error));
    }
}


// ============================================
// تسجيل خروج
// ============================================

async function logExit() {
    if (!currentVisit) return;

    if (!confirm(`تسجيل خروج للزائر: ${currentVisit.visitor_name}؟`)) return;

    const token = localStorage.getItem("ksu_token");
    try {
        await API.request("/security/exit", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: JSON.stringify({
                visit_id: currentVisit.visit_id,
                gate_number: "Main Gate"
            })
        });

        alert("✅ تم تسجيل الخروج بنجاح");
        document.getElementById("permitCode").value = "";
        document.getElementById("resultBox").className = "result-box";
        currentVisit = null;
        loadTodayLogs();

    } catch (error) {
        console.error("Exit Error:", error);
        alert("فشل تسجيل الخروج: " + getErrorMessage(error));
    }
}


// ============================================
// سجلات اليوم
// ============================================

async function loadTodayLogs() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const tbody = document.getElementById("logsTableBody");
    if (!tbody) return;

    try {
        const data = await API.request("/security/logs/today", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        renderLogs(data.logs || []);
        updateStats(data.logs || []);

    } catch (error) {
        console.error("Load Logs Error:", error);
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">
            لا توجد سجلات اليوم
        </td></tr>`;
    }
}


function renderLogs(logs) {
    const tbody = document.getElementById("logsTableBody");
    if (!tbody) return;

    if (!logs || logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-muted">
            <i class="fas fa-inbox fa-2x mb-2"></i>
            <p class="mb-0">لا توجد سجلات اليوم</p>
        </td></tr>`;
        return;
    }

    tbody.innerHTML = logs.map((log, i) => {
        const isEntry = log.action === "Entry";
        const badge = isEntry 
            ? '<span class="badge bg-success"><i class="fas fa-sign-in-alt me-1"></i>دخول</span>'
            : '<span class="badge bg-info"><i class="fas fa-sign-out-alt me-1"></i>خروج</span>';

        return `
            <tr>
                <td>${i + 1}</td>
                <td><strong>${log.visitor_name || "-"}</strong></td>
                <td><code>${log.visit_code || "-"}</code></td>
                <td>${badge}</td>
                <td><small>${log.gate_number || "-"}</small></td>
                <td><small class="text-muted">${formatDateTime(log.created_at)}</small></td>
            </tr>
        `;
    }).join("");
}


function updateStats(logs) {
    const entries = logs.filter(l => l.action === "Entry").length;
    const exits = logs.filter(l => l.action === "Exit").length;

    const el = (id, val) => {
        const e = document.getElementById(id);
        if (e) e.textContent = val;
    };

    el("statEntries", entries);
    el("statExits", exits);
    el("statApproved", entries - exits);
    el("statTotal", logs.length);
}


// ============================================
// أدوات
// ============================================

function getStatusText(status) {
    const map = {
        "Pending": "قيد الانتظار",
        "Approved": "موافق عليها",
        "Rejected": "مرفوضة",
        "Completed": "مكتملة",
        "Cancelled": "ملغية"
    };
    return map[status] || status;
}


function formatDateTime(dt) {
    if (!dt) return "-";
    try {
        return new Date(dt).toLocaleString("ar-SA");
    } catch {
        return dt;
    }
}


function getErrorMessage(error) {
    try {
        const data = JSON.parse(error.message);
        return data.error || error.message;
    } catch {
        return error.message || "خطأ غير معروف";
    }
}


// البحث بالضغط على Enter
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("permitCode");
    if (input) {
        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") verifyCode();
        });
    }
});