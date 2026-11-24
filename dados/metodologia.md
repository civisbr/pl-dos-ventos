# Dados de desastres por ventos fortes

**Fonte primária.** Ministério da Integração e do Desenvolvimento Regional (MIDR), Atlas Digital de Desastres no Brasil. [Página de download](https://atlasdigital.mdr.gov.br/paginas/downloads.xhtml) e [arquivo CSV consolidado, versão 1.1, 06/08/2026](https://atlasdigital.mdr.gov.br/arquivos/2026/BD_Atlas_1991_2025_v1.1_2026.08.06_Consolidado.csv). O SHA-256 do arquivo usado consta em [impactos.json](impactos.json).

**Recorte.** Datas de evento entre 1991 e 2025, inclusive. Agregação pela UF do registro e pelos rótulos oficiais “Vendavais e Ciclones” e “Tornado”. Granizo e demais categorias ficam fora. A sigla da UF é normalizada para maiúsculas. Cada linha da base conta como um registro de desastre. Um único fenômeno pode atingir vários municípios e gerar vários registros.

| Indicador | Campo ou cálculo |
| --- | --- |
| Registros | Contagem de linhas por grupo e UF |
| Danos humanos diretos | Soma de `DH_total_danos_humanos_diretos` |
| Moradias danificadas | Soma de `DM_Uni Habita Danificadas` |
| Moradias destruídas | Soma de `DM_Uni Habita Destruidas` |
| Moradias atingidas | Soma dos dois campos de moradias |
| Registros com dano habitacional | Registros com contagem positiva de unidades danificadas ou destruídas |

## Limitações

- São dados administrativos retrospectivos. A comparação por número absoluto não mede frequência meteorológica, taxa por moradia nem risco individual.
- Os danos humanos diretos e habitacionais são somados entre registros. A base não permite deduplicar pessoas ou imóveis.
- Um zero pode refletir ausência de dano ou de informação. A contagem de registros com dano habitacional facilita a leitura, mas não estima cobertura de notificação.
- Os dados habitacionais não isolam danos especificamente em coberturas. Para selecionar imóveis, é necessário combinar um recorte territorial com vistoria.
- A página compara danos registrados em unidades habitacionais. Um ranking de perdas em reais exige recorte monetário próprio e avaliação separada da comparabilidade dos valores.

## Reprodução

Baixe o CSV da edição indicada e, com Python 3.11 ou superior, execute na raiz do repositório:

```sh
python3 scripts/agregar_atlas.py /caminho/para/arquivo.csv > dados/impactos.json
python3 scripts/gerar_site.py
```

Para conferência da série, compare com [Vendavais e ciclones](https://atlassocioeconomico.rs.gov.br/vendavais) e [Tornados](https://atlassocioeconomico.rs.gov.br/tornados), do Atlas Socioeconômico do RS. Revisões, datas de corte e regras de extração podem alterar os totais.
