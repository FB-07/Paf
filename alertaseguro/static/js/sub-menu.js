function toggleSubmenu(id) {
  const menu = document.getElementById(id);
  const arrow = document.getElementById("arrow-" + id);
  const btn = document.getElementById("btn-" + id);

  document.querySelectorAll('[id^="submenu-"]').forEach(el => {
    if (el.id !== id) el.classList.add("hidden");
  });

  document.querySelectorAll('[id^="btn-submenu-"]').forEach(el => {
    if (el.id !== "btn-" + id) {
      el.classList.remove("border-white");
      el.classList.add("border-transparent");
    }
  });

  document.querySelectorAll('[id^="arrow-submenu-"]').forEach(el => {
    if (el.id !== "arrow-" + id) {
      el.innerHTML = "▸";
    }
  });

  const isHidden = menu.classList.contains("hidden");

  if (isHidden) {
    menu.classList.remove("hidden");

    if (arrow) arrow.innerHTML = "▾";

    if (btn) {
      btn.classList.remove("border-transparent");
      btn.classList.add("border-white");
    }

  } else {
    menu.classList.add("hidden");

    if (arrow) arrow.innerHTML = "▸";

    if (btn) {
      btn.classList.remove("border-white");
      btn.classList.add("border-transparent");
    }
  }
}