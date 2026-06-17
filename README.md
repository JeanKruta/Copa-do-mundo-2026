# Bolão da Copa — Tabela de Classificação

Site estático que mostra a classificação dos participantes a partir dos placares
de um CSV. Hospedado de graça no **GitHub Pages**.

## Estrutura do projeto

```
copa/
├── atualizar.ps1        ← você roda este para publicar
├── .env / .env.example  ← sua chave de acesso (privado)
├── .gitignore
├── README.md
├── docs/                ← SITE PÚBLICO (GitHub Pages serve daqui)
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   └── dados/           ← JSON calculados (gerados automaticamente)
└── fonte/               ← dados e cálculo
    ├── equipes.py       ← participantes e seus países
    ├── gerar.py         ← calcula a classificação
    └── resultados.csv   ← você edita os placares aqui (privado)
```

## Como funciona

- `fonte/equipes.py` — participantes e os 3 países de cada um (fonte da verdade).
- `fonte/resultados.csv` — **seu** arquivo central com os placares (NÃO vai para produção).
- `fonte/gerar.py` — lê o CSV + `equipes.py` e calcula a classificação.
- `docs/dados/*.json` — dados públicos calculados que o site consome.
- `docs/index.html` / `style.css` / `app.js` — o site (responsivo, celular e PC).
- `atualizar.ps1` — valida sua chave e publica os novos placares.

### Regras da classificação
- Vitória = 3 pontos · Empate = 1 · Derrota = 0
- Critérios de desempate, nesta ordem: **Pontos → Saldo de Gols → Gols Marcados**

## Formato do `fonte/resultados.csv`

```
equipe1,placar1,equipe2,placar2
Alemanha,3,Inglaterra,1
Brasil,2,Argentina,2
```

Cada linha é um confronto: `Alemanha,3,Inglaterra,1` = Alemanha 3 x 1 Inglaterra.
Os pontos vão para o **dono** de cada país (definido em `fonte/equipes.py`).
Use exatamente os mesmos nomes de país que estão em `equipes.py`.

## Configuração inicial (uma vez só)

1. Instale o **Python**: https://www.python.org/downloads/ (marque "Add to PATH").
2. Crie o arquivo `.env` (copie de `.env.example`) e defina sua senha:
   ```
   CHAVE_ACESSO=sua-senha-secreta
   ```
3. Crie um repositório **público** no GitHub e suba estes arquivos:
   ```powershell
   git init
   git add .
   git commit -m "Primeira versão"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
   git push -u origin main
   ```
4. No GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
   selecione branch `main` / pasta **`/docs`** e salve.
5. Em ~1 minuto o site fica no ar em:
   `https://SEU_USUARIO.github.io/SEU_REPO/` — compartilhe esse link.

> O `.env` e o `fonte/resultados.csv` estão no `.gitignore`, então **não sobem** para o GitHub.

## Atualizar os placares (no dia a dia)

1. Edite o `fonte/resultados.csv` (adicione as novas linhas de confronto).
2. Rode o script e digite sua chave quando pedir:
   ```powershell
   .\atualizar.ps1
   ```
   Ele calcula tudo, gera os JSON e dá `git push` automaticamente.
3. Em ~1 minuto o site atualizado aparece para todos.

Se algum país estiver escrito errado no CSV, o script avisa e não publica nada.

## Bandeiras

As bandeiras dos confrontos vêm de `flagcdn.com` (gratuito). Usamos imagens em vez de
emojis porque o Windows não renderiza emojis de bandeira no navegador.
