// ============================================
// KSU Visitor Parking - Visit Logic
// ============================================

let currentStep = 1;
const totalSteps = 3;

// ============================================
// التهيئة
// ============================================
document.addEventListener("DOMContentLoaded", () => {
    // التحقق من تسجيل الدخول
    const token = requireAuth();
    if (!token) return;

    const user = getCurrentUser();
    if (user && user.role !== "visitor") {
        alert("هذه الصفحة للزوار فقط");
        window.location.href = "../index.html";
        return;
    }

    // تحميل المضيفين والمباني
    if (document.getElementById("visitForm")) {
        loadHosts();
        loadBuildings();
        setupForm();
        setupMinDate();
    }
});


// ============================================
// تعيين الحد الأدنى للتاريخ (اليوم)
// ============================================
function setupMinDate() {
    const dateInput = document.getElementById("scheduledDate");
    if (dateInput) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.min = today;
        dateInput.value = today;
    }
}


// ============================================
// تحميل المضيفين
// ============================================
async function loadHosts() {
    const token = localStorage.getItem("ksu_token");
    const select = document.getElementById("hostId");
    if (!select) return;

    try {
        // ملاحظة: نحتاج API لعرض المضيفين للزوار
        // حالياً، نستخدم API عام (سننشئه)
        const data = await API.request("/hosts/public", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (data.hosts && data.hosts.length > 0) {
            data.hosts.forEach(h => {
                const opt = document.createElement("option");
                opt.value = h.host_id;
                opt.textContent = `${h.full_name} - ${h.department || "غير محدد"}`;
                select.appendChild(opt);
            });
        } else {
            select.innerHTML = '<option value="">لا يوجد مضيفون متاحون</option>';
        }
    } catch (error) {
        console.error("Load Hosts Error:", error);
        select.innerHTML = '<option value="">فشل تحميل المضيفين</option>';
    }
}


// ============================================
// تحميل المباني
// ============================================
async function loadBuildings() {
    const select = document.getElementById("buildingId");
    if (!select) return;

    try {
        const data = await API.request("/buildings/", { method: "GET" });
        if (data.buildings) {
            data.buildings.forEach(b => {
                const opt = document.createElement("option");
                opt.value = b.building_id;
                opt.textContent = `${b.building_name} (${b.building_code})`;
                select.appendChild(opt);
            });
        }
    } catch (error) {
        console.error("Load Buildings Error:", error);
    }
}


// ============================================
// إعداد النموذج
// ============================================
function setupForm() {
    const form = document.getElementById("visitForm");
    if (form) {
        form.addEventListener("submit", handleSubmit);
    }
}


// ============================================
// التنقل بين الخطوات
// ============================================
function nextStep() {
    if (!validateStep(currentStep)) return;

    if (currentStep < totalSteps) {
        currentStep++;
        updateStepUI();
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepUI();
    }
}

function updateStepUI() {
    // إخفاء الكل
    for (let i = 1; i <= totalSteps; i++) {
        const content = document.getElementById(`stepContent${i}`);
        const step = document.getElementById(`step${i}`);
        if (content) content.style.display = "none";
        if (step) {
            step.classList.remove("active", "completed");
            if (i < currentStep) step.classList.add("completed");
            if (i === currentStep) step.classList.add("active");
        }
    }

    // إظهار الحالي
    const currentContent = document.getElementById(`stepContent${currentStep}`);
    if (currentContent) currentContent.style.display = "block";

    // تحديث الأزرار
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const submitBtn = document.getElementById("submitBtn");

    if (prevBtn) prevBtn.style.display = currentStep > 1 ? "block" : "none";
    if (nextBtn) nextBtn.style.display = currentStep < totalSteps ? "block" : "none";
    if (submitBtn) submitBtn.style.display = currentStep === totalSteps ? "block" : "none";

    // تعبئة ملخص
    if (currentStep === totalSteps) {
        fillSummary();
    }
}


// ============================================
// التحقق من صحة الخطوة
// ============================================
function validateStep(step) {
    if (step === 1) {
        const hostId = document.getElementById("hostId").value;
        const date = document.getElementById("scheduledDate").value;
        const time = document.getElementById("scheduledTime").value;

        if (!hostId) {
            showAlert("يجب اختيار المضيف", "danger");
            return false;
        }
        if (!date || !time) {
            showAlert("يجب تحديد التاريخ والوقت", "danger");
            return false;
        }
    } else if (step === 2) {
        const plate = document.getElementById("vehiclePlate").value.trim();
        if (!plate) {
            showAlert("يجب إدخال رقم اللوحة", "danger");
            return false;
        }
    }
    return true;
}


// ============================================
// ملء ملخص الزيارة
// ============================================
function fillSummary() {
    const box = document.getElementById("summaryBox");
    if (!box) return;

    const hostSelect = document.getElementById("hostId");
    const hostText = hostSelect.options[hostSelect.selectedIndex]?.text || "-";

    const buildingSelect = document.getElementById("buildingId");
    const buildingText = buildingSelect.value 
        ? buildingSelect.options[buildingSelect.selectedIndex]?.text 
        : "غير محدد";

    const date = document.getElementById("scheduledDate").value;
    const time = document.getElementById("scheduledTime").value;
    const plate = document.getElementById("vehiclePlate").value;
    const visitors = document.getElementById("visitorsCount").value;
    const purpose = document.getElementById("purpose").value;

    box.innerHTML = `
        <div class="row g-2">
            <div class="col-md-6">
                <small class="text-muted d-block">المضيف</small>
                <strong>${hostText}</strong>
            </div>
            <div class="col-md-6">
                <small class="text-muted d-block">المبنى</small>
                <strong>${buildingText}</strong>
            </div>
            <div class="col-md-6">
                <small class="text-muted d-block">التاريخ</small>
                <strong>${date}</strong>
            </div>
            <div class="col-md-6">
                <small class="text-muted d-block">الوقت</small>
                <strong>${time}</strong>
            </div>
            <div class="col-md-6">
                <small class="text-muted d-block">اللوحة</small>
                <strong>${plate}</strong>
            </div>
            <div class="col-md-6">
                <small class="text-muted d-block">عدد الزوار</small>
                <strong>${visitors}</strong>
            </div>
            ${purpose ? `
                <div class="col-12">
                    <small class="text-muted d-block">الغرض</small>
                    <strong>${purpose}</strong>
                </div>
            ` : ""}
        </div>
    `;
}


// ============================================
// إرسال النموذج
// ============================================
async function handleSubmit(e) {
    e.preventDefault();

    const token = localStorage.getItem("ksu_token");
    if (!token) {
        showAlert("انتهت الجلسة", "danger");
        return;
    }

    const submitBtn = document.getElementById("submitBtn");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i> جاري الإرسال...`;

    const data = {
        host_id: parseInt(document.getElementById("hostId").value),
        building_id: document.getElementById("buildingId").value 
            ? parseInt(document.getElementById("buildingId").value) 
            : null,
        purpose: document.getElementById("purpose").value.trim(),
        scheduled_date: document.getElementById("scheduledDate").value,
        scheduled_time: document.getElementById("scheduledTime").value,
        vehicle_plate: document.getElementById("vehiclePlate").value.trim(),
        vehicle_type: document.getElementById("vehicleType").value,
        visitors_count: parseInt(document.getElementById("visitorsCount").value) || 1,
        expected_duration: 60
    };

    try {
        const response = await API.request("/visits/", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: JSON.stringify(data)
        });

        // عرض نافذة النجاح
        document.getElementById("successCode").textContent = response.visit.visit_code;
        const modal = new bootstrap.Modal(document.getElementById("successModal"));
        modal.show();

    } catch (error) {
        console.error("Submit Error:", error);

        let msg = "فشل إرسال الطلب";
        try {
            const errData = JSON.parse(error.message);
            msg = errData.error || msg;
        } catch (e) {}

        showAlert("❌ " + msg, "danger");
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fas fa-paper-plane me-2"></i> إرسال الطلب`;
    }
}


