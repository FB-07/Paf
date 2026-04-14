function toggleSubmenu(id) {
  const menu = document.getElementById(id);
  const arrow = document.getElementById("arrow-" + id);

  menu.classList.toggle("hidden");

  if (arrow) {
    if (menu.classList.contains("hidden")) {
      arrow.innerHTML = "&gt;";
    } else {
      arrow.innerHTML = "v";
    }
  }
}