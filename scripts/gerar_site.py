"""Gera o site estático e valida os dados que serão publicados."""

from datetime import date
from html import escape
import json
from pathlib import Path
import re
import shutil

try:
    from scripts.md import converter
except ImportError:
    from md import converter

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
SITE_URL = "https://civisbr.github.io/pl-dos-ventos/"
SUL = ("RS", "SC", "PR")
GRUPOS = {"vendavais_ciclones", "tornados"}
# Texto livre é público: barra o que costuma identificar pessoas ou protocolos.
DADO_PESSOAL = re.compile(
    r"\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2}\b"
    r"|\d{2}[.\s]?\d{3}[.\s]?\d{3}/?\d{4}[-\s]?\d{2}\b"
    r"|\S+@\S+|\barroba\b"
    r"|(?:\+55\s?)?\(?\d{2}\)?[\s-]?9?\d{4}[\s-]?\d{4}\b"
    r"|\b9\d{4}[\s-]?\d{4}\b"
    r"|\b(?:protocolo|processo|sei|nup)\b[\s:nº.o]*[\w./-]*\d{4,}",
    re.IGNORECASE,
)
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "object-src 'none'; base-uri 'none'; form-action 'none'"
)
DOCUMENTOS = {
    "minuta-modelo": ("docs/minuta-modelo.md", "Minuta-modelo de projeto de lei estadual", "Texto-modelo preliminar do programa estadual de reforço preventivo de coberturas contra ventos fortes."),
    "encaminhamentos": ("docs/encaminhamentos.md", "Encaminhamentos estaduais", "Canais, dados locais e mensagem para encaminhar a proposta às Assembleias do RS, SC e PR."),
    "metodologia": ("dados/metodologia.md", "Metodologia dos dados", "Como os registros do Atlas Digital de Desastres foram agregados e quais são os limites da comparação."),
}
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
        if not isinstance(evento["data"], str):
            raise ValueError(f"{uf}: a data deve ser texto AAAA-MM-DD")
        dia = date.fromisoformat(evento["data"])
        etapa = evento["etapa"]
        resumo = evento["resumo"]
        if dia.isoformat() != evento["data"] or dia < anterior:
            raise ValueError(f"{uf}: use datas AAAA-MM-DD em ordem cronológica")
        if etapa not in ETAPAS or not isinstance(resumo, str) or not 1 <= len(resumo.strip()) <= 320:
            raise ValueError(f"{uf}: etapa inválida ou resumo fora do limite")
        if DADO_PESSOAL.search(resumo):
            raise ValueError(f"{uf}: o resumo parece conter dado pessoal ou protocolo")
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
    if not re.fullmatch(r"\d{4}–\d{4} · v\d+(\.\d+)* · \d{2}/\d{2}/\d{4}", str(base.get("edicao"))) or not re.fullmatch(r"[0-9a-f]{64}", str(base.get("sha256_csv"))):
        raise ValueError("impactos.json deve informar edicao (ex.: 1991–2025 · v1.1 · 06/08/2026) e sha256_csv")
    grupos = base["grupos"]
    if set(grupos) != GRUPOS:
        raise ValueError("Os grupos devem ser vendavais_ciclones e tornados")
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
    return base["edicao"], grupos


def cabeca(arquivo, titulo, descricao):
    url = SITE_URL + ("" if arquivo == "index.html" else arquivo)
    titulo, descricao = escape(titulo, quote=True), escape(descricao, quote=True)
    return "\n  ".join([
        f"<title>{titulo}</title>",
        f'<meta name="description" content="{descricao}">',
        f'<meta http-equiv="Content-Security-Policy" content="{CSP}">',
        '<meta name="referrer" content="strict-origin-when-cross-origin">',
        '<meta name="theme-color" content="#f8fbfc">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="pt_BR">',
        '<meta property="og:site_name" content="PL dos Ventos · CivisBR">',
        f'<meta property="og:title" content="{titulo}">',
        f'<meta property="og:description" content="{descricao}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{SITE_URL}assets/logo-ventos-brisa.png">',
        '<meta name="twitter:card" content="summary">',
    ])


