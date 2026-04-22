document.addEventListener("DOMContentLoaded", () => {
  const TOAST_DURATION = 2500;

  setTimeout(() => {
    document.querySelectorAll(".toast").forEach(el => {
      el.style.opacity = "0";
      el.style.transform = "translateY(-10px)";
      el.style.transition = "all 0.3s ease";

      setTimeout(() => el.remove(), 500);
    });
  }, TOAST_DURATION);
});