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
const aviso = document.getElementById("aviso-explorador");
const seletores = { fenomeno, indicador, recorte };
let linhasAtuais = [];

function criarLinha(uf, valor, maximo) {
  const linha = document.createElement("li");
  if (sul.includes(uf)) linha.className = "barra-sul";

  const nome = document.createElement("span");
  nome.className = "barra-nome";
  nome.textContent = ufs[uf];
  if (sul.includes(uf) && recorte.value === "brasil") {
    const selo = document.createElement("span");
    selo.className = "selo-sul";
    selo.textContent = "Sul";
    nome.append(" ", selo);
  }

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
  linhasAtuais = linhas;
  const maximo = linhas[0][1];
  const lideres = linhas.filter(([, valor]) => valor === maximo).map(([uf]) => ufs[uf]);
  barras.replaceChildren(...linhas.map(([uf, valor]) => criarLinha(uf, valor, maximo)));
  resumo.textContent = maximo
    ? `${indicador.selectedOptions[0].textContent} · Maior total: ${lideres.join(", ")} (${numero.format(maximo)}).`
    : `${indicador.selectedOptions[0].textContent} · Sem valores positivos no recorte selecionado.`;
}

function lerEndereco() {
  const parametros = new URLSearchParams(location.search);
  for (const [nome, controle] of Object.entries(seletores)) {
    const valor = parametros.get(nome);
    if (valor && [...controle.options].some(opcao => opcao.value === valor)) controle.value = valor;
  }
}

function enderecoAtual() {
  const url = new URL(location.href);
  url.hash = "";
  for (const [nome, controle] of Object.entries(seletores)) url.searchParams.set(nome, controle.value);
  return url;
}

let temporizador = 0;
function avisar(texto, fixo = false) {
  clearTimeout(temporizador);
  aviso.textContent = texto;
  if (!fixo) temporizador = setTimeout(() => { aviso.textContent = ""; }, 4000);
}

async function copiarLink() {
  const endereco = enderecoAtual().href;
  try {
    await navigator.clipboard.writeText(endereco);
    avisar("Link copiado.");
  } catch {
    avisar(`Copie o endereço: ${endereco}`, true);
  }
}

function baixarCsv() {
  const cabecalho = ["Estado", "Sigla", indicador.selectedOptions[0].textContent];
  const corpo = linhasAtuais.map(([uf, valor]) => [ufs[uf], uf, valor]);
  const campo = valor => `"${String(valor).replaceAll('"', '""')}"`;
  const texto = [cabecalho, ...corpo].map(linha => linha.map(campo).join(";")).join("\r\n");
  const arquivo = URL.createObjectURL(new Blob(["\ufeff", texto], { type: "text/csv;charset=utf-8" }));
  const ancora = document.createElement("a");
  ancora.href = arquivo;
  ancora.download = `${fenomeno.value}-${indicador.value}-${recorte.value}.csv`;
  document.body.append(ancora);
  ancora.click();
  ancora.remove();
  setTimeout(() => URL.revokeObjectURL(arquivo), 1000);
}

for (const controle of Object.values(seletores)) {
  controle.addEventListener("change", () => {
    atualizar();
    history.replaceState(null, "", enderecoAtual());
  });
}
document.getElementById("copiar-link").addEventListener("click", copiarLink);
document.getElementById("baixar-csv").addEventListener("click", baixarCsv);
lerEndereco();
atualizar();
painel.hidden = false;
