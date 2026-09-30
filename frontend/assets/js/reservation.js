// ============================================
// KSU Smart Parking - Reservation Logic
// ============================================

let currentReservationSpaceId = null;
let currentReservationSpaceCode = null;
let currentReservationStatus = null;


// ============================================
// فتح نافذة الحجز
// ============================================

function openReservationModal(spaceId, spaceCode, status) {
    const user = getCurrentUser();

    if (!user) {
        if (confirm("يجب تسجيل الدخول أولاً للحجز. هل تريد تسجيل الدخول الآن؟")) {
            window.location.href = "admin/login.html";
        }
        return;
    }

    if (user.role !== "visitor") {
        alert("الحجز متاح للزوار فقط. أنت مسجل كـ " + getRoleName(user.role));
        return;
    }

    if (status !== "Available") {
        alert("هذا الموقف غير متاح للحجز حالياً.");
        return;
    }

    currentReservationSpaceId = spaceId;
    currentReservationSpaceCode = spaceCode;
    currentReservationStatus = status;

    document.getElementById("resSpaceCode").textContent = spaceCode;
    document.getElementById("resNotes").value = "";

    const modal = new bootstrap.Modal(document.getElementById("reservationModal"));
    modal.show();
}


// ============================================
// تأكيد الحجز
// ============================================

async function confirmReservation() {
    const token = localStorage.getItem("ksu_token");
    if (!token) {
        alert("انتهت الجلسة، يرجى تسجيل الدخول");
        window.location.href = "admin/login.html";
        return;
    }

    const notes = document.getElementById("resNotes").value.trim();
    const confirmBtn = document.getElementById("confirmReservationBtn");

    confirmBtn.disabled = true;
    confirmBtn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i> جاري الحجز...`;

    try {
        const response = await API.request("/reservations/", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: JSON.stringify({
                space_id: currentReservationSpaceId,
                notes: notes
            })
        });

        // إغلاق النافذة
        const modalEl = document.getElementById("reservationModal");
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();

        // عرض نجاح
        showReservationSuccess(response.reservation);

        // تحديث الصفحة
        setTimeout(() => {
            if (typeof loadParkingSpaces === "function") loadParkingSpaces();
        }, 1000);

    } catch (error) {
        console.error("Reservation Error:", error);

        let msg = "فشل إنشاء الحجز";
        try {
            const errData = JSON.parse(error.message);
            msg = errData.error || msg;
        } catch (e) {}

        alert("❌ " + msg);
    } finally {
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = `<i class="fas fa-check me-2"></i> تأكيد الحجز`;
    }
}


// ============================================
// عرض نجاح الحجز
// ============================================

function showReservationSuccess(reservation) {
    const successModal = document.getElementById("successModal");
    if (!successModal) {
        alert(`✅ تم إنشاء الحجز بنجاح!\nكود الحجز: ${reservation.reservation_code}`);
        return;
    }

    document.getElementById("successCode").textContent = reservation.reservation_code;
    document.getElementById("successSpace").textContent = reservation.space_code || "-";

    const modal = new bootstrap.Modal(successModal);
    modal.show();
}


// ============================================
// تحميل حجوزات الزائر
// ============================================

async function loadMyReservations() {
    const token = localStorage.getItem("ksu_token");
    if (!token) return;

    const container = document.getElementById("reservationsList");
    if (!container) return;

    try {
        const data = await API.request("/reservations/my", {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        });

        renderReservations(data.reservations);
        updateReservationStats(data.reservations);

    } catch (error) {
        console.error("Load Reservations Error:", error);
        container.innerHTML = `
            <div class="alert alert-danger">
                فشل تحميل الحجوزات: ${error.message}
            </div>
        `;
    }
}


// ============================================
// عرض الحجوزات
// ============================================

function renderReservations(reservations) {
    const container = document.getElementById("reservationsList");
    if (!container) return;

    if (!reservations || reservations.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-calendar-times fa-4x text-muted mb-3"></i>
                <h4 class="text-muted">لا توجد حجوزات بعد</h4>
                <p class="text-muted">احجز موقفك الأول الآن</p>
                <a href="visitor.html" class="btn btn-ksu">
                    <i class="fas fa-parking me-1"></i> عرض المواقف
                </a>
            </div>
        `;
        return;
    }

    container.innerHTML = reservations.map(r => {
        const statusInfo = getReservationStatusInfo(r.status);
        const date = new Date(r.reserved_at).toLocaleString("ar-SA");

        return `
            <div class="reservation-card ${statusInfo.class} mb-3">
                <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
                    <div>
                        <div class="d-flex align-items-center gap-2 mb-2">
                            <span class="badge ${statusInfo.badge}">
                                <i class="fas ${statusInfo.icon} me-1"></i>
                                ${statusInfo.label}
                            </span>
                            <small class="text-muted">${date}</small>
                        </div>
                        <h5 class="mb-1 fw-bold">
                            <i class="fas fa-parking text-warning me-1"></i>
                            الموقف: ${r.space_code}
                        </h5>
                        <p class="mb-1 text-muted small">
                            الصف: ${r.row_zone} | الرقم: ${r.space_number}
                        </p>
                        <p class="mb-0 small">
                            <strong>كود الحجز:</strong>
                            <code class="text-dark">${r.reservation_code}</code>
                        </p>
                        ${r.notes ? `<p class="mb-0 mt-2 small text-muted"><i class="fas fa-sticky-note me-1"></i>${r.notes}</p>` : ""}
                    </div>
                    <div class="text-end">
                        ${r.status === "Pending" ? `
                            <button class="btn btn-sm btn-outline-danger" onclick="cancelReservation(${r.reservation_id})">
                                <i class="fas fa-times me-1"></i> إلغاء
                            </button>
                        ` : ""}
                    </div>
                </div>
            </div>
        `;
    }).join("");
}


