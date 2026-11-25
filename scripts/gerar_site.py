"""Gera o site estático e valida os dados que serão publicados."""

from datetime import date
from html import escape
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "_dist"
UFS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco",
    "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
}
SUL = ("SC", "RS", "PR")
ETAPAS = {
    "registrada": "Sugestão registrada",
    "encaminhada": "Sugestão encaminhada",
    "em_analise": "Em análise",
    "respondida": "Resposta recebida",
    "encerrada": "Manifestação encerrada",
    "proposicao_publicada": "Proposição formal localizada",
    "outra": "Outra movimentação confirmada",
}
METRICAS = {
    "ocorrencias": "Registros",
    "atingidos": "Danos humanos diretos",
    "moradias_danificadas": "Moradias danificadas",
    "moradias_destruidas": "Moradias destruídas",
    "moradias": "Moradias atingidas",
    "registros_com_moradias": "Registros com dano habitacional",
}


def carregar(nome):
    return json.loads((ROOT / "dados" / nome).read_text(encoding="utf-8"))


def numero(valor):
    return f"{valor:,}".replace(",", ".")


def acompanhar(uf, eventos):
    if not isinstance(eventos, list):
        raise ValueError(f"{uf}: a lista de movimentações é obrigatória")

    itens = []
    anterior = date.min
    vistos = set()
    for evento in eventos:
        if set(evento) != {"data", "etapa", "resumo"}:
            raise ValueError(f"{uf}: use somente data, etapa e resumo")
        dia = date.fromisoformat(evento["data"])
        etapa = evento["etapa"]
        resumo = evento["resumo"]
        if dia.isoformat() != evento["data"] or dia < anterior:
            raise ValueError(f"{uf}: use datas AAAA-MM-DD em ordem cronológica")
        if etapa not in ETAPAS or not isinstance(resumo, str) or not 1 <= len(resumo.strip()) <= 320:
            raise ValueError(f"{uf}: etapa inválida ou resumo fora do limite")
        chave = (dia, etapa, resumo.strip())
        if chave in vistos:
            raise ValueError(f"{uf}: movimentação duplicada")
        vistos.add(chave)
        anterior = dia
        itens.append(
            f'<li><time datetime="{dia.isoformat()}">{dia:%d/%m/%Y}</time>'
            f'<strong>{ETAPAS[etapa]}</strong><br>{escape(resumo.strip())}</li>'
        )
    historico = (
        '<ol class="registro">' + "".join(reversed(itens)) + "</ol>"
        if itens else "<p>Sem movimentações confirmadas publicadas.</p>"
    )
    situacao = (
        f'{ETAPAS[eventos[-1]["etapa"]]} · {anterior:%d/%m/%Y}'
        if eventos else "Sem movimentações publicadas"
    )
    return (
        f'<details><summary><span>{UFS[uf]}</span><small>{situacao}</small></summary>'
        f'{historico}</details>'
    )


def tabela(dados, legenda):
    campos = list(METRICAS)
    colunas = "".join(f'<th scope="col">{METRICAS[chave]}</th>' for chave in campos)
    linhas = []
    for uf, valores in dados:
        celulas = "".join(f"<td>{numero(valores[chave])}</td>" for chave in campos)
        classe = ' class="sul"' if uf in SUL else ""
        linhas.append(f'<tr{classe}><th scope="row">{UFS[uf]}</th>{celulas}</tr>')
    return (
        f'<div class="tabela" role="region" aria-label="{legenda}" tabindex="0"><table>'
        f'<caption>{legenda}</caption><thead><tr><th scope="col">Estado</th>{colunas}'
        f'</tr></thead><tbody>{"".join(linhas)}</tbody></table></div>'
    )


def comparacao(dados):
    sul = sorted(((uf, dados[uf]) for uf in SUL), key=lambda item: -item[1]["moradias"])
    brasil = sorted(dados.items(), key=lambda item: (-item[1]["moradias"], item[0]))
    return tabela(sul, "Comparação no Sul") + (
        "<details><summary>Ver todos os estados, por total de moradias atingidas</summary>"
        + tabela(brasil, "Comparação nacional") + "</details>"
    )


def preparar_impactos():
    base = carregar("impactos.json")
    grupos = base["grupos"]
    for dados in grupos.values():
        if set(dados) != set(UFS):
            raise ValueError("Esperados dados das 27 unidades da Federação")
        for valores in dados.values():
            if set(valores) != set(METRICAS) - {"moradias"} or any(
                type(valor) is not int or valor < 0 for valor in valores.values()
            ):
                raise ValueError("Indicadores incompletos ou inválidos")
            valores["moradias"] = valores["moradias_danificadas"] + valores["moradias_destruidas"]
            if valores["registros_com_moradias"] > valores["ocorrencias"]:
                raise ValueError("Registros com dano habitacional excedem o total")
    return grupos


def escrever(nome, substituicoes):
    pagina = (ROOT / "site" / nome).read_text(encoding="utf-8")
    for marcador, html in substituicoes.items():
        if pagina.count(marcador) != 1:
            raise ValueError(f"{nome}: marcador ausente ou duplicado")
        pagina = pagina.replace(marcador, html)
    (DIST / nome).write_text(pagina, encoding="utf-8")


def main():
    eventos = carregar("acompanhamento.json")
    if set(eventos) != set(SUL):
        raise ValueError("A linha do tempo deve conter SC, RS e PR")
    historico = "".join(acompanhar(uf, eventos[uf]) for uf in SUL)
    impactos = preparar_impactos()
    ventos = impactos["vendavais_ciclones"]
    explorador = json.dumps(
        {"ufs": UFS, "sul": SUL, "grupos": impactos},
        ensure_ascii=False, separators=(",", ":"),
    ).replace("<", "\\u003c")

    DIST.mkdir(exist_ok=True)
    escrever("index.html", {
        "@@ACOMPANHAMENTO@@": historico,
        "@@DADOS_EXPLORADOR@@": explorador,
        "@@REGISTROS_SUL@@": numero(sum(ventos[uf]["ocorrencias"] for uf in SUL)),
        "@@REGISTROS_BRASIL@@": numero(sum(dados["ocorrencias"] for dados in ventos.values())),
    })
    escrever("dados.html", {
        "@@DADOS_EXPLORADOR@@": explorador,
        "@@VENTOS@@": comparacao(ventos),
        "@@TORNADOS@@": comparacao(impactos["tornados"]),
    })
    for arquivo in (
        "site/estilos.css", "site/vento.js", "site/explorar.js",
        "docs/minuta-modelo.md", "docs/encaminhamentos.md",
        "dados/metodologia.md", "dados/impactos.json",
    ):
        shutil.copyfile(ROOT / arquivo, DIST / Path(arquivo).name)
    shutil.copytree(ROOT / "site/assets", DIST / "assets", dirs_exist_ok=True)


if __name__ == "__main__":
    main()
