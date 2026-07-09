function loadProductsData() {
    fetch(`${API_BASE}/api/v1/products`)
        .then(res => res.json())
        .then(resData => {
            const products = resData.data || [];
            localProductsStore = products;

            const tBody = document.getElementById("tableBody");
            tBody.innerHTML = "";

            if (products.length === 0) {
                tBody.innerHTML = `
                    <tr>
                        <td colspan="7" class="text-center py-4 text-muted-custom">
                            Henüz işlenmiş ürün yok. Yukarıdan bir tarama başlatın.
                        </td>
                    </tr>
                `;
                return;
            }

            products.forEach(prod => {
                const links = prod.additional_images ? prod.additional_images.split(",") : [];
                const firstImgUrl = links.length > 0 ? cleanAndFormatUrl(links[0]) : "";

                let imageHtml = `
                    <div class="img-container">
                        <div class="w-100 h-100 d-flex align-items-center justify-content-center text-muted-custom" style="font-size:1.1rem;">
                            <i class="fa-solid fa-shirt"></i>
                        </div>
                    </div>
                `;

                if (firstImgUrl !== "") {
                    imageHtml = `
                        <div class="img-container">
                            <img src="${escapeHtml(firstImgUrl)}" class="product-thumb" alt="Product">
                        </div>
                    `;
                }

                const cleanDesc = stripHtml(prod.body_html || "").trim();

                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${imageHtml}</td>

                    <td class="text-dark-custom fw-semibold" style="font-size:0.9rem;">
                        ${escapeHtml(prod.original_title || "Orijinal Başlık")}
                    </td>

                    <td class="text-ai-green fw-semibold">
                        <i class="fa-solid fa-wand-magic-sparkles me-1 text-beige-premium"></i>
                        ${escapeHtml(prod.title || "")}
                    </td>

                    <td>
                        <div class="desc-truncate">
                            ${escapeHtml(cleanDesc)}
                        </div>
                    </td>

                    <td>
                        <span class="badge bg-white text-dark border">
                            £${parseFloat(prod.cost_price || 0).toFixed(2)}
                        </span>
                    </td>

                    <td>
                        <strong class="text-dark-custom">
                            £${parseFloat(prod.ebay_price || 0).toFixed(2)}
                        </strong>
                    </td>

                    <td>
                        <div class="d-flex flex-column gap-2">
                            <button onclick="showProductDetails('${escapeHtml(prod.shopify_product_id)}')" class="btn btn-outline-premium btn-sm rounded-pill px-3 fw-semibold">
                                <i class="fa-solid fa-magnifying-glass-plus me-1"></i>
                                İncele
                            </button>

                            <button onclick="sendToEbay('${escapeHtml(prod.shopify_product_id)}')" class="btn btn-warning btn-sm rounded-pill px-3 fw-bold">
                                🚀 eBay
                            </button>
                        </div>
                    </td>
                `;

                tBody.appendChild(row);
            });
        })
        .catch(err => console.error(err));
}