document.addEventListener("DOMContentLoaded", () => {
  const showMessage = (msg, color = "#28a745") => {
    const box = document.createElement("div");
    box.textContent = msg;
    Object.assign(box.style, {
      position: "fixed",
      top: "20px",
      left: "50%",
      transform: "translateX(-50%)",
      backgroundColor: color,
      color: "#fff",
      padding: "12px 20px",
      borderRadius: "8px",
      fontWeight: "bold",
      boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
      zIndex: "9999",
      opacity: "0",
      transition: "opacity 0.3s ease-in-out",
    });
    document.body.appendChild(box);
    requestAnimationFrame(() => (box.style.opacity = "1"));
    setTimeout(() => {
      box.style.opacity = "0";
      setTimeout(() => box.remove(), 300);
    }, 2000);
  };

  const highlightInvalid = (field) => {
    field.style.borderColor = "red";
    setTimeout(() => (field.style.borderColor = "#ccc"), 1500);
  };

  const produtoForm = document.querySelector('form[action="/produtos"]');
  if (produtoForm) {
    produtoForm.addEventListener("submit", (e) => {
      const nome = produtoForm.querySelector("#nome");
      const categoria = produtoForm.querySelector("#categoria");
      const precoCompra = produtoForm.querySelector("#preco_compra");
      const precoRevenda = produtoForm.querySelector("#preco_revenda");
      const quantidade = produtoForm.querySelector("#quantidade");

      let erro = false;

      if (!nome.value.trim()) { highlightInvalid(nome); erro = true; }
      if (!categoria.value.trim()) { highlightInvalid(categoria); erro = true; }
      if (!precoCompra.value || precoCompra.value <= 0) { highlightInvalid(precoCompra); erro = true; }
      if (!precoRevenda.value || precoRevenda.value <= 0) { highlightInvalid(precoRevenda); erro = true; }
      if (!quantidade.value || quantidade.value <= 0) { highlightInvalid(quantidade); erro = true; }

      if (erro) {
        e.preventDefault();
        showMessage("Preencha todos os campos corretamente.", "#d9534f");
        return;
      }

      if (parseFloat(precoRevenda.value) <= parseFloat(precoCompra.value)) {
        e.preventDefault();
        highlightInvalid(precoRevenda);
        showMessage("Preço de revenda deve ser maior que o preço de compra.", "#d9534f");
        return;
      }

      showMessage("Produto cadastrado com sucesso!");
    });
  }

  const funcionarioForm = document.querySelector('form[action="/funcionarios"]');
  if (funcionarioForm) {
    funcionarioForm.addEventListener("submit", (e) => {
      const nome = funcionarioForm.querySelector("#nome");
      if (!nome.value.trim()) {
        e.preventDefault();
        highlightInvalid(nome);
        showMessage("Preencha o nome do funcionário.", "#d9534f");
        return;
      }
      showMessage("Funcionário cadastrado!");
    });
  }

  document.addEventListener("click", (e) => {
    const menuToggleBtn = document.querySelector("#menu-toggle");
    const sideMenu = document.querySelector(".side-menu");

    if (menuToggleBtn && sideMenu) {
      if (e.target === menuToggleBtn || menuToggleBtn.contains(e.target)) {
        sideMenu.classList.toggle("menu-aberto");
      } else if (!sideMenu.contains(e.target)) {
        sideMenu.classList.remove("menu-aberto");
      }
    }
  });
});

