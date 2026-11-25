"use strict";

const painel = document.getElementById("explorador");
const fenomeno = document.getElementById("fenomeno");
const indicador = document.getElementById("indicador");
const recorte = document.getElementById("recorte");
const barras = document.getElementById("barras");
const resumo = document.getElementById("resumo-grafico");
const { ufs, sul, grupos } = JSON.parse(document.getElementById("dados-explorador").textContent);
const numero = new Intl.NumberFormat("pt-BR");
const compararNomes = new Intl.Collator("pt-BR");

function criarLinha(uf, valor, maximo) {
  const linha = document.createElement("li");
  if (sul.includes(uf)) linha.className = "barra-sul";

  const nome = document.createElement("span");
  nome.className = "barra-nome";
  nome.textContent = ufs[uf];

  const eixo = document.createElement("span");
  eixo.className = "barra-eixo";
  eixo.setAttribute("aria-hidden", "true");
  const medida = document.createElement("span");
  medida.style.width = maximo > 0 ? `${100 * valor / maximo}%` : "0%";
  eixo.append(medida);

  const total = document.createElement("strong");
  total.textContent = numero.format(valor);
  linha.append(nome, eixo, total);
  return linha;
}

function atualizar() {
  const grupo = grupos[fenomeno.value];
  const chave = indicador.value;
  const siglas = recorte.value === "sul" ? sul : Object.keys(ufs);
  const linhas = siglas.map(uf => [uf, grupo[uf][chave]]);
  linhas.sort(([ufA, valorA], [ufB, valorB]) => valorB - valorA || compararNomes.compare(ufs[ufA], ufs[ufB]));
  const maximo = linhas[0][1];
  const lideres = linhas.filter(([, valor]) => valor === maximo).map(([uf]) => ufs[uf]);
  barras.replaceChildren(...linhas.map(([uf, valor]) => criarLinha(uf, valor, maximo)));
  resumo.textContent = maximo
    ? `${indicador.selectedOptions[0].textContent} · Maior total: ${lideres.join(", ")} (${numero.format(maximo)}).`
    : `${indicador.selectedOptions[0].textContent} · Sem valores positivos no recorte selecionado.`;
}

for (const controle of [fenomeno, indicador, recorte]) {
  controle.addEventListener("change", atualizar);
}
atualizar();
painel.hidden = false;
