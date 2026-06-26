const FLAG_BASE = "https://flagcdn.com/w40/";

async function carregarJSON(caminho) {
  // cache-buster para o GitHub Pages não servir versão antiga
  const resp = await fetch(`${caminho}?t=${Date.now()}`);
  if (!resp.ok) throw new Error(`Falha ao carregar ${caminho}`);
  return resp.json();
}

function bandeira(codigo, nome) {
  const img = document.createElement("img");
  img.src = `${FLAG_BASE}${codigo}.png`;
  img.alt = nome;
  img.loading = "lazy";
  return img;
}

function renderTabela(dados) {
  const corpo = document.getElementById("tabela-corpo");
  corpo.innerHTML = "";

  for (const t of dados.tabela) {
    const tr = document.createElement("tr");
    if (t.pos <= 3) tr.classList.add(`top${t.pos}`);

    const sgClasse = t.sg > 0 ? "sg-pos" : t.sg < 0 ? "sg-neg" : "";
    const sgTexto = t.sg > 0 ? `+${t.sg}` : `${t.sg}`;

    tr.innerHTML = `
      <td class="col-pos"><span class="pos-badge">${t.pos}</span></td>
      <td class="col-nome">${t.nome}</td>
      <td class="pts">${t.pontos}</td>
      <td>${t.jogos}</td>
      <td>${t.v}</td>
      <td>${t.e}</td>
      <td>${t.d}</td>
      <td>${t.gp}</td>
      <td>${t.gc}</td>
      <td class="${sgClasse}">${sgTexto}</td>
    `;
    corpo.appendChild(tr);
  }
}

function criarConfronto(c) {
  const div = document.createElement("div");
  div.className = "match";

  const home = document.createElement("div");
  home.className = "team home";
  const nomeH = document.createElement("span");
  nomeH.className = "nome";
  nomeH.textContent = c.e1;
  home.append(nomeH, bandeira(c.f1, c.e1));

  const placar = document.createElement("div");
  placar.className = "placar";
  placar.textContent = `${c.g1} x ${c.g2}`;

  const away = document.createElement("div");
  away.className = "team away";
  const nomeA = document.createElement("span");
  nomeA.className = "nome";
  nomeA.textContent = c.e2;
  away.append(bandeira(c.f2, c.e2), nomeA);

  div.append(home, placar, away);
  return div;
}

function mostrarRodada(rodada) {
  const cont = document.getElementById("confrontos");
  cont.innerHTML = "";
  for (const c of rodada.confrontos) {
    cont.appendChild(criarConfronto(c));
  }
}

const KNOCKOUT_NOMES = ["Dezesseis Avos", "Oitavas", "Quartas", "Semis", "Final"];

function preencher(confrontos, tamanho) {
  const out = [];
  for (let i = 0; i < tamanho; i++) {
    out.push(confrontos[i] || null);
  }
  return out;
}

function bracketMatch(c) {
  const div = document.createElement("div");
  div.className = "bm";
  if (!c) {
    div.classList.add("bm-vazio");
    div.innerHTML = `
      <div class="bm-row"><span class="bm-team">?</span><span class="bm-score">–</span></div>
      <div class="bm-row"><span class="bm-team">?</span><span class="bm-score">–</span></div>
    `;
    return div;
  }

  const venceu1 = c.g1 > c.g2;
  const venceu2 = c.g2 > c.g1;

  const row1 = document.createElement("div");
  row1.className = "bm-row" + (venceu1 ? " bm-vencedor" : "");
  const nome1 = document.createElement("span");
  nome1.className = "bm-team";
  nome1.textContent = c.e1;
  const s1 = document.createElement("span");
  s1.className = "bm-score";
  s1.textContent = c.g1;
  row1.append(bandeira(c.f1, c.e1), nome1, s1);

  const row2 = document.createElement("div");
  row2.className = "bm-row" + (venceu2 ? " bm-vencedor" : "");
  const nome2 = document.createElement("span");
  nome2.className = "bm-team";
  nome2.textContent = c.e2;
  const s2 = document.createElement("span");
  s2.className = "bm-score";
  s2.textContent = c.g2;
  row2.append(bandeira(c.f2, c.e2), nome2, s2);

  div.append(row1, row2);
  return div;
}

function bracketCol(label, matches) {
  const col = document.createElement("div");
  col.className = "bracket-col";
  col.dataset.qtd = matches.length;

  const titulo = document.createElement("div");
  titulo.className = "bracket-col-titulo";
  titulo.textContent = label;
  col.appendChild(titulo);

  const items = document.createElement("div");
  items.className = "bracket-col-items";
  matches.forEach((m) => items.appendChild(bracketMatch(m)));
  col.appendChild(items);

  return col;
}

