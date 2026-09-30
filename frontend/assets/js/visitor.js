// ============================================
// KSU Smart Parking - Visitor Logic
// ============================================

let refreshTimer = null;

// متغيرات لتخزين مؤقتات الحركة (لمنع التراكم)
const visitorAnimations = {};


/**
 * تحميل المواقف من الـ API
 */
async function loadParkingSpaces() {
    try {
        const data = await API.getSpaces();
        renderParkingMap(data.spaces);
        updateStats(data.spaces);
    } catch (error) {
        console.error("Load Error:", error);
        showError("فشل تحميل المواقف. تأكد من تشغيل السيرفر.");
    }
}


function renderParkingMap(spaces) {
    const container = document.getElementById("parkingMap");
    if (!container) return;

    const rows = {};
    spaces.forEach(space => {
        if (!rows[space.row_zone]) rows[space.row_zone] = [];
        rows[space.row_zone].push(space);
    });

    let html = "";
    for (const [zone, zoneSpaces] of Object.entries(rows)) {
        const availableCount = zoneSpaces.filter(s => s.status === "Available").length;
        const rowClass = availableCount > 0 ? "available" : "occupied";

        html += `
            <div class="parking-row ${rowClass}">
                <div class="row-label">${zone}</div>
                ${zoneSpaces.map(space => `
                    <div class="parking-space ${space.status.toLowerCase()}"
                         data-tooltip="${space.space_code} - ${space.status === 'Available' ? 'متاح' : 'مشغول'}"
                         onclick="handleSpaceClick(${space.space_id}, '${space.space_code}', '${space.status}')">
                        ${space.space_number}
                    </div>
                `).join("")}
                <div class="ms-auto me-5 align-self-center">
                    <span class="badge ${availableCount > 0 ? 'bg-success' : 'bg-danger'} fs-6">
                        ${availableCount} / ${zoneSpaces.length} متاح
                    </span>
                </div>
            </div>
        `;
    }

    container.innerHTML = html;
    updateGuideBanner(rows);
}


/**
 * معالج النقر على الموقف
 */
function handleSpaceClick(spaceId, spaceCode, status) {
    const user = getCurrentUser();

    // إذا لم يكن مسجلاً، اعرض التفاصيل فقط
    if (!user) {
        showSpaceDetails(spaceId, spaceCode, status);
        return;
    }

    // إذا كان زائراً، افتح نافذة الحجز
    if (user.role === "visitor") {
        openReservationModal(spaceId, spaceCode, status);
        return;
    }

    // admin/staff → عرض التفاصيل
    showSpaceDetails(spaceId, spaceCode, status);
}


/**
 * تحديث الإحصائيات
 */
function updateStats(spaces) {
    const total = spaces.length;
    const available = spaces.filter(s => s.status === "Available").length;
    const occupied = total - available;

    animateNumber("totalSpaces", total);
    animateNumber("availableSpaces", available);
    animateNumber("occupiedSpaces", occupied);
}


/**
 * تحديث لافتة التوجيه
 */
function updateGuideBanner(rows) {
    const banner = document.getElementById("guideBanner");
    if (!banner) return;

    let bestZone = null;
    let maxAvailable = 0;

    for (const [zone, spaces] of Object.entries(rows)) {
        const available = spaces.filter(s => s.status === "Available").length;
        if (available > maxAvailable) {
            maxAvailable = available;
            bestZone = zone;
        }
    }

    if (bestZone && maxAvailable > 0) {
        banner.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-map-signs fa-3x me-3"></i>
                <div>
                    <h3 class="mb-1">التوجيه المقترح</h3>
                    <p class="mb-0 fs-5">
                        توجه إلى <strong class="text-warning">الصف ${bestZone}</strong>
                        — يحتوي على <strong>${maxAvailable}</strong> موقف متاح
                    </p>
                </div>
            </div>
        `;
        banner.classList.add("pulse-green");
    } else {
        banner.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-exclamation-triangle fa-3x me-3 text-warning"></i>
                <div>
                    <h3 class="mb-1">لا توجد مواقف متاحة حالياً</h3>
                    <p class="mb-0">يرجى المحاولة بعد قليل</p>
                </div>
            </div>
        `;
    }
}


/**
 * عرض تفاصيل موقف
 */
function showSpaceDetails(spaceId, spaceCode, status) {
    const statusText = status === "Available" ? "متاح ✅" : "مشغول ❌";
    alert(`الموقف: ${spaceCode}\nالحالة: ${statusText}`);
}


/**
 * تحديث الأرقام بحركة (بدون تراكم)
 */
function animateNumber(elementId, target) {
    const el = document.getElementById(elementId);
    if (!el) return;

    // إلغاء أي حركة سابقة على نفس العنصر
    if (visitorAnimations[elementId]) {
        clearInterval(visitorAnimations[elementId]);
        delete visitorAnimations[elementId];
    }

    let current = parseInt(el.textContent) || 0;

    // إذا كانت القيمة الحالية تساوي الهدف، لا داعي للحركة
    if (current === target) {
        el.textContent = target;
        return;
    }

    const diff = target - current;
    const step = diff > 0 ? Math.ceil(Math.abs(diff) / 8) : -Math.ceil(Math.abs(diff) / 8);

    visitorAnimations[elementId] = setInterval(() => {
        current += step;
        if ((step > 0 && current >= target) || (step < 0 && current <= target)) {
            current = target;
            clearInterval(visitorAnimations[elementId]);
            delete visitorAnimations[elementId];
        }
        el.textContent = current;
    }, 30);
}


/**
 * عرض خطأ
 */
function showError(message) {
    console.error(message);
    const container = document.getElementById("parkingMap");
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger text-center">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}


/**
 * بدء التحديث التلقائي
 */
function startAutoRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    // تحديث كل 10 ثوانٍ بدلاً من 5
    refreshTimer = setInterval(loadParkingSpaces, 10000);
}


/**
 * عند تحميل الصفحة
 */
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("parkingMap")) {
        loadParkingSpaces();
        startAutoRefresh();
    }
});
