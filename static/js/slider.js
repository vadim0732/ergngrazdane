(function () {
  const slider = document.getElementById("slider");
  if (!slider) return;

  const slides = slider.querySelectorAll(".slides img");
  const dotsWrap = slider.querySelector("#dots");
  const prevBtn = slider.querySelector(".slider-btn.prev");
  const nextBtn = slider.querySelector(".slider-btn.next");

  if (slides.length === 0) return;

  let current = 0;
  let timer = null;
  const INTERVAL = 3000; // 3 секунды — как в задании

  // Точки
  const dots = [];
  if (dotsWrap) {
    slides.forEach((_, i) => {
      const dot = document.createElement("span");
      if (i === 0) dot.classList.add("active");
      dot.addEventListener("click", () => goTo(i));
      dotsWrap.appendChild(dot);
      dots.push(dot);
    });
  }

  function render() {
    slides.forEach((img, i) => {
      img.classList.toggle("active", i === current);
    });
    dots.forEach((d, i) => {
      d.classList.toggle("active", i === current);
    });
  }

  function goTo(index) {
    current = (index + slides.length) % slides.length;
    render();
    restart();
  }

  function next() { goTo(current + 1); }
  function prev() { goTo(current - 1); }

  function start() {
    stop();
    timer = setInterval(next, INTERVAL);
  }
  function stop() {
    if (timer) { clearInterval(timer); timer = null; }
  }
  function restart() { start(); }

  if (prevBtn) prevBtn.addEventListener("click", prev);
  if (nextBtn) nextBtn.addEventListener("click", next);

  // Пауза при наведении — приятный бонус
  slider.addEventListener("mouseenter", stop);
  slider.addEventListener("mouseleave", start);

  // Первый слайд сразу видим
  render();
  start();
})();