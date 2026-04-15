function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);

    const closedEye = button.querySelector(".closed-eye");
    const openEye = button.querySelector(".open-eye");

    if (input.type === "password") {
        input.type = "text";
        closedEye.classList.add("hidden");
        openEye.classList.remove("hidden");
    } else {
        input.type = "password";
        closedEye.classList.remove("hidden");
        openEye.classList.add("hidden");
    }
}