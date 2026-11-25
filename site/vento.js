"use strict";

const canvas = document.getElementById("vento-canvas");
const ctx = canvas.getContext("2d");
const controles = document.getElementById("controles-vento");
const direcao = document.getElementById("direcao");
const intensidade = document.getElementById("intensidade");
const movimento = document.getElementById("movimento");
const reducao = window.matchMedia("(prefers-reduced-motion: reduce)");
const rosa = ["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste"];
const niveis = ["Suave", "Moderada", "Forte"];
let parado = true;
let quadro = 0;
let tempo = 0;
let anterior = 0;
let largura = 0;
let altura = 0;

function desenhar() {
  if (!largura || !altura) return;
  ctx.clearRect(0, 0, largura, altura);
  ctx.save();
  ctx.translate(largura / 2, altura / 2);
  ctx.rotate(Number(direcao.value) * Math.PI / 4 + Math.PI / 2);
  const alcance = Math.hypot(largura, altura);
  const passo = Math.max(13, altura / 14);
  const forca = Number(intensidade.value) + 1;
  const raio = altura * .28;

  for (let linha = -Math.ceil(alcance / passo); linha <= alcance / passo; linha++) {
    const y = linha * passo;
    ctx.beginPath();
    for (let x = -alcance; x <= alcance; x += 5) {
      const curva = Math.exp(-((x / raio) ** 2 + (y / raio) ** 2)) * (y < 0 ? -1 : 1) * forca * 15;
      const onda = Math.sin(x / 65 - tempo + linha * .35) * (3 + forca);
      const posY = y + curva + onda;
      if (x === -alcance) ctx.moveTo(x, posY);
      else ctx.lineTo(x, posY);
    }
    const destaque = linha % 4 === 0;
    ctx.strokeStyle = destaque ? "#245d84" : "#6b99b7";
    ctx.globalAlpha = destaque ? .96 : .76;
    ctx.lineWidth = destaque ? 1.55 : 1;
    if (destaque) {
      ctx.setLineDash([2, 5, 28, 5]);
      ctx.lineDashOffset = -tempo * (6 + forca);
    } else {
      ctx.setLineDash([]);
    }
    ctx.stroke();
  }
  ctx.restore();

  const x = largura / 2;
  const y = altura / 2;
  ctx.fillStyle = "#edf5fa";
  ctx.strokeStyle = "#245d84";
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.arc(x, y, 11, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x - 4, y);
  ctx.lineTo(x + 4, y);
  ctx.moveTo(x, y - 4);
  ctx.lineTo(x, y + 4);
  ctx.stroke();
}

function animar(agora) {
  if (anterior) tempo += Math.min(agora - anterior, 32) * (Number(intensidade.value) + 1) / 2200;
  anterior = agora;
  desenhar();
  quadro = requestAnimationFrame(animar);
}

function ajustarMovimento() {
  cancelAnimationFrame(quadro);
  anterior = 0;
  movimento.textContent = parado ? "Animar o vento" : "Pausar movimento";
  if (!parado) quadro = requestAnimationFrame(animar);
  else desenhar();
}

function atualizarControles() {
  const origem = rosa[Number(direcao.value)];
  const nivel = niveis[Number(intensidade.value)];
  document.getElementById("direcao-atual").value = origem;
  document.getElementById("intensidade-atual").value = nivel;
  direcao.setAttribute("aria-valuetext", origem);
  intensidade.setAttribute("aria-valuetext", nivel);
  desenhar();
}

if (ctx) {
  controles.hidden = false;
  new ResizeObserver(() => {
    const pixels = Math.min(window.devicePixelRatio || 1, 2);
    largura = canvas.clientWidth;
    altura = canvas.clientHeight;
    canvas.width = Math.round(largura * pixels);
    canvas.height = Math.round(altura * pixels);
    ctx.setTransform(pixels, 0, 0, pixels, 0, 0);
    desenhar();
  }).observe(canvas);
  for (const controle of [direcao, intensidade]) {
    controle.addEventListener("input", atualizarControles);
  }
  movimento.addEventListener("click", () => {
    parado = !parado;
    ajustarMovimento();
  });
  reducao.addEventListener("change", () => {
    if (reducao.matches) {
      parado = true;
      ajustarMovimento();
    }
  });
  atualizarControles();
  ajustarMovimento();
}
