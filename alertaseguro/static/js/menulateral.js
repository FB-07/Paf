document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.getElementById("menu-btn");
  const sideMenu = document.getElementById("side-menu");
  const mainContent = document.getElementById("main-content");

  const MENU_WIDTH = "16rem";
  let isOpen = false;

  if (!menuBtn || !sideMenu) return;

  const openMenu = () => {
    sideMenu.style.width = MENU_WIDTH;

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

  menuBtn.addEventListener("click", () => {
    isOpen ? closeMenu() : openMenu();
  });
});
