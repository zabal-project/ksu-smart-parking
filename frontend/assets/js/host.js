// ============================================
// KSU Visitor Parking - Host Dashboard Logic
// ============================================

let allVisits = [];
let currentFilter = "Pending";
let currentVisitId = null;


// ============================================
// تحميل زيارات المضيف
// ============================================

async function loadHostVisits() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const container = document.getElementById("visitsContainer");
    if (!container) return;

    try {
        const data = await API.request("/hosts/me/visits", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        allVisits = data.visits || [];
        renderVisits();
        updateStats();

    } catch (error) {
        console.error("Load Host Visits Error:", error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                فشل تحميل الزيارات: ${error.message}
            </div>
        `;
    }
}


// ============================================
// عرض الزيارات
// ============================================

function renderVisits() {
    const container = document.getElementById("visitsContainer");
    if (!container) return;

    let filtered = allVisits;
    if (currentFilter !== "all") {
        filtered = allVisits.filter(v => v.status === currentFilter);
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-inbox fa-4x text-muted mb-3"></i>
                <h4 class="text-muted">لا توجد زيارات</h4>
                <p class="text-muted">
                    ${currentFilter === "Pending" ? "لا توجد طلبات قيد الانتظار" : 
                      currentFilter === "Approved" ? "لا توجد زيارات موافق عليها" :
                      currentFilter === "Rejected" ? "لا توجد زيارات مرفوضة" : "لا توجد زيارات"}
                </p>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(v => {
        const info = getVisitStatusInfo(v.status);
        const date = v.scheduled_date ? new Date(v.scheduled_date).toLocaleDateString("ar-SA") : "-";
        const time = v.scheduled_time || "-";

        return `
            <div class="visit-card ${v.status.toLowerCase()}">
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
                            <i class="fas fa-user text-warning me-1"></i>
                            ${v.visitor_name || "زائر"}
                        </h5>

                        <div class="row g-2 text-muted small">
                            <div class="col-md-6">
                                <i class="fas fa-calendar me-1"></i> ${date} - ${time}
                            </div>
                            ${v.vehicle_plate ? `
                                <div class="col-md-6">
                                    <i class="fas fa-car me-1"></i> ${v.vehicle_plate}
                                </div>
                            ` : ""}
                            ${v.building_name ? `
                                <div class="col-md-6">
                                    <i class="fas fa-building me-1"></i> ${v.building_name}
                                </div>
                            ` : ""}
                            <div class="col-md-6">
                                <i class="fas fa-users me-1"></i> ${v.visitors_count || 1} زائر
                            </div>
                            ${v.purpose ? `
                                <div class="col-12">
                                    <i class="fas fa-info-circle me-1"></i> ${v.purpose}
                                </div>
                            ` : ""}
                            ${v.host_notes ? `
                                <div class="col-12 text-success">
                                    <i class="fas fa-sticky-note me-1"></i> ملاحظاتي: ${v.host_notes}
                                </div>
                            ` : ""}
                            ${v.rejection_reason ? `
                                <div class="col-12 text-danger">
                                    <i class="fas fa-times-circle me-1"></i> سبب الرفض: ${v.rejection_reason}
                                </div>
                            ` : ""}
                        </div>
                    </div>

                    <div class="col-md-4 text-md-end mt-3 mt-md-0">
                        ${v.status === "Pending" ? `
                            <button class="btn btn-success w-100 mb-2" 
                                    onclick="openApproveModal(${v.visit_id}, '${v.visitor_name}')">
                                <i class="fas fa-check me-1"></i> موافقة
                            </button>
                            <button class="btn btn-danger w-100" 
                                    onclick="openRejectModal(${v.visit_id}, '${v.visitor_name}')">
                                <i class="fas fa-times me-1"></i> رفض
                            </button>
                        ` : `
                            <small class="text-muted">${info.label}</small>
                        `}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}


function getVisitStatusInfo(status) {
    const map = {
        "Pending": { label: "قيد الانتظار", icon: "fa-clock", badge: "bg-warning text-dark" },
        "Approved": { label: "موافق عليها", icon: "fa-check-circle", badge: "bg-success" },
        "Rejected": { label: "مرفوضة", icon: "fa-times-circle", badge: "bg-danger" },
        "Completed": { label: "مكتملة", icon: "fa-flag-checkered", badge: "bg-info" },
        "Cancelled": { label: "ملغية", icon: "fa-ban", badge: "bg-secondary" }
    };
    return map[status] || map["Pending"];
}


// ============================================
// الإحصائيات
// ============================================

function updateStats() {
    const el = (id, val) => {
        const e = document.getElementById(id);
        if (e) e.textContent = val;
    };

    const pending = allVisits.filter(v => v.status === "Pending").length;
    el("statPending", pending);
    el("statApproved", allVisits.filter(v => v.status === "Approved").length);
    el("statRejected", allVisits.filter(v => v.status === "Rejected").length);
    el("statTotal", allVisits.length);

    // Badge
    const badge = document.getElementById("pendingBadge");
    if (badge) {
        if (pending > 0) {
            badge.textContent = pending;
            badge.style.display = "inline-block";
        } else {
            badge.style.display = "none";
        }
    }
}


// ============================================
// الفلترة
// ============================================

function filterVisits(status, btn) {
    currentFilter = status;
    // تحديث التبويبات
    document.querySelectorAll(".nav-pills .nav-link").forEach(b => b.classList.remove("active"));
    if (btn) btn.classList.add("active");
    renderVisits();
}


// ============================================
// الموافقة
// ============================================

function openApproveModal(visitId, visitorName) {
    currentVisitId = visitId;
    document.getElementById("approveVisitorName").textContent = visitorName;
    document.getElementById("approveNotes").value = "";
    new bootstrap.Modal(document.getElementById("approveModal")).show();
}


async function confirmApprove() {
    const token = localStorage.getItem("ksu_token");
    const notes = document.getElementById("approveNotes").value.trim();

    try {
        await API.request(`/visits/${currentVisitId}/approve`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ notes: notes })
        });

        const modalEl = document.getElementById("approveModal");
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        alert("✅ تمت الموافقة على الزيارة. تم إنشاء تصريح QR تلقائياً.");
        loadHostVisits();

    } catch (error) {
        console.error("Approve Error:", error);
        alert("فشل الموافقة: " + error.message);
    }
}


// ============================================
// الرفض
// ============================================

function openRejectModal(visitId, visitorName) {
    currentVisitId = visitId;
    document.getElementById("rejectVisitorName").textContent = visitorName;
    document.getElementById("rejectReason").value = "";
    new bootstrap.Modal(document.getElementById("rejectModal")).show();
}


async function confirmReject() {
    const token = localStorage.getItem("ksu_token");
    const reason = document.getElementById("rejectReason").value.trim();

    if (!reason) {
        alert("يجب إدخال سبب الرفض");
        return;
    }

    try {
        await API.request(`/visits/${currentVisitId}/reject`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${token}` },
            body: JSON.stringify({ reason: reason })
        });

        const modalEl = document.getElementById("rejectModal");
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        alert("تم رفض الزيارة");
        loadHostVisits();

    } catch (error) {
        console.error("Reject Error:", error);
        alert("فشل الرفض: " + error.message);
    }
}