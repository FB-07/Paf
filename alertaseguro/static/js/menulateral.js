document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menu-btn");
  const sideMenu = document.getElementById("side-menu");

  const PC_WIDTH = "16rem"; 
  let isOpen = false;

  if (!menuBtn || !sideMenu) return;

  const openMenu = () => {
    if (window.innerWidth < 640) {
      sideMenu.style.width = "100vw";
    } else {
      sideMenu.style.width = PC_WIDTH;
    }
    menuBtn.textContent = "⛌";
    menuBtn.classList.add("rotate-90");
    isOpen = true;
  };

  const closeMenu = () => {
    sideMenu.style.width = "0";
    menuBtn.textContent = "☰";
    menuBtn.classList.remove("rotate-90");
    isOpen = false;
  };

  menuBtn.addEventListener("click", (e) => {
    e.stopPropagation(); 
    isOpen ? closeMenu() : openMenu();
  });

  document.addEventListener("click", (e) => {
    if (!menuBtn.contains(e.target) && !sideMenu.contains(e.target)) {
      closeMenu();
    }
  });

  window.addEventListener("resize", () => {
    if (isOpen) openMenu();
  });
});