function bracketSide(lado, colunas) {
  const side = document.createElement("div");
  side.className = `bracket-side bracket-${lado}`;
  for (const c of colunas) side.appendChild(c);
  return side;
}

function mostrarMataMata(rodadas) {
  const cont = document.getElementById("confrontos");
  cont.innerHTML = "";

  const porNome = {};
  for (const r of rodadas) porNome[r.nome] = r;

  // listas completas (jogos vazios = "?")
  const avos   = preencher(porNome["Dezesseis Avos"]?.confrontos || [], 16);
  const oitavas = preencher(porNome["Oitavas"]?.confrontos        || [], 8);
  const quartas = preencher(porNome["Quartas"]?.confrontos        || [], 4);
  const semis   = preencher(porNome["Semis"]?.confrontos          || [], 2);
  const final   = preencher(porNome["Final"]?.confrontos          || [], 1);

  // metade da esquerda x metade da direita
  const ladoEsq = [
    bracketCol("Dezesseis Avos", avos.slice(0, 8)),
    bracketCol("Oitavas", oitavas.slice(0, 4)),
    bracketCol("Quartas", quartas.slice(0, 2)),
    bracketCol("Semis", semis.slice(0, 1)),
  ];
  const ladoDir = [
    bracketCol("Semis", semis.slice(1, 2)),
    bracketCol("Quartas", quartas.slice(2, 4)),
    bracketCol("Oitavas", oitavas.slice(4, 8)),
    bracketCol("Dezesseis Avos", avos.slice(8, 16)),
  ];
  const centro = [bracketCol("Final", final)];

  const wrap = document.createElement("div");
  wrap.className = "bracket-wrap";

  const bracket = document.createElement("div");
  bracket.className = "bracket";
  bracket.append(
    bracketSide("left", ladoEsq),
    bracketSide("center", centro),
    bracketSide("right", ladoDir),
  );

  wrap.append(bracket);
  cont.append(wrap);
}

function renderRodadas(dados) {
  const abas = document.getElementById("abas");
  const cont = document.getElementById("confrontos");
  abas.innerHTML = "";
  cont.innerHTML = "";

  const rodadas = dados.rodadas || [];
  const grupo = rodadas.filter((r) => !KNOCKOUT_NOMES.includes(r.nome));
  const mata = rodadas.filter((r) => KNOCKOUT_NOMES.includes(r.nome));

  const tabs = [];
  for (const r of grupo) {
    tabs.push({
      label: r.nome,
      desbloqueada: r.desbloqueada,
      temPlacar: r.desbloqueada,
      mostrar: () => mostrarRodada(r),
    });
  }
  let abaMata = null;
  if (mata.length > 0) {
    abaMata = {
      label: "Mata-mata",
      desbloqueada: true, // sempre aberta para visualizar o chaveamento
      temPlacar: mata.some((r) => r.desbloqueada),
      mostrar: () => mostrarMataMata(mata),
    };
    tabs.push(abaMata);
  }

  const temAlgum = tabs.some((t) => t.temPlacar);
  if (!temAlgum) {
    cont.innerHTML = `<p class="aviso">Nenhum placar cadastrado ainda.</p>`;
  }

  // default: Mata-mata se já tiver placar nele; senão, última fase de grupos com placar
  let selecionada = null;
  if (abaMata && abaMata.temPlacar) {
    selecionada = abaMata;
  } else {
    for (const t of tabs) if (t !== abaMata && t.temPlacar) selecionada = t;
  }

  for (const t of tabs) {
    const btn = document.createElement("button");
    btn.className = "aba";
    btn.textContent = t.label;

    if (!t.desbloqueada) {
      btn.classList.add("bloqueada");
      btn.disabled = true;
      btn.title = "Aba ainda sem placares";
    } else {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".aba").forEach((b) => b.classList.remove("ativa"));
        btn.classList.add("ativa");
        t.mostrar();
      });
    }

    if (t === selecionada) btn.classList.add("ativa");
    abas.appendChild(btn);
  }

  if (selecionada) selecionada.mostrar();
}

async function iniciar() {
  try {
    const [classificacao, confrontos] = await Promise.all([
      carregarJSON("dados/classificacao.json"),
      carregarJSON("dados/confrontos.json"),
    ]);

    renderTabela(classificacao);
    renderRodadas(confrontos);

    if (classificacao.atualizado_em) {
      document.getElementById("atualizado").textContent =
        `Atualizado em ${classificacao.atualizado_em}`;
    }
  } catch (e) {
    document.getElementById("tabela-corpo").innerHTML =
      `<tr><td colspan="10" class="aviso">Não foi possível carregar os dados.</td></tr>`;
    console.error(e);
  }
}

iniciar();
