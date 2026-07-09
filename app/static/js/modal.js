function showProductDetails(shopifyId) {
    const prod = localProductsStore.find(
        p => String(p.shopify_product_id) === String(shopifyId)
    );

    if (!prod) return;

    const links = prod.additional_images
        ? prod.additional_images.split(",")
        : [];

    const firstImg = links.length > 0
        ? cleanAndFormatUrl(links[0])
        : "https://via.placeholder.com/300?text=No+Image";

    const mainImgElement = document.getElementById("modal_img");
    mainImgElement.src = firstImg;

    document.getElementById("modal_id").innerText =
        `Shopify ID: ${prod.shopify_product_id}`;

    document.getElementById("modal_orig_title").innerText =
        prod.original_title || "Bilinmeyen Ürün";

    document.getElementById("modal_ai_title").innerText =
        prod.title || "Oluşturulmadı";

    document.getElementById("modal_desc").innerText =
        stripHtml(prod.body_html || "Açıklama metni boş.");

    const galleryWrapper = document.getElementById("modal_gallery");
    galleryWrapper.innerHTML = "";

    if (links.length > 0) {
        links.forEach(imgUrlRaw => {
            const cleanImg = cleanAndFormatUrl(imgUrlRaw);

            if (cleanImg) {
                const imgNode = document.createElement("img");

                imgNode.src = cleanImg;
                imgNode.className = "gallery-item";

                imgNode.onclick = function () {
                    mainImgElement.src = cleanImg;
                };

                galleryWrapper.appendChild(imgNode);
            }
        });
    } else {
        galleryWrapper.innerHTML =
            '<span class="text-muted-custom small">Ek resim yok.</span>';
    }

    const myModal = new bootstrap.Modal(
        document.getElementById("detailModal")
    );

    myModal.show();
}