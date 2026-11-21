(() => {
  const form = document.getElementById("reg-form");
  if (!form) return;

  const rules = {
    login: {
      re: /^[A-Za-z0-9]{6,}$/,
      msg: "Логин: латиница и цифры, не менее 6 символов.",
    },
    password: {
      test: (v) => v.length >= 8,
      msg: "Пароль: минимум 8 символов.",
    },
    full_name: {
      re: /^[А-Яа-яЁё]+(?:\s[А-Яа-яЁё]+)*$/,
      msg: "ФИО: только кириллица и пробелы.",
    },
    phone: {
      re: /^8\(\d{3}\)\d{3}-\d{2}-\d{2}$/,
      msg: "Телефон: 8(XXX)XXX-XX-XX.",
    },
    email: {
      re: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      msg: "Некорректный email.",
    },
  };

  function check(name, value) {
    const rule = rules[name];
    if (!rule) return true;
    if (rule.re) return rule.re.test(value);
    return rule.test(value);
  }

  form.addEventListener("submit", (e) => {
    let ok = true;
    Object.keys(rules).forEach((name) => {
      const input = form.elements[name];
      const err = input.parentElement.querySelector(".field-error");
      const value = (input.value || "").trim();
      if (!check(name, name === "password" ? input.value : value)) {
        ok = false;
        err.textContent = rules[name].msg;
        err.classList.add("show");
      } else if (!err.textContent.includes("занят")) {
        err.classList.remove("show");
      }
    });
    if (!ok) e.preventDefault();
  });
})();
