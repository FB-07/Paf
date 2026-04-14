let buffer = "";

document.addEventListener("keydown", (e) => {
  buffer += e.key.toLowerCase();

  buffer = buffer.slice(-5);

  if (buffer.endsWith("admin")) {
    window.location.href = "/admin";
  }
  /*
  if (buffer.endsWith("home") || buffer.endsWith("back")) {
    window.location.href = "/";
  }
  */
});