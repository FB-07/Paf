let buffer = [];

document.addEventListener("keydown", (e) => {
  buffer.push(e.key);
  
  if (buffer.length > 9) buffer.shift();

  const sequence = [
    "ArrowUp",
    "ArrowUp",
    "ArrowDown",
    "ArrowDown",
    "a",
    "d",
    "m",
    "i",
    "n"
  ];

  if (buffer.join(",") === sequence.join(",")) {
    window.location.href = "/admin";
  }
});