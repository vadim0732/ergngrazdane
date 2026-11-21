document.addEventListener("DOMContentLoaded", () => {
  const toasts = document.getElementById("toasts");
  if (!toasts) return;
  setTimeout(() => {
    toasts.style.transition = "opacity .4s";
    toasts.style.opacity = "0";
    setTimeout(() => toasts.remove(), 400);
  }, 3500);
});
