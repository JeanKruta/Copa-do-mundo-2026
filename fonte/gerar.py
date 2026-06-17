# -*- coding: utf-8 -*-
"""
Lê resultados.csv + equipes.py, calcula a classificação dos participantes
e gera os arquivos públicos docs/dados/classificacao.json e confrontos.json.

- A comparação de países é feita por código ISO (ignora acentos/grafia),
  então "Catar"/"Qatar" ou "Bósnia"/"Bósnia e Herzegovina" são o mesmo país.
- Só os times de participantes pontuam; adversários sem dono apenas aparecem
  nos confrontos (com bandeira).
- O CSV bruto NÃO é publicado: só os JSON calculados vão para produção.
"""
import csv
import json
import os
import sys
import unicodedata
from datetime import datetime, timezone, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from equipes import equipes

# Nome do país (em português) -> código ISO usado pelo flagcdn.com.
# Lista ampla para que praticamente qualquer seleção pegue a bandeira sozinha.
PAIS_ISO = {
    # Europa
    "Albânia": "al", "Alemanha": "de", "Andorra": "ad", "Armênia": "am",
    "Áustria": "at", "Azerbaijão": "az", "Bélgica": "be", "Bielorrússia": "by",
    "Bósnia": "ba", "Bósnia e Herzegovina": "ba", "Bulgária": "bg",
    "Cazaquistão": "kz", "Chipre": "cy", "Croácia": "hr", "Dinamarca": "dk",
    "Escócia": "gb-sct", "Eslováquia": "sk", "Eslovênia": "si", "Espanha": "es",
    "Estônia": "ee", "Ilhas Faroé": "fo", "Finlândia": "fi", "França": "fr",
    "País de Gales": "gb-wls", "Geórgia": "ge", "Gibraltar": "gi", "Grécia": "gr",
    "Holanda": "nl", "Países Baixos": "nl", "Hungria": "hu", "Inglaterra": "gb-eng",
    "Irlanda": "ie", "Irlanda do Norte": "gb-nir", "Islândia": "is", "Israel": "il",
    "Itália": "it", "Kosovo": "xk", "Letônia": "lv", "Liechtenstein": "li",
    "Lituânia": "lt", "Luxemburgo": "lu", "Macedônia do Norte": "mk", "Malta": "mt",
    "Moldávia": "md", "Montenegro": "me", "Noruega": "no", "Polônia": "pl",
    "Portugal": "pt", "Reino Unido": "gb", "República Tcheca": "cz", "Tchéquia": "cz",
    "Romênia": "ro", "Rússia": "ru", "San Marino": "sm", "Sérvia": "rs",
    "Suécia": "se", "Suíça": "ch", "Turquia": "tr", "Ucrânia": "ua",

    # América do Sul
    "Argentina": "ar", "Bolívia": "bo", "Brasil": "br", "Chile": "cl",
    "Colômbia": "co", "Equador": "ec", "Paraguai": "py", "Peru": "pe",
    "Uruguai": "uy", "Venezuela": "ve",

    # América do Norte / Central / Caribe
    "Canadá": "ca", "Costa Rica": "cr", "Cuba": "cu", "El Salvador": "sv",
    "Estados Unidos": "us", "EUA": "us", "Guatemala": "gt", "Haiti": "ht",
    "Honduras": "hn", "Jamaica": "jm", "México": "mx", "Nicarágua": "ni",
    "Panamá": "pa", "República Dominicana": "do", "Trinidad e Tobago": "tt",
    "Curaçao": "cw", "Suriname": "sr",

    # África
    "África do Sul": "za", "Angola": "ao", "Argélia": "dz", "Benin": "bj",
    "Botsuana": "bw", "Burkina Faso": "bf", "Burundi": "bi", "Cabo Verde": "cv",
    "Camarões": "cm", "Chade": "td", "Comores": "km", "Congo": "cg",
    "República do Congo": "cg", "RD Congo": "cd", "República Democrática do Congo": "cd",
    "Costa do Marfim": "ci", "Egito": "eg", "Eritreia": "er", "Etiópia": "et",
    "Gabão": "ga", "Gâmbia": "gm", "Gana": "gh", "Guiné": "gn",
    "Guiné-Bissau": "gw", "Guiné Equatorial": "gq", "Líbia": "ly", "Libéria": "lr",
    "Madagáscar": "mg", "Malawi": "mw", "Mali": "ml", "Marrocos": "ma",
    "Mauritânia": "mr", "Moçambique": "mz", "Namíbia": "na", "Níger": "ne",
    "Nigéria": "ng", "Quênia": "ke", "Ruanda": "rw", "Senegal": "sn",
    "Serra Leoa": "sl", "Seychelles": "sc", "Somália": "so", "Sudão": "sd",
    "Sudão do Sul": "ss", "Essuatíni": "sz", "Suazilândia": "sz", "Tanzânia": "tz",
    "Togo": "tg", "Tunísia": "tn", "Uganda": "ug", "Zâmbia": "zm", "Zimbábue": "zw",

    # Ásia
    "Arábia Saudita": "sa", "Bahrein": "bh", "Bangladesh": "bd", "Catar": "qa",
    "Qatar": "qa", "China": "cn", "Coreia do Norte": "kp", "Coreia do Sul": "kr",
    "Emirados Árabes Unidos": "ae", "Filipinas": "ph", "Iêmen": "ye", "Índia": "in",
    "Indonésia": "id", "Irã": "ir", "Iraque": "iq", "Japão": "jp", "Jordânia": "jo",
    "Kuwait": "kw", "Líbano": "lb", "Malásia": "my", "Omã": "om", "Paquistão": "pk",
    "Quirguistão": "kg", "Síria": "sy", "Tailândia": "th", "Tajiquistão": "tj",
    "Turcomenistão": "tm", "Uzbequistão": "uz", "Vietnã": "vn",

    # Oceania
    "Austrália": "au", "Fiji": "fj", "Nova Zelândia": "nz",
    "Papua-Nova Guiné": "pg", "Ilhas Salomão": "sb",
}

