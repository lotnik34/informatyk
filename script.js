function showPage(pageId) {
    document.querySelectorAll(".page").forEach(page => {
        page.classList.remove("active");
    });
    document.getElementById(pageId).classList.add("active");
}

function toggleTheme() {
    document.body.classList.toggle("dark");
    document.body.classList.toggle("light");
}

document.getElementById("contactForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const status = document.getElementById("status");
    const formData = new FormData(this);

    const response = await fetch("http://127.0.0.1:5000/send", {
        method: "POST",
        body: formData
    });

    const result = await response.text();
    status.textContent = result;
    this.reset();
});
