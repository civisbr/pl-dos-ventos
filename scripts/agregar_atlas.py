"""Agrega a edição 1991–2025 do CSV oficial do Atlas Digital de Desastres."""

import argparse
import csv
from collections import defaultdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path

METRICAS = {
    "atingidos": "DH_total_danos_humanos_diretos",
    "moradias_danificadas": "DM_Uni Habita Danificadas",
    "moradias_destruidas": "DM_Uni Habita Destruidas",
}
GRUPOS = {"Vendavais e Ciclones": "vendavais_ciclones", "Tornado": "tornados"}

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("csv", type=Path)
args = parser.parse_args()

ufs = defaultdict(lambda: defaultdict(int))
base = {grupo: defaultdict(lambda: defaultdict(int)) for grupo in GRUPOS.values()}
with args.csv.open(encoding="cp1252", newline="") as origem:
    for linha in csv.DictReader(origem, delimiter=";"):
        uf = linha["Sigla_UF"].strip().upper()
        if len(uf) == 2:
            ufs[uf]
        grupo = GRUPOS.get(linha["descricao_tipologia"])
        if not grupo:
            continue
        if not linha["Data_Evento"] or linha.get(None) or linha["PE_PLePR"] is None:
            raise ValueError("Registro incompleto ou CSV malformado")
        ano = int(linha["Data_Evento"][-4:])
        if not 1991 <= ano <= 2025:
            continue
        destino = base[grupo][uf]
        destino["ocorrencias"] += 1
        for chave, coluna in METRICAS.items():
            destino[chave] += int(linha[coluna] or 0)
        if int(linha[METRICAS["moradias_danificadas"]] or 0) or int(linha[METRICAS["moradias_destruidas"]] or 0):
            destino["registros_com_moradias"] += 1

chaves = ["ocorrencias", *METRICAS, "registros_com_moradias"]
saida = {
    "edicao": "1991–2025 · v1.1 · 06/08/2026",
    "sha256_csv": hashlib.file_digest(args.csv.open("rb"), "sha256").hexdigest(),
    "grupos": {
        grupo: {uf: {chave: dados[uf][chave] for chave in chaves} for uf in sorted(ufs)}
        for grupo, dados in base.items()
    },
}
print(json.dumps(saida, ensure_ascii=False, indent=2))
