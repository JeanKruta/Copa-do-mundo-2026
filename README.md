# Bolão da Copa — Tabela de Classificação

Site estático que mostra a classificação dos participantes a partir dos placares
de um CSV. Hospedado de graça no **GitHub Pages**.

## Estrutura do projeto

```
copa/
├── atualizar.ps1         ← você roda este para publicar
├── requirements.txt      ← dependências Python (openpyxl)
├── .env / .env.example   ← sua chave de acesso (privado)
├── .gitignore
├── README.md
├── docs/                 ← SITE PÚBLICO (GitHub Pages serve daqui)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── dados/            ← JSON calculados (gerados automaticamente)
└── fonte/                ← dados e cálculo
    ├── equipes.py        ← participantes e seus países
    ├── gerar.py          ← calcula a classificação
    └── resultados.xlsx   ← você edita os placares aqui (privado)
```

## Como funciona

- `fonte/equipes.py` — participantes e os 3 países de cada um (fonte da verdade).
- `fonte/resultados.xlsx` — **sua** planilha com os placares (NÃO vai para produção).
- `fonte/gerar.py` — lê a planilha + `equipes.py` e calcula a classificação.
- `docs/dados/*.json` — dados públicos calculados que o site consome.
- `docs/index.html` / `style.css` / `app.js` — o site (responsivo, celular e PC).
- `atualizar.ps1` — valida sua chave e publica os novos placares.

### Regras da classificação
- Vitória = 3 pontos · Empate = 1 · Derrota = 0
- Critérios de desempate, nesta ordem: **Pontos → Saldo de Gols → Gols Marcados**
- A classificação é **acumulada** somando todas as rodadas.

## A planilha `fonte/resultados.xlsx`

Cada **aba** é uma rodada: `Primeira Rodada`, `Segunda Rodada`, `Terceira Rodada`,
`Dezesseis Avos`, `Oitavas`, `Quartas`, `Semis`, `Final`.

Em cada aba, preencha as colunas com cabeçalho `equipe1 | placar1 | equipe2 | placar2`:

| equipe1  | placar1 | equipe2    | placar2 |
|----------|---------|------------|---------|
| Alemanha | 3       | Inglaterra | 1       |

Cada linha é um confronto: `Alemanha 3 x 1 Inglaterra`. Detalhes:

- Os pontos vão para o **dono** de cada país (definido em `fonte/equipes.py`).
  Adversários sem dono só aparecem nos confrontos (com bandeira), sem pontuar.
- Linhas **sem placar** são ignoradas (servem para deixar jogos preparados).
- No site, a aba de uma rodada fica **bloqueada (cadeado)** enquanto não tiver
  nenhum placar; a ordem dos jogos segue a ordem das linhas da planilha.
- A grafia dos países é tolerante a acentos e variações (`Catar`/`Qatar`,
  `Coréia`/`Coreia`, `Bósnia`/`Bósnia e Herzegovina`).

## Configuração inicial (uma vez só)

1. Instale o **Python**: https://www.python.org/downloads/ (marque "Add to PATH").
2. Instale as dependências (uma vez):
   ```powershell
   python -m pip install -r requirements.txt
   ```
   (O `atualizar.ps1` também instala o `openpyxl` sozinho se faltar.)
3. Crie o arquivo `.env` (copie de `.env.example`) e defina sua senha:
   ```
   CHAVE_ACESSO=sua-senha-secreta
   ```
4. Crie um repositório **público** no GitHub e suba estes arquivos:
   ```powershell
   git init
   git add .
   git commit -m "Primeira versão"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
   git push -u origin main
   ```
5. No GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
   selecione branch `main` / pasta **`/docs`** e salve.
6. Em ~1 minuto o site fica no ar em:
   `https://SEU_USUARIO.github.io/SEU_REPO/` — compartilhe esse link.

> O `.env` e o `fonte/resultados.xlsx` estão no `.gitignore`, então **não sobem** para o GitHub.

## Atualizar os placares (no dia a dia)

1. Edite o `fonte/resultados.xlsx` (preencha os placares na aba da rodada).
   **Feche a planilha no Excel** antes de publicar (o Excel trava o arquivo enquanto aberto).
2. Rode o script e digite sua chave quando pedir:
   ```powershell
   .\atualizar.ps1
   ```
   Ele calcula tudo, gera os JSON e dá `git push` automaticamente.
3. Em ~1 minuto o site atualizado aparece para todos.

Se algum país estiver escrito errado na planilha, o script avisa (com a aba e a linha) e não publica nada.

## Bandeiras

As bandeiras dos confrontos vêm de `flagcdn.com` (gratuito). Usamos imagens em vez de
emojis porque o Windows não renderiza emojis de bandeira no navegador.