MARCADOR = re.compile(r"@@[A-Z_]+@@")


def montar(nome, modelo, substituicoes):
    """Substitui em uma só passada, para um valor inserido não ser expandido de novo."""
    esperados = set(MARCADOR.findall(modelo))
    if esperados != set(substituicoes):
        raise ValueError(f"{nome}: marcadores divergentes {esperados ^ set(substituicoes)}")
    return MARCADOR.sub(lambda achado: substituicoes[achado.group()], modelo)


def escrever(nome, substituicoes, titulo, descricao, saida=None):
    pagina = (ROOT / "site" / nome).read_text(encoding="utf-8")
    substituicoes = {**substituicoes, "@@CABECA@@": cabeca(saida or nome, titulo, descricao)}
    (DIST / (saida or nome)).write_text(montar(nome, pagina, substituicoes), encoding="utf-8")


def main():
    eventos = carregar("acompanhamento.json")
    if set(eventos) != set(SUL):
        raise ValueError("A linha do tempo deve conter SC, RS e PR")
    historico = "".join(acompanhar(uf, eventos[uf]) for uf in SUL)
    edicao, impactos = preparar_impactos()
    periodo = edicao.split(" · ")[0]
    ventos = impactos["vendavais_ciclones"]
    explorador = json.dumps(
        {"ufs": UFS, "sul": SUL, "grupos": impactos},
        ensure_ascii=False, separators=(",", ":"),
    ).replace("<", "\\u003c")
    comuns = {"@@PERIODO@@": escape(periodo), "@@EDICAO@@": escape(edicao)}
    sul_ventos = sorted(((uf, ventos[uf]) for uf in SUL), key=lambda item: -item[1]["moradias"])

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    escrever("index.html", {
        **comuns,
        "@@ACOMPANHAMENTO@@": historico,
        "@@DADOS_EXPLORADOR@@": explorador,
        "@@REGISTROS_SUL@@": numero(sum(ventos[uf]["ocorrencias"] for uf in SUL)),
        "@@REGISTROS_BRASIL@@": numero(sum(dados["ocorrencias"] for dados in ventos.values())),
        "@@MORADIAS_SUL@@": numero(sum(ventos[uf]["moradias"] for uf in SUL)),
        "@@TABELA_SUL@@": tabela(sul_ventos, "Comparação no Sul"),
    }, "PL dos Ventos · CivisBR", "Proposta cidadã de reforço preventivo de coberturas no Sul do Brasil, dados de desastres e acompanhamento das sugestões.")
    escrever("dados.html", {
        **comuns,
        "@@DADOS_EXPLORADOR@@": explorador,
        "@@VENTOS@@": comparacao(ventos),
        "@@TORNADOS@@": comparacao(impactos["tornados"]),
    }, "Dados de desastres por vento · PL dos Ventos", f"Compare registros de vendavais, ciclones e tornados e seus danos humanos e habitacionais por estado, de {periodo}.")
    for stem, (origem, titulo, descricao) in DOCUMENTOS.items():
        escrever("documento.html", {
            "@@CONTEUDO@@": converter((ROOT / origem).read_text(encoding="utf-8")),
            "@@ORIGEM@@": Path(origem).name,
        }, f"{titulo} · PL dos Ventos", descricao, saida=f"{stem}.html")
    for arquivo in (
        "site/estilos.css", "site/vento.js", "site/explorar.js",
        "docs/minuta-modelo.md", "docs/encaminhamentos.md",
        "dados/metodologia.md", "dados/impactos.json",
    ):
        shutil.copyfile(ROOT / arquivo, DIST / Path(arquivo).name)
    shutil.copytree(
        ROOT / "site/assets", DIST / "assets", dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("icone-ventos-brisa.png"),
    )
    paginas = ["", "dados.html", *(f"{stem}.html" for stem in DOCUMENTOS)]
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{SITE_URL}{pagina}</loc></url>\n" for pagina in paginas)
        + "</urlset>\n", encoding="utf-8",
    )
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    main()
