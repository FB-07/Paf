document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn-topo");
  if (!btn) return;

  btn.style.display = "none";

  window.addEventListener("scroll", () => {
    btn.style.display = window.scrollY > 200 ? "block" : "none";
  });

  btn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  });
});