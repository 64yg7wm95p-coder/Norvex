function startDirectScan() {
    const urlInput = document.getElementById("form_site_url").value.trim();

    if (!urlInput.startsWith("http")) {
        alert("Lütfen geçerli bir URL girin!");
        return;
    }

    const payload = {
        user_id: 1,
        site_url: urlInput,
        limit: parseInt(document.getElementById("form_limit").value, 10) || 4
    };

    const btn = document.getElementById("btn_start");

    btn.disabled = true;
    btn.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2"></span>
        Taranıyor...
    `;

    document.getElementById("progress_container").classList.remove("d-none");

    updateProgressBar(
        0,
        "Tarama emri gönderildi...",
        "info"
    );

    fetch(`${API_BASE}/api/v1/scan/bulk`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    })
        .then(async response => {
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(
                    data.detail || "Tarama başlatılamadı."
                );
            }

            if (checkInterval) {
                clearInterval(checkInterval);
            }

            checkInterval = setInterval(
                trackLiveProgress,
                1000
            );
        })
        .catch(err => {
            updateProgressBar(
                100,
                err.message,
                "error"
            );

            const bar = document.getElementById("progress_bar");

            bar.classList.remove(
                "progress-bar-info",
                "progress-bar-success"
            );

            bar.classList.add("progress-bar-error");

            document.getElementById("progress_perc").innerText = "HATA";

            btn.disabled = false;
            btn.innerHTML = `
                <i class="fa-solid fa-play me-2"></i>
                Taramayı Başlat
            `;
        });
}


function trackLiveProgress() {
    fetch(`${API_BASE}/api/v1/scan/progress`)
        .then(r => r.json())
        .then(status => {
            const bar = document.getElementById("progress_bar");

            bar.classList.remove(
                "progress-bar-info",
                "progress-bar-success",
                "progress-bar-error"
            );

            if (status.status_type === "error") {
                bar.classList.add("progress-bar-error");
            } else if (status.status_type === "success") {
                bar.classList.add("progress-bar-success");
            } else {
                bar.classList.add("progress-bar-info");
            }

            if (status.is_running) {
                let percent = 0;

                if (status.total > 0) {
                    percent = Math.round(
                        status.current / status.total * 100
                    );
                }

                updateProgressBar(
                    percent,
                    status.msg || "İşleniyor...",
                    status.status_type
                );

                loadProductsData();
            } else {
                clearInterval(checkInterval);

                const btn = document.getElementById("btn_start");

                btn.disabled = false;
                btn.innerHTML = `
                    <i class="fa-solid fa-play me-2"></i>
                    Taramayı Başlat
                `;

                if (status.status_type === "error") {
                    updateProgressBar(
                        100,
                        status.msg || "Hata oluştu.",
                        "error"
                    );

                    document.getElementById("progress_perc").innerText = "HATA";
                } else {
                    updateProgressBar(
                        100,
                        status.msg || "Tarama tamamlandı.",
                        "success"
                    );

                    document.getElementById("progress_perc").innerText = "100%";
                }

                loadProductsData();
            }
        });
}


function updateProgressBar(percent, msg, type) {
    document.getElementById("progress_bar").style.width = percent + "%";
    document.getElementById("progress_perc").innerText = percent + "%";
    document.getElementById("progress_msg").innerHTML = escapeHtml(msg);
}