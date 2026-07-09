const API_BASE = window.location.origin;

let checkInterval = null;
let localProductsStore = [];

function escapeHtml(value) {
    if (value === null || value === undefined) return "";

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function stripHtml(value) {
    if (!value) return "";

    const div = document.createElement("div");
    div.innerHTML = value;

    return div.textContent || div.innerText || "";
}

function cleanAndFormatUrl(singleUrl) {
    if (!singleUrl || singleUrl.trim() === "") return "";

    const clean = singleUrl.trim();

    if (clean.startsWith("//")) {
        return "https:" + clean;
    }

    return clean;
}