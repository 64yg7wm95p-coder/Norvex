function logoutUser() {
    fetch("/api/v1/auth/logout", {
        method: "POST"
    })
    .then(() => {
        window.location.href = "/login";
    })
    .catch(() => {
        alert("Çıkış yapılamadı.");
    });
}