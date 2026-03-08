document.addEventListener("DOMContentLoaded", () => {

  const panel = document.getElementById("incident-panel");
  const overlay = document.getElementById("incident-overlay");
  const closeBtn = document.getElementById("incident-close");
  const content = document.getElementById("incident-content");

  if (!panel) return;

  function openIncidentPanel(html) {
    content.innerHTML = html;

    panel.classList.remove("-translate-x-full");
    overlay.classList.remove("hidden");
  }

  function closeIncidentPanel() {
    panel.classList.add("-translate-x-full");
    overlay.classList.add("hidden");
  }

  closeBtn.addEventListener("click", closeIncidentPanel);
  overlay.addEventListener("click", closeIncidentPanel);

  window.openIncidentPanel = openIncidentPanel;
});