// ============================================
// إظهار التنبيه
// ============================================
function showAlert(message, type) {
    const box = document.getElementById("alertBox");
    if (!box) return;

    box.className = `alert alert-${type}`;
    box.textContent = message;
    box.classList.remove("d-none");

    window.scrollTo({ top: 0, behavior: "smooth" });

    if (type === "danger") {
        setTimeout(() => box.classList.add("d-none"), 5000);
    }
}

// ============================================
// عرض زياراتي
// ============================================

async function loadMyVisits() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const container = document.getElementById("visitsList");
    if (!container) return;

    try {
        const data = await API.request("/visits/my", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        renderVisits(data.visits);
        updateVisitsStats(data.visits);

    } catch (error) {
        console.error("Load Visits Error:", error);
        container.innerHTML = `
            <div class="alert alert-danger">
                فشل تحميل الزيارات: ${error.message}
            </div>
        `;
    }
}


function renderVisits(visits) {
    const container = document.getElementById("visitsList");
    if (!container) return;

    if (!visits || visits.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-calendar-times fa-4x text-muted mb-3"></i>
                <h4 class="text-muted">لا توجد زيارات</h4>
                <p class="text-muted">ابدأ بإنشاء زيارة جديدة</p>
                <a href="visitor-visit.html" class="btn btn-ksu">
                    <i class="fas fa-plus me-1"></i> طلب زيارة
                </a>
            </div>
        `;
        return;
    }

    container.innerHTML = visits.map(v => {
        const info = getVisitStatusInfo(v.status);
        const date = v.scheduled_date 
            ? new Date(v.scheduled_date).toLocaleDateString("ar-SA") 
            : "-";
        const time = v.scheduled_time || "-";
        const canShowQR = v.status === "Approved" && v.permit_code;

        return `
            <div class="visit-card ${info.class}">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <div class="d-flex align-items-center gap-2 mb-2">
                            <span class="badge ${info.badge}">
                                <i class="fas ${info.icon} me-1"></i>
                                ${info.label}
                            </span>
                            <small class="text-muted">${v.visit_code}</small>
                        </div>

                        <h5 class="fw-bold mb-2">
                            <i class="fas fa-user-tie text-warning me-1"></i>
                            ${v.host_name || "المضيف"}
                        </h5>

                        <div class="row g-2 text-muted small">
                            <div class="col-md-6">
                                <i class="fas fa-calendar me-1"></i> ${date} - ${time}
                            </div>
                            ${v.building_name ? `
                                <div class="col-md-6">
                                    <i class="fas fa-building me-1"></i> ${v.building_name}
                                </div>
                            ` : ""}
                            ${v.vehicle_plate ? `
                                <div class="col-md-6">
                                    <i class="fas fa-car me-1"></i> ${v.vehicle_plate}
                                </div>
                            ` : ""}
                            ${v.purpose ? `
                                <div class="col-12">
                                    <i class="fas fa-info-circle me-1"></i> ${v.purpose}
                                </div>
                            ` : ""}
                        </div>
                    </div>

                    <div class="col-md-4 text-md-end mt-3 mt-md-0">
                        ${canShowQR ? `
                            <button class="btn btn-success w-100 mb-2" 
                                    onclick="showQR('${v.visit_code}', '${v.permit_code}', '${v.vehicle_plate || ''}', '${date} ${time}')">
                                <i class="fas fa-qrcode me-1"></i> عرض QR
                            </button>
                        ` : ""}

                        ${v.status === "Pending" ? `
                            <button class="btn btn-outline-danger btn-sm w-100" 
                                    onclick="cancelVisit(${v.visit_id})">
                                <i class="fas fa-times me-1"></i> إلغاء
                            </button>
                        ` : ""}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}


function getVisitStatusInfo(status) {
    const map = {
        "Pending": {
            label: "قيد الانتظار",
            icon: "fa-clock",
            badge: "bg-warning text-dark",
            class: "border-warning"
        },
        "Approved": {
            label: "موافق عليها",
            icon: "fa-check-circle",
            badge: "bg-success",
            class: "border-success"
        },
        "Rejected": {
            label: "مرفوضة",
            icon: "fa-times-circle",
            badge: "bg-danger",
            class: "border-danger"
        },
        "Completed": {
            label: "مكتملة",
            icon: "fa-flag-checkered",
            badge: "bg-info",
            class: "border-info"
        },
        "Cancelled": {
            label: "ملغية",
            icon: "fa-ban",
            badge: "bg-secondary",
            class: "border-secondary"
        },
        "Expired": {
            label: "منتهية",
            icon: "fa-hourglass-end",
            badge: "bg-dark",
            class: "border-dark"
        }
    };
    return map[status] || map["Pending"];
}


function updateVisitsStats(visits) {
    const el = (id, val) => {
        const e = document.getElementById(id);
        if (e) e.textContent = val;
    };

    el("visitTotal", visits.length);
    el("visitPending", visits.filter(v => v.status === "Pending").length);
    el("visitApproved", visits.filter(v => v.status === "Approved").length);
    el("visitCompleted", visits.filter(v => v.status === "Completed").length);
}


// ============================================
// عرض QR Code
// ============================================

let currentQR = null;

function showQR(visitCode, permitCode, plate, dateTime) {
    document.getElementById("qrVisitCode").textContent = visitCode;
    document.getElementById("qrPlate").textContent = plate || "-";
    document.getElementById("qrDateTime").textContent = dateTime || "-";

    const qrContainer = document.getElementById("qrcode");
    qrContainer.innerHTML = "";

    // توليد QR
    if (typeof QRCode !== "undefined") {
        new QRCode(qrContainer, {
            text: permitCode,
            width: 200,
            height: 200,
            colorDark: "#1a4d2e",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });
    } else {
        qrContainer.innerHTML = `<p class="text-muted">QR Code: ${permitCode}</p>`;
    }

    const modal = new bootstrap.Modal(document.getElementById("qrModal"));
    modal.show();
}


function printQR() {
    window.print();
}


// ============================================
// إلغاء زيارة
// ============================================

async function cancelVisit(visitId) {
    if (!confirm("هل أنت متأكد من إلغاء هذه الزيارة؟")) return;

    const token = localStorage.getItem("ksu_token");
    try {
        await API.request(`/visits/${visitId}/cancel`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${token}` }
        });
        alert("✅ تم إلغاء الزيارة");
        loadMyVisits();
    } catch (error) {
        console.error("Cancel Error:", error);
        alert("فشل إلغاء الزيارة: " + error.message);
    }
}