function getReservationStatusInfo(status) {
    const map = {
        "Pending": {
            label: "قيد الانتظار",
            icon: "fa-clock",
            badge: "bg-warning text-dark",
            class: "border-warning"
        },
        "Confirmed": {
            label: "مؤكد",
            icon: "fa-check-circle",
            badge: "bg-success",
            class: "border-success"
        },
        "Cancelled": {
            label: "ملغي",
            icon: "fa-times-circle",
            badge: "bg-secondary",
            class: "border-secondary"
        },
        "Rejected": {
            label: "مرفوض",
            icon: "fa-ban",
            badge: "bg-danger",
            class: "border-danger"
        },
        "Completed": {
            label: "مكتمل",
            icon: "fa-flag-checkered",
            badge: "bg-info",
            class: "border-info"
        }
    };
    return map[status] || map["Pending"];
}


// ============================================
// إحصائيات الحجوزات
// ============================================

function updateReservationStats(reservations) {
    const stats = {
        total: reservations.length,
        pending: reservations.filter(r => r.status === "Pending").length,
        confirmed: reservations.filter(r => r.status === "Confirmed").length,
        completed: reservations.filter(r => r.status === "Completed").length
    };

    const el = (id, val) => {
        const e = document.getElementById(id);
        if (e) e.textContent = val;
    };

    el("resTotal", stats.total);
    el("resPending", stats.pending);
    el("resConfirmed", stats.confirmed);
    el("resCompleted", stats.completed);
}


// ============================================
// إلغاء حجز
// ============================================

async function cancelReservation(reservationId) {
    if (!confirm("هل أنت متأكد من إلغاء هذا الحجز؟")) return;

    const token = localStorage.getItem("ksu_token");
    try {
        await API.request(`/reservations/${reservationId}/cancel`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${token}` }
        });
        alert("✅ تم إلغاء الحجز بنجاح");
        loadMyReservations();
    } catch (error) {
        console.error("Cancel Error:", error);
        alert("فشل إلغاء الحجز: " + error.message);
    }
}


// ============================================
// التهيئة
// ============================================

document.addEventListener("DOMContentLoaded", () => {
    // تحميل الحجوزات إذا كنا في صفحة my-reservations
    if (document.getElementById("reservationsList")) {
        loadMyReservations();
    }

    // ربط زر التأكيد
    const confirmBtn = document.getElementById("confirmReservationBtn");
    if (confirmBtn) {
        confirmBtn.addEventListener("click", confirmReservation);
    }
});