CSV_PATH = os.path.join(BASE, "resultados.csv")
SAIDA_DIR = os.path.join(BASE, "..", "docs", "dados")


def normalizar(nome):
    """minúsculas, sem acentos e sem espaços extras, para casar grafias diferentes."""
    texto = " ".join(nome.strip().lower().split())
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return sem_acento


# Lookup por nome normalizado -> código ISO
ISO_POR_NOME = {normalizar(nome): iso for nome, iso in PAIS_ISO.items()}


def iso_de(pais):
    return ISO_POR_NOME.get(normalizar(pais))


def erro(msg):
    print(f"ERRO: {msg}")
    sys.exit(1)


def main():
    # Dono (participante) por código ISO do país
    dono_por_iso = {}
    paises_sem_iso = []
    for e in equipes:
        for pais in e["paises"]:
            iso = iso_de(pais)
            if not iso:
                paises_sem_iso.append(pais)
            else:
                dono_por_iso[iso] = e["nome"]
    if paises_sem_iso:
        erro("Países de equipes.py sem código mapeado em gerar.py: " + ", ".join(paises_sem_iso))

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

    def pontuar(nome, gp, gc):
        s = stats[nome]
        s["jogos"] += 1
        s["gp"] += gp
        s["gc"] += gc
        if gp > gc:
            s["pontos"] += 3; s["v"] += 1
        elif gp < gc:
            s["d"] += 1
        else:
            s["pontos"] += 1; s["e"] += 1

    confrontos = []
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f), start=1):
            if not row or not any(c.strip() for c in row):
                continue
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

            iso1, iso2 = iso_de(e1), iso_de(e2)
            if not iso1:
                erro(f"Linha {i}: país sem bandeira '{e1}'. Adicione em PAIS_ISO (gerar.py) ou confira a grafia.")
            if not iso2:
                erro(f"Linha {i}: país sem bandeira '{e2}'. Adicione em PAIS_ISO (gerar.py) ou confira a grafia.")

            dono1 = dono_por_iso.get(iso1)
            dono2 = dono_por_iso.get(iso2)
            if dono1:
                pontuar(dono1, g1, g2)
            if dono2:
                pontuar(dono2, g2, g1)

            confrontos.append({
                "e1": e1, "g1": g1, "f1": iso1,
                "e2": e2, "g2": g2, "f2": iso2,
            })

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
