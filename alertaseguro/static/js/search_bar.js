document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("searchInput");
    const results = document.getElementById("results");

    if (!input || !results) {
        console.error("Erro: input ou results não encontrado");
        return;
    }

    let timeout = null;

    input.addEventListener("input", function () {
        clearTimeout(timeout);

        const query = this.value;

        timeout = setTimeout(() => {
            fetch(`?q=${encodeURIComponent(query)}`, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.text())
            .then(data => {
                results.innerHTML = data;
            })
            .catch(err => console.error(err));
        }, 300);
    });
});