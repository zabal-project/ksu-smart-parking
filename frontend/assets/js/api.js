// ============================================
// KSU Smart Parking - API Helper
// ============================================

const API = {
    async request(endpoint, options = {}) {
        try {
            const url = `${CONFIG.API_BASE_URL}${endpoint}`;

            const defaultHeaders = {
                "Content-Type": "application/json"
            };

            const finalHeaders = {
                ...defaultHeaders,
                ...(options.headers || {})
            };

            const finalOptions = {
                ...options,
                headers: finalHeaders
            };

            const response = await fetch(url, finalOptions);

            // معالجة انتهاء التوكن (401)
            if (response.status === 401) {
                console.warn("⚠️ التوكن منتهي — جاري تسجيل الخروج...");
                localStorage.removeItem("ksu_token");
                localStorage.removeItem("ksu_user");
                window.location.href = "login.html";
                throw new Error("انتهت الجلسة، يرجى تسجيل الدخول مرة أخرى");
            }

            // معالجة عدم الصلاحية (403)
            if (response.status === 403) {
                const errorData = await response.json();
                throw new Error(errorData.error || "غير مصرح لك بهذه العملية");
            }

            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMessage = JSON.stringify(errorData);
                } catch (e) {}
                throw new Error(errorMessage);
            }

            return await response.json();
        } catch (error) {
            console.error("API Error:", error);
            throw error;
        }
    },

    async login(username, password) {
        return this.request(CONFIG.ENDPOINTS.LOGIN, {
            method: "POST",
            body: JSON.stringify({ username, password })
        });
    },

    async getSpaces() {
        return this.request(CONFIG.ENDPOINTS.SPACES, { method: "GET" });
    },

    async getZones() {
        return this.request(CONFIG.ENDPOINTS.ZONES, { method: "GET" });
    },

    async updateSpace(spaceId, status, token) {
        return this.request(`${CONFIG.ENDPOINTS.UPDATE_SPACE}/${spaceId}`, {
            method: "PUT",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ status })
        });
    }
};