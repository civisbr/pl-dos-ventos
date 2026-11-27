"use strict";

// Bloco próprio: os scripts clássicos compartilham o escopo global, e explorar.js também define atualizar().
{
  // O campo de vento é decorativo, mas anima por mais de cinco segundos: só anima com este script,
  // que oferece a pausa (WCAG 2.2.2), e nunca com redução de movimento ativa.
  const botao = document.getElementById("movimento");
  const reducao = window.matchMedia("(prefers-reduced-motion: reduce)");
  const raiz = document.documentElement;

  function atualizar() {
    const pausado = botao.getAttribute("aria-pressed") === "true";
    raiz.classList.toggle("vento-ativo", !reducao.matches);
    raiz.classList.toggle("vento-parado", pausado);
    botao.hidden = reducao.matches;
  }

  if (botao) {
    botao.addEventListener("click", () => {
      botao.setAttribute("aria-pressed", String(botao.getAttribute("aria-pressed") !== "true"));
      atualizar();
    });
    reducao.addEventListener("change", atualizar);
    atualizar();
  }
}
