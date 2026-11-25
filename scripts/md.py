"""Conversor mínimo de Markdown para HTML, restrito ao que os documentos do projeto usam."""

from html import escape
import re

LINK_INTERNO = {
    "../dados/metodologia.md": "metodologia.html",
    "impactos.json": "impactos.json",
}
INLINE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)\s]+)\)")


def destino(url):
    url = LINK_INTERNO.get(url, url)
    if not re.match(r"(https://|[\w.-]+\.(html|json)$)", url):
        raise ValueError(f"Link não permitido: {url}")
    return escape(url, quote=True)


def inline(texto):
    saida, posicao = [], 0
    for achado in INLINE.finditer(texto):
        saida.append(escape(texto[posicao:achado.start()]))
        negrito, codigo, rotulo, url = achado.groups()
        if negrito is not None:
            saida.append(f"<strong>{escape(negrito)}</strong>")
        elif codigo is not None:
            saida.append(f"<code>{escape(codigo)}</code>")
        else:
            saida.append(f'<a href="{destino(url)}">{escape(rotulo)}</a>')
        posicao = achado.end()
    saida.append(escape(texto[posicao:]))
    return "".join(saida)


def celulas(linha):
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def converter(texto):
    linhas = texto.splitlines()
    blocos, i = [], 0
    while i < len(linhas):
        linha = linhas[i]
        if not linha.strip():
            i += 1
        elif linha.startswith("```"):
            i += 1
            codigo = []
            while i < len(linhas) and not linhas[i].startswith("```"):
                codigo.append(linhas[i])
                i += 1
            i += 1
            blocos.append(f"<pre><code>{escape(chr(10).join(codigo))}</code></pre>")
        elif linha.startswith("#"):
            marcas = len(linha) - len(linha.lstrip("#"))
            nivel = min(marcas, 6)
            blocos.append(f"<h{nivel}>{inline(linha[marcas:].strip())}</h{nivel}>")
            i += 1
        elif linha.startswith("|"):
            tabela = []
            while i < len(linhas) and linhas[i].startswith("|"):
                tabela.append(celulas(linhas[i]))
                i += 1
            if len(tabela) < 2 or not all(set(c) <= set("-: ") for c in tabela[1]):
                raise ValueError("Tabela Markdown sem linha separadora")
            cab, corpo = tabela[0], tabela[2:]
            cabecalho = "".join(f'<th scope="col">{inline(c)}</th>' for c in cab)
            linhas_html = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in linha_tab) + "</tr>"
                for linha_tab in corpo
            )
            blocos.append(
                '<div class="tabela" role="region" tabindex="0" aria-label="Tabela do documento">'
                f"<table><thead><tr>{cabecalho}</tr></thead><tbody>{linhas_html}</tbody></table></div>"
            )
        elif linha.startswith("- "):
            itens = []
            while i < len(linhas) and linhas[i].startswith("- "):
                itens.append(f"<li>{inline(linhas[i][2:])}</li>")
                i += 1
            blocos.append("<ul>" + "".join(itens) + "</ul>")
        elif linha.startswith(">"):
            citacao = []
            while i < len(linhas) and linhas[i].startswith(">"):
                citacao.append(linhas[i][1:].strip())
                i += 1
            paragrafos = _paragrafos(citacao)
            blocos.append("<blockquote>" + "".join(f"<p>{inline(p)}</p>" for p in paragrafos) + "</blockquote>")
        else:
            paragrafo = []
            while i < len(linhas) and linhas[i].strip() and not linhas[i].startswith(("#", "|", "- ", ">", "```")):
                paragrafo.append(linhas[i].strip())
                i += 1
            blocos.append(f"<p>{inline(' '.join(paragrafo))}</p>")
    return "\n".join(blocos)


def _paragrafos(linhas):
    atual, saida = [], []
    for linha in linhas:
        if linha:
            atual.append(linha)
        elif atual:
            saida.append(" ".join(atual))
            atual = []
    if atual:
        saida.append(" ".join(atual))
    return saida
