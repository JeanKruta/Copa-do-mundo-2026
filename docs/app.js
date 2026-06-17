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
  // ordem do Excel (sem inverter)
  for (const c of rodada.confrontos) {
    cont.appendChild(criarConfronto(c));
  }
}

function renderRodadas(dados) {
  const abas = document.getElementById("abas");
  const cont = document.getElementById("confrontos");
  abas.innerHTML = "";
  cont.innerHTML = "";

  const rodadas = dados.rodadas || [];
  const temAlgum = rodadas.some((r) => r.desbloqueada);
  if (!temAlgum) {
    cont.innerHTML = `<p class="aviso">Nenhum placar cadastrado ainda.</p>`;
  }

  // seleciona por padrão a última rodada com placar
  let selecionada = null;
  for (const r of rodadas) {
    if (r.desbloqueada) selecionada = r;
  }

  rodadas.forEach((r) => {
    const btn = document.createElement("button");
    btn.className = "aba";
    btn.textContent = r.nome;

    if (!r.desbloqueada) {
      btn.classList.add("bloqueada");
      btn.disabled = true;
      btn.title = "Rodada ainda sem placares";
      const lock = document.createElement("span");
      lock.className = "cadeado";
      lock.textContent = "🔒";
      btn.appendChild(lock);
    } else {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".aba").forEach((b) => b.classList.remove("ativa"));
        btn.classList.add("ativa");
        mostrarRodada(r);
      });
    }

    if (r === selecionada) {
      btn.classList.add("ativa");
    }
    abas.appendChild(btn);
  });

  if (selecionada) mostrarRodada(selecionada);
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
