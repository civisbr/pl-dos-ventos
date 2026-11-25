import io
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import agregar_atlas
import gerar_site
from md import converter

RAIZ = Path(__file__).resolve().parents[1]
CABECALHO = "Sigla_UF;Data_Evento;descricao_tipologia;DH_total_danos_humanos_diretos;DM_Uni Habita Danificadas;DM_Uni Habita Destruidas\n"


def evento(**campos):
    return {"data": "2027-01-15", "etapa": "encaminhada", "resumo": "Sugestão encaminhada ao setor legislativo.", **campos}


class Acompanhamento(unittest.TestCase):
    def test_escapa_html_do_resumo(self):
        html = gerar_site.acompanhar("RS", [evento(resumo="<b>x</b>")])
        self.assertIn("&lt;b&gt;", html)
        self.assertNotIn("<b>", html)

    def test_rejeita_dado_pessoal(self):
        casos = (
            "CPF 123.456.789-09", "CPF 123 456 789 01", "CNPJ 12.345.678/0001-90", "contato a@b.com",
            "fulano arroba gmail", "ligar (51) 99876-5432", "ligar (51) 3333 4444", "ligar 99999-9999",
            "+55 51 99876-5432", "Protocolo nº 2026/12345", "protocolo: 2024/123456", "processo SEI 12345",
        )
        for resumo in casos:
            with self.subTest(resumo=resumo), self.assertRaises(ValueError):
                gerar_site.acompanhar("RS", [evento(resumo=resumo)])

    def test_aceita_periodo_com_hifen(self):
        gerar_site.acompanhar("RS", [evento(resumo="Dados de 1991-2025 conferidos.")])

    def test_rejeita_data_desordenada_duplicada_e_nao_texto(self):
        with self.assertRaises(ValueError):
            gerar_site.acompanhar("RS", [evento(), evento(data="2027-01-01")])
        with self.assertRaises(ValueError):
            gerar_site.acompanhar("RS", [evento(), evento()])
        with self.assertRaises(ValueError):
            gerar_site.acompanhar("RS", [evento(data=20270115)])

    def test_rejeita_etapa_e_campos_extras(self):
        with self.assertRaises(ValueError):
            gerar_site.acompanhar("RS", [evento(etapa="inventada")])
        with self.assertRaises(ValueError):
            gerar_site.acompanhar("RS", [{**evento(), "extra": 1}])


class Montagem(unittest.TestCase):
    def test_marcadores_divergentes_falham(self):
        with self.assertRaises(ValueError):
            gerar_site.montar("x", "@@A@@ @@B@@", {"@@A@@": "1"})

    def test_valor_inserido_nao_e_expandido(self):
        self.assertEqual(gerar_site.montar("x", "@@A@@ @@B@@", {"@@A@@": "@@B@@", "@@B@@": "2"}), "@@B@@ 2")

    def test_cabeca_escapa_e_traz_csp(self):
        html = gerar_site.cabeca("index.html", 'T"<x>', 'D"<y>')
        self.assertNotIn("<x>", html)
        self.assertIn("Content-Security-Policy", html)
        self.assertIn('rel="canonical"', html)

    def test_site_gerado(self):
        gerar_site.main()
        dist = gerar_site.DIST
        for arquivo in dist.glob("*.html"):
            texto = arquivo.read_text(encoding="utf-8")
            self.assertNotRegex(texto, r"@@[A-Z_]+@@", arquivo.name)
            self.assertIn("Content-Security-Policy", texto, arquivo.name)
        self.assertIn("sitemap.xml", (dist / "robots.txt").read_text())
        self.assertIn("<urlset", (dist / "sitemap.xml").read_text())


class Impactos(unittest.TestCase):
    def test_dados_publicados_sao_validos(self):
        edicao, grupos = gerar_site.preparar_impactos()
        self.assertTrue(edicao)
        self.assertEqual(set(grupos), {"vendavais_ciclones", "tornados"})


