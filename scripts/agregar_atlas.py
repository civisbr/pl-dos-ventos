"""Agrega a edição 1991–2025 do CSV oficial do Atlas Digital de Desastres."""

import argparse
import csv
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

METRICAS = {
    "atingidos": "DH_total_danos_humanos_diretos",
    "moradias_danificadas": "DM_Uni Habita Danificadas",
    "moradias_destruidas": "DM_Uni Habita Destruidas",
}
GRUPOS = {"Vendavais e Ciclones": "vendavais_ciclones", "Tornado": "tornados"}
SIGLAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}
PRIMEIRO_ANO, ULTIMO_ANO = 1991, 2025


def inteiro(linha, numero, coluna):
    try:
        return int(linha[coluna] or 0)
    except ValueError as erro:
        raise ValueError(f"linha {numero}: valor inválido em {coluna}") from erro


def agregar(origem, edicao, sha256):
    base = {grupo: defaultdict(lambda: defaultdict(int)) for grupo in GRUPOS.values()}
    for numero, linha in enumerate(csv.DictReader(origem, delimiter=";"), start=2):
        grupo = GRUPOS.get((linha["descricao_tipologia"] or "").strip())
        if not grupo:
            continue
        if None in linha.values() or linha.get(None) or not linha["Data_Evento"].strip():
            raise ValueError(f"linha {numero}: registro incompleto ou CSV malformado")
        texto_ano = linha["Data_Evento"].strip().split("/")[-1]
        if not re.fullmatch(r"\d{4}", texto_ano):
            raise ValueError(f"linha {numero}: data inválida ({linha['Data_Evento']!r})")
        ano = int(texto_ano)
        if not PRIMEIRO_ANO <= ano <= ULTIMO_ANO:
            continue
        uf = linha["Sigla_UF"].strip().upper()
        if uf not in SIGLAS:
            raise ValueError(f"linha {numero}: sigla de UF inválida ({uf!r})")
        destino = base[grupo][uf]
        destino["ocorrencias"] += 1
        for chave, coluna in METRICAS.items():
            destino[chave] += inteiro(linha, numero, coluna)
        if inteiro(linha, numero, METRICAS["moradias_danificadas"]) or inteiro(linha, numero, METRICAS["moradias_destruidas"]):
            destino["registros_com_moradias"] += 1
    for grupo, dados in base.items():
        if not dados:
            raise ValueError(f"nenhum registro encontrado para {grupo}")
    chaves = ["ocorrencias", *METRICAS, "registros_com_moradias"]
    return {
        "edicao": edicao,
        "sha256_csv": sha256,
        "grupos": {
            grupo: {uf: {chave: dados[uf][chave] for chave in chaves} for uf in sorted(SIGLAS)}
            for grupo, dados in base.items()
        },
    }


def gravar(caminho, saida):
    """Troca o arquivo só no fim, para uma falha não deixar o JSON vazio."""
    caminho = Path(caminho)
    descritor, temporario = tempfile.mkstemp(dir=caminho.parent, suffix=".tmp")
    try:
        os.fchmod(descritor, 0o644)
        with os.fdopen(descritor, "w", encoding="utf-8") as arquivo:
            json.dump(saida, arquivo, ensure_ascii=False, indent=2)
            arquivo.write("\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    except BaseException:
        Path(temporario).unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--edicao", required=True, help='ex.: "1991–2025 · v1.1 · 06/08/2026"')
    parser.add_argument("--saida", type=Path, default=Path(__file__).resolve().parents[1] / "dados/impactos.json")
    args = parser.parse_args()
    with args.csv.open("rb") as arquivo:
        sha256 = hashlib.file_digest(arquivo, "sha256").hexdigest()
    with args.csv.open(encoding="cp1252", newline="") as origem:
        saida = agregar(origem, args.edicao, sha256)
    gravar(args.saida, saida)


if __name__ == "__main__":
    main()
