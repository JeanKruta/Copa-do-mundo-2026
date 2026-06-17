# -*- coding: utf-8 -*-
"""
Lê resultados.csv + equipes.py, calcula a classificação dos participantes
e gera os arquivos públicos dados/classificacao.json e dados/confrontos.json.

O CSV bruto NÃO é publicado: só os JSON calculados vão para produção.
"""
import csv
import json
import os
import sys
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from equipes import equipes

# Mapa país (como escrito em equipes.py) -> código de bandeira do flagcdn.com
PAIS_FLAG = {
    "Uruguai": "uy",
    "Suécia": "se",
    "Austrália": "au",
    "Turquia": "tr",
    "México": "mx",
    "Iraque": "iq",
    "Colômbia": "co",
    "Noruega": "no",
    "Bósnia": "ba",
    "Portugal": "pt",
    "EUA": "us",
    "Cabo Verde": "cv",
    "Suíça": "ch",
    "Arábia Saudita": "sa",
    "Costa do Marfim": "ci",
    "Alemanha": "de",
    "Marrocos": "ma",
    "Canadá": "ca",
    "República Tcheca": "cz",
    "Holanda": "nl",
    "Egito": "eg",
    "Nova Zelândia": "nz",
    "Senegal": "sn",
    "Bélgica": "be",
    "Argentina": "ar",
    "Panamá": "pa",
    "Japão": "jp",
    "Inglaterra": "gb-eng",
    "Áustria": "at",
    "Congo": "cg",
    "Qatar": "qa",
    "Coreia do Sul": "kr",
    "Espanha": "es",
    "África do Sul": "za",
    "Equador": "ec",
    "França": "fr",
    "Brasil": "br",
    "Gana": "gh",
    "Irã": "ir",
    "Croácia": "hr",
    "Tunísia": "tn",
    "Paraguai": "py",
}

CSV_PATH = os.path.join(BASE, "resultados.csv")
SAIDA_DIR = os.path.join(BASE, "..", "docs", "dados")


def erro(msg):
    print(f"ERRO: {msg}")
    sys.exit(1)


def main():
    # País -> dono (participante)
    pais_dono = {}
    for e in equipes:
        for pais in e["paises"]:
            pais_dono[pais] = e["nome"]

    # Garante que todo país tem bandeira mapeada
    sem_flag = sorted(p for p in pais_dono if p not in PAIS_FLAG)
    if sem_flag:
        erro("Países sem bandeira mapeada em gerar.py: " + ", ".join(sem_flag))

    # Estatísticas por participante
    stats = {
        e["nome"]: {
            "nome": e["nome"],
            "pontos": 0, "jogos": 0,
            "v": 0, "e": 0, "d": 0,
            "gp": 0, "gc": 0,
        }
        for e in equipes
    }

    if not os.path.exists(CSV_PATH):
        erro(f"{CSV_PATH} não encontrado.")

    confrontos = []
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f), start=1):
            if not row or not any(c.strip() for c in row):
                continue  # linha em branco
            if len(row) < 4:
                erro(f"Linha {i}: esperado 4 colunas (equipe1,placar1,equipe2,placar2): {row}")

            e1, p1, e2, p2 = (c.strip() for c in row[:4])

            try:
                g1, g2 = int(p1), int(p2)
            except ValueError:
                if i == 1:
                    continue  # cabeçalho
                erro(f"Linha {i}: placar inválido (use números): {row}")

            if g1 < 0 or g2 < 0:
                erro(f"Linha {i}: placar não pode ser negativo: {row}")

            for pais in (e1, e2):
                if pais not in pais_dono:
                    erro(f"Linha {i}: país desconhecido '{pais}'. Confira a grafia em equipes.py")

            dono1, dono2 = pais_dono[e1], pais_dono[e2]
            s1, s2 = stats[dono1], stats[dono2]

            s1["jogos"] += 1
            s2["jogos"] += 1
            s1["gp"] += g1; s1["gc"] += g2
            s2["gp"] += g2; s2["gc"] += g1

            if g1 > g2:
                s1["pontos"] += 3; s1["v"] += 1
                s2["d"] += 1
            elif g1 < g2:
                s2["pontos"] += 3; s2["v"] += 1
                s1["d"] += 1
            else:
                s1["pontos"] += 1; s1["e"] += 1
                s2["pontos"] += 1; s2["e"] += 1

            confrontos.append({
                "e1": e1, "g1": g1, "f1": PAIS_FLAG[e1],
                "e2": e2, "g2": g2, "f2": PAIS_FLAG[e2],
            })

    # Saldo de gols + ordenação: Pontos -> SG -> Gols Marcados -> nome
    tabela = list(stats.values())
    for t in tabela:
        t["sg"] = t["gp"] - t["gc"]
    tabela.sort(key=lambda t: (-t["pontos"], -t["sg"], -t["gp"], t["nome"]))
    for pos, t in enumerate(tabela, start=1):
        t["pos"] = pos

    atualizado_em = datetime.now(timezone(timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")

    os.makedirs(SAIDA_DIR, exist_ok=True)
    with open(os.path.join(SAIDA_DIR, "classificacao.json"), "w", encoding="utf-8") as f:
        json.dump({"atualizado_em": atualizado_em, "tabela": tabela}, f, ensure_ascii=False, indent=2)
    with open(os.path.join(SAIDA_DIR, "confrontos.json"), "w", encoding="utf-8") as f:
        json.dump({"atualizado_em": atualizado_em, "confrontos": confrontos}, f, ensure_ascii=False, indent=2)

    print(f"OK: {len(confrontos)} confronto(s) processado(s), {len(tabela)} participante(s).")
    print("Gerados: docs/dados/classificacao.json e docs/dados/confrontos.json")


if __name__ == "__main__":
    main()
