document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("menu-btn-filtros");
  const drop = document.getElementById("menu-drop-filtros");

  if (!btn || !drop) return;

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    drop.classList.toggle("hidden");
  });

  document.addEventListener("click", (e) => {
    if (!btn.contains(e.target) && !drop.contains(e.target)) {
      drop.classList.add("hidden");
    }
  });
});
  

