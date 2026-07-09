function sendToEbay(shopifyId) {
    if (!confirm("Bu ürünü eBay'e göndermek istiyor musun?")) {
        return;
    }

    fetch("/api/v1/ebay/list?shopify_id=" + encodeURIComponent(shopifyId), {
        method: "POST"
    })
        .then(async response => {
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                const detail = data.detail || data.error || "Bilinmeyen sunucu hatası";
                throw new Error(detail);
            }

            return data;
        })
        .then(data => {
            alert(
                data.success
                    ? "✅ Ürün başarıyla eBay'e aktarıldı!\neBay ID: " + (data.ebay_id || "Yok")
                    : "❌ Hata: " + (data.error || "Bilinmeyen hata")
            );
        })
        .catch(err => {
            console.error("eBay hata detayı:", err);
            alert("❌ eBay Hatası:\n" + err.message);
        });
}