class Markdown(unittest.TestCase):
    def test_escapa_e_converte(self):
        html = converter("# T <i>\n\n**negrito** e [link](https://exemplo.org)\n\n- a\n- b")
        self.assertIn("<h1>T &lt;i&gt;</h1>", html)
        self.assertIn("<strong>negrito</strong>", html)
        self.assertIn('<a href="https://exemplo.org">link</a>', html)
        self.assertIn("<li>b</li>", html)

    def test_lista_numerada(self):
        html = converter("1. um\n2. [dois](https://exemplo.org)\n\ntexto")
        self.assertIn("<ol><li>um</li><li><a", html)
        self.assertIn("<p>texto</p>", html)
        self.assertNotIn("<ol>", converter("2013. Depois do tornado"))

    def test_rejeita_link_perigoso(self):
        with self.assertRaises(ValueError):
            converter("[x](javascript:alert(1))")

    def test_titulo_profundo_e_tabela_sem_separador(self):
        self.assertIn("<h6>x</h6>", converter("####### x"))
        with self.assertRaises(ValueError):
            converter("| a | b |\n| 1 | 2 |")

    def test_link_para_metodologia(self):
        self.assertIn('href="metodologia.html"', converter("[m](../dados/metodologia.md)"))


class Agregacao(unittest.TestCase):
    def agregar(self, linhas):
        return agregar_atlas.agregar(io.StringIO(CABECALHO + linhas), "ed", "0" * 64)

    def test_soma_por_uf_e_grupo(self):
        saida = self.agregar(
            "RS;01/02/2020;Vendavais e Ciclones;3;2;1\n"
            "RS;01/02/2021;Tornado;0;0;0\n"
            "SC;01/02/1990;Tornado;9;9;9\n"
        )
        ventos = saida["grupos"]["vendavais_ciclones"]["RS"]
        self.assertEqual((ventos["ocorrencias"], ventos["atingidos"], ventos["registros_com_moradias"]), (1, 3, 1))
        self.assertEqual(saida["grupos"]["tornados"]["SC"]["ocorrencias"], 0)

    def test_falha_com_sigla_invalida_ou_valor_ruim(self):
        with self.assertRaises(ValueError):
            self.agregar("XX;01/02/2020;Vendavais e Ciclones;1;1;1\nRS;01/02/2020;Tornado;0;0;0\n")
        with self.assertRaises(ValueError):
            self.agregar("RS;01/02/2020;Vendavais e Ciclones;x;1;1\nRS;01/02/2020;Tornado;0;0;0\n")

    def test_falha_com_linha_truncada_e_ano_de_dois_digitos(self):
        with self.assertRaises(ValueError):
            self.agregar("RS;01/02/2020;Vendavais e Ciclones\nRS;01/02/2020;Tornado;0;0;0\n")
        with self.assertRaises(ValueError):
            self.agregar("RS;01/02/20;Vendavais e Ciclones;1;1;1\nRS;01/02/2020;Tornado;0;0;0\n")

    def test_falha_sem_registros_de_um_grupo(self):
        with self.assertRaises(ValueError):
            self.agregar("RS;01/02/2020;Vendavais e Ciclones;1;1;1\n")

    def test_gravacao_atomica(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "saida.json"
            destino.write_text("{}")
            agregar_atlas.gravar(destino, {"a": 1})
            self.assertEqual(json.loads(destino.read_text()), {"a": 1})
            self.assertEqual(list(Path(pasta).iterdir()), [destino])


class FontesExternas(unittest.TestCase):
    def setUp(self):
        site = (RAIZ / "site" / "index.html").read_text(encoding="utf-8")
        self.links_site = []
        self.links_por_secao = {}
        for secao in ("experiencia", "normas"):
            inicio = site.index(f'<section id="{secao}"')
            links = re.findall(r'href="([^"]+)"', site[inicio:site.index("</section>", inicio)])
            self.links_por_secao[secao] = links
            self.links_site += links
        minuta = (RAIZ / "docs" / "minuta-modelo.md").read_text(encoding="utf-8")
        self.referencias = minuta[minuta.index("## Referências"):]

    def test_secao_tem_links(self):
        self.assertGreaterEqual(len(self.links_por_secao["experiencia"]), 4)
        self.assertGreaterEqual(len(self.links_por_secao["normas"]), 2)

    def test_links_do_site_sao_https(self):
        for link in self.links_site:
            self.assertTrue(link.startswith("https://"), link)

    def test_links_do_site_estao_nas_referencias_da_minuta(self):
        for link in self.links_site:
            self.assertIn(link, self.referencias)

    def test_citacoes_da_justificacao_tem_referencia(self):
        minuta = (RAIZ / "docs" / "minuta-modelo.md").read_text(encoding="utf-8")
        citadas = set(re.findall(r"\[(\d+)\]", minuta[:minuta.index("## Referências")]))
        listadas = set(re.findall(r"^(\d+)\. ", self.referencias, flags=re.M))
        self.assertEqual(citadas, listadas)
        self.assertEqual(sorted(listadas, key=int), [str(n) for n in range(1, len(listadas) + 1)])


if __name__ == "__main__":
    unittest.main()
