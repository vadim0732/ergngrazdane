(() => {
  const root = document.getElementById("slider");
  if (!root) return;

  const slides = [...root.querySelectorAll(".slide")];
  const dotsBox = document.getElementById("dots");
  let i = 0;

  slides.forEach((_, idx) => {
    const b = document.createElement("button");
    b.type = "button";
    b.setAttribute("aria-label", `Слайд ${idx + 1}`);
    b.addEventListener("click", () => show(idx));
    dotsBox.appendChild(b);
  });

  const dots = [...dotsBox.querySelectorAll("button")];

  function show(n) {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, idx) => s.classList.toggle("active", idx === i));
    dots.forEach((d, idx) => d.classList.toggle("active", idx === i));
  }

  root.querySelectorAll(".slider-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      show(i + Number(btn.dataset.dir));
    });
  });

  show(0);
  setInterval(() => show(i + 1), 3000);
})();
