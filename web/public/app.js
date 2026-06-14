"use strict";

// ---------------------------------------------------------------------------
// Ludoteca — frontend (sem framework). Conversa com o gateway via /api.
// Qualquer falha vira mensagem amigável; nada de detalhe técnico na tela.
// ---------------------------------------------------------------------------

const GENERIC = "Não foi possível carregar agora. Tente novamente em instantes.";
const PLAYER_KEY = "ludoteca:player";

const state = {
  players: [],
  currentId: localStorage.getItem(PLAYER_KEY) || "",
  storeSearch: "",
};

function money(cents) {
  return (Number(cents || 0) / 100).toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function friendly(body) {
  return (body && body.error && body.error.message) || GENERIC;
}

async function apiGet(path) {
  let res;
  try {
    res = await fetch(path, { headers: { accept: "application/json" } });
  } catch (_e) {
    throw new Error(GENERIC);
  }
  const body = await res.json().catch(() => null);
  if (!res.ok) throw new Error(friendly(body));
  return body;
}

async function apiSend(method, path, payload) {
  let res;
  try {
    res = await fetch(path, {
      method,
      headers: { "content-type": "application/json" },
      body: payload === undefined ? undefined : JSON.stringify(payload),
    });
  } catch (_e) {
    throw new Error(GENERIC);
  }
  const body = await res.json().catch(() => null);
  if (!res.ok) throw new Error(friendly(body));
  return body;
}

const apiPost = (path, payload) => apiSend("POST", path, payload);
const apiDelete = (path) => apiSend("DELETE", path);

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function stars(average) {
  if (average === null || average === undefined) {
    return '<span class="muted">sem nota</span>';
  }
  const filled = Math.round(Number(average));
  return `<span class="stars">${"★".repeat(filled)}${"☆".repeat(5 - filled)}</span> ${average}`;
}

function alertHtml(message) {
  return `<div class="alert">${esc(message)}</div>`;
}

function currentPlayer() {
  return state.players.find((p) => p.id === state.currentId) || null;
}

// ----- Navegação -----------------------------------------------------------
document.getElementById("nav").addEventListener("click", (event) => {
  const button = event.target.closest(".nav__btn");
  if (!button) return;
  showView(button.dataset.view, button);
});

function showView(view, button) {
  document.querySelectorAll(".nav__btn").forEach((b) => {
    b.classList.toggle("nav__btn--on", button ? b === button : b.dataset.view === view);
  });
  document.querySelectorAll(".view").forEach((v) => {
    v.classList.toggle("view--on", v.id === `view-${view}`);
  });

  if (view === "loja") loadStore();
  if (view === "catalogo") loadCatalog();
  if (view === "ranking") loadRanking();
  if (view === "colecao") loadCollection();
  if (view === "amigos") loadFriends();
}

// ===========================================================================
// JOGADOR (perfil ativo + carteira)
// ===========================================================================
async function loadPlayers() {
  const select = document.getElementById("player-select");
  try {
    const body = await apiGet("/api/players");
    state.players = body.data || [];
  } catch (_err) {
    state.players = [];
  }

  if (state.players.length === 0) {
    select.innerHTML = '<option value="">Nenhum jogador</option>';
    state.currentId = "";
    renderWallet();
    return;
  }

  if (!state.players.some((p) => p.id === state.currentId)) {
    state.currentId = state.players[0].id;
  }
  localStorage.setItem(PLAYER_KEY, state.currentId);

  select.innerHTML = state.players
    .map((p) => `<option value="${esc(p.id)}">${esc(p.name)}</option>`)
    .join("");
  select.value = state.currentId;
  renderWallet();
}

function renderWallet() {
  const player = currentPlayer();
  document.getElementById("player-saldo").textContent = player ? money(player.walletCents) : "—";
}

document.getElementById("player-select").addEventListener("change", (event) => {
  state.currentId = event.target.value;
  localStorage.setItem(PLAYER_KEY, state.currentId);
  renderWallet();
  // Recarrega a view ativa para refletir o novo jogador.
  const active = document.querySelector(".nav__btn--on");
  if (active) showView(active.dataset.view, active);
});

document.getElementById("novo-jogador-btn").addEventListener("click", () => {
  document.getElementById("form-novo-jogador").classList.toggle("is-hidden");
});

document.getElementById("form-novo-jogador").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const msg = document.getElementById("novo-jogador-msg");
  msg.className = "msg";
  msg.textContent = "Criando…";
  try {
    const body = await apiPost("/api/players", { name: form.name.value });
    state.currentId = body.data.id;
    localStorage.setItem(PLAYER_KEY, state.currentId);
    msg.className = "msg ok";
    msg.textContent = "Jogador criado!";
    form.reset();
    form.parentElement.classList.add("is-hidden");
    await loadPlayers();
  } catch (err) {
    msg.className = "msg err";
    msg.textContent = err.message;
  }
});

document.getElementById("deposito-btn").addEventListener("click", async () => {
  const player = currentPlayer();
  if (!player) {
    alert("Crie ou selecione um jogador primeiro.");
    return;
  }
  const value = prompt("Quanto deseja adicionar à carteira? (em R$)", "50");
  if (value === null) return;
  const cents = Math.round((parseFloat(value.replace(",", ".")) || 0) * 100);
  if (cents <= 0) return;
  try {
    const body = await apiPost(`/api/players/${player.id}/deposit`, { amountCents: cents });
    updatePlayerInState(body.data);
    renderWallet();
  } catch (err) {
    alert(err.message);
  }
});

function updatePlayerInState(updated) {
  const index = state.players.findIndex((p) => p.id === updated.id);
  if (index >= 0) state.players[index] = updated;
}

async function refreshCurrentPlayer() {
  const player = currentPlayer();
  if (!player) return;
  try {
    const body = await apiGet(`/api/players/${player.id}`);
    updatePlayerInState(body.data);
    renderWallet();
  } catch (_err) {
    /* mantém o saldo em cache se a atualização falhar */
  }
}

// ===========================================================================
// LOJA
// ===========================================================================
const lojaGrid = document.getElementById("loja-grid");

async function loadStore() {
  const status = document.getElementById("loja-status");
  status.innerHTML = "";
  lojaGrid.innerHTML = '<p class="muted">Carregando loja…</p>';

  const pid = state.currentId;
  try {
    const body = await apiGet(`/api/store${pid ? `?playerId=${encodeURIComponent(pid)}` : ""}`);
    const payload = body.data || {};
    let games = payload.games || [];

    if (state.storeSearch) {
      const term = state.storeSearch.toLowerCase();
      games = games.filter(
        (g) =>
          (g.title || "").toLowerCase().includes(term) ||
          (g.genre || "").toLowerCase().includes(term),
      );
    }

    if (!payload.playersAvailable && pid) {
      status.innerHTML = alertHtml(
        "Os perfis estão indisponíveis — exibindo a loja sem suas marcações de compra.",
      );
    }
    if (!pid) {
      status.innerHTML = alertHtml("Crie um jogador para comprar e favoritar jogos.");
    }

    if (games.length === 0) {
      lojaGrid.innerHTML = '<p class="muted">Nenhum jogo encontrado.</p>';
      return;
    }
    lojaGrid.innerHTML = games.map(storeCard).join("");
  } catch (err) {
    lojaGrid.innerHTML = "";
    status.innerHTML = alertHtml(err.message);
  }
}

function storeCard(game) {
  const id = esc(game.id);
  let action;
  if (game.owned) {
    action = '<span class="badge badge--own">✓ Na biblioteca</span>';
  } else if (state.currentId) {
    const wish = game.wished
      ? `<button class="btn btn--ghost btn--mini" data-unwish="${id}">★ Remover desejo</button>`
      : `<button class="btn btn--ghost btn--mini" data-wish="${id}">☆ Desejar</button>`;
    action = `<button class="btn btn--neon btn--mini" data-buy="${id}">Comprar</button>${wish}`;
  } else {
    action = '<span class="muted">selecione um jogador</span>';
  }

  return `
    <article class="game">
      <div class="game__genre">${esc(game.genre)}</div>
      <div class="game__title">${esc(game.title)}</div>
      <div class="game__meta">
        <span>🕹️ ${esc(game.platform)}</span>
        <span>📅 ${esc(game.releaseYear)}</span>
      </div>
      <div class="game__price">${money(game.priceCents)}</div>
      <div class="game__actions">${action}</div>
    </article>`;
}

lojaGrid.addEventListener("click", async (event) => {
  const buy = event.target.closest("[data-buy]");
  const wish = event.target.closest("[data-wish]");
  const unwish = event.target.closest("[data-unwish]");
  const pid = state.currentId;
  if (!pid) return;

  if (buy) {
    buy.disabled = true;
    try {
      const body = await apiPost(`/api/players/${pid}/purchases`, { gameId: buy.dataset.buy });
      const pricing = body.data.pricing;
      flashToast(
        pricing.discountCents > 0
          ? `Compra concluída! ${pricing.label} (${money(pricing.finalCents)})`
          : `Compra concluída! ${money(pricing.finalCents)}`,
      );
      await refreshCurrentPlayer();
      loadStore();
    } catch (err) {
      buy.disabled = false;
      document.getElementById("loja-status").innerHTML = alertHtml(err.message);
    }
  } else if (wish) {
    try {
      await apiPost(`/api/players/${pid}/wishlist`, { gameId: wish.dataset.wish });
      loadStore();
    } catch (err) {
      document.getElementById("loja-status").innerHTML = alertHtml(err.message);
    }
  } else if (unwish) {
    try {
      await apiDelete(`/api/players/${pid}/wishlist/${unwish.dataset.unwish}`);
      loadStore();
    } catch (err) {
      document.getElementById("loja-status").innerHTML = alertHtml(err.message);
    }
  }
});

let storeTimer;
document.getElementById("loja-busca").addEventListener("input", (event) => {
  clearTimeout(storeTimer);
  const value = event.target.value;
  storeTimer = setTimeout(() => {
    state.storeSearch = value.trim();
    loadStore();
  }, 250);
});
document.getElementById("reload-loja").addEventListener("click", loadStore);

// ===========================================================================
// CATÁLOGO (administração + avaliações)
// ===========================================================================
const grid = document.getElementById("catalogo-grid");

async function loadCatalog() {
  const status = document.getElementById("catalogo-status");
  status.innerHTML = "";
  grid.innerHTML = '<p class="muted">Carregando jogos…</p>';

  try {
    const body = await apiGet("/api/games");
    const games = body.data || [];
    if (games.length === 0) {
      grid.innerHTML = '<p class="muted">Nenhum jogo cadastrado ainda.</p>';
      return;
    }
    grid.innerHTML = games.map(gameCard).join("");
  } catch (err) {
    grid.innerHTML = "";
    status.innerHTML = alertHtml(err.message);
  }
}

function gameCard(game) {
  const available = game.available
    ? '<span class="badge">disponível</span>'
    : '<span class="muted">indisponível</span>';
  return `
    <article class="game" data-game-id="${esc(game.id)}">
      <div class="game__genre">${esc(game.genre)}</div>
      <div class="game__title">${esc(game.title)}</div>
      <div class="game__meta">
        <span>🕹️ ${esc(game.platform)}</span>
        <span>📅 ${esc(game.releaseYear)}</span>
        ${available}
      </div>
      <div class="game__price">${money(game.priceCents)}</div>
      <button class="btn btn--ghost btn--mini" data-toggle-reviews="${esc(game.id)}">
        Ver avaliações
      </button>
      <div class="game__reviews is-hidden" data-reviews-panel="${esc(game.id)}"></div>
    </article>`;
}

grid.addEventListener("click", async (event) => {
  const toggle = event.target.closest("[data-toggle-reviews]");
  if (!toggle) return;
  const id = toggle.dataset.toggleReviews;
  const panel = grid.querySelector(`[data-reviews-panel="${id}"]`);
  if (!panel) return;

  panel.classList.toggle("is-hidden");
  if (!panel.classList.contains("is-hidden") && !panel.dataset.loaded) {
    await loadReviews(id, panel);
  }
});

async function loadReviews(gameId, panel) {
  panel.innerHTML = '<p class="muted">Carregando avaliações…</p>';
  let listHtml = "";
  try {
    const body = await apiGet(`/api/games/${gameId}/reviews`);
    const reviews = body.data || [];
    listHtml = reviews.length
      ? reviews
          .map(
            (r) =>
              `<div class="review"><b>${esc(r.author)}</b> ${stars(r.rating)}<br>${esc(r.comment || "")}</div>`,
          )
          .join("")
      : '<p class="muted">Ainda sem avaliações. Seja o primeiro!</p>';
  } catch (err) {
    listHtml = alertHtml(err.message);
  }
  panel.innerHTML = listHtml + reviewFormHtml(gameId);
  panel.dataset.loaded = "1";
}

function reviewFormHtml(gameId) {
  const author = currentPlayer() ? esc(currentPlayer().name) : "";
  return `
    <form data-review-form="${esc(gameId)}" class="review-form">
      <div class="row">
        <label>Seu nome<input name="author" required minlength="2" value="${author}" /></label>
        <label>Nota
          <select name="rating">
            <option value="5">5 - Excelente</option>
            <option value="4">4 - Muito bom</option>
            <option value="3">3 - Ok</option>
            <option value="2">2 - Fraco</option>
            <option value="1">1 - Ruim</option>
          </select>
        </label>
      </div>
      <label>Comentário<input name="comment" placeholder="O que achou?" /></label>
      <button class="btn btn--neon btn--mini" type="submit">Avaliar</button>
      <p class="msg" data-review-msg="${esc(gameId)}"></p>
    </form>`;
}

grid.addEventListener("submit", async (event) => {
  const form = event.target.closest("[data-review-form]");
  if (!form) return;
  event.preventDefault();

  const gameId = form.dataset.reviewForm;
  const msg = grid.querySelector(`[data-review-msg="${gameId}"]`);
  msg.className = "msg";
  msg.textContent = "Enviando…";

  try {
    await apiPost(`/api/games/${gameId}/reviews`, {
      author: form.author.value,
      rating: Number(form.rating.value),
      comment: form.comment.value,
    });
    msg.className = "msg ok";
    msg.textContent = "Avaliação registrada!";
    const panel = grid.querySelector(`[data-reviews-panel="${gameId}"]`);
    if (panel) {
      panel.dataset.loaded = "";
      await loadReviews(gameId, panel);
    }
  } catch (err) {
    msg.className = "msg err";
    msg.textContent = err.message;
  }
});

document.getElementById("toggle-novo-jogo").addEventListener("click", () => {
  document.getElementById("form-jogo").classList.toggle("is-hidden");
});

document.getElementById("form-jogo").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  const msg = document.getElementById("jogo-msg");
  msg.className = "msg";
  msg.textContent = "Salvando…";

  try {
    await apiPost("/api/games", {
      title: form.title.value,
      genre: form.genre.value,
      platform: form.platform.value,
      priceCents: Math.round((parseFloat(form.price.value) || 0) * 100),
      releaseYear: Number(form.releaseYear.value),
    });
    msg.className = "msg ok";
    msg.textContent = "Jogo adicionado!";
    form.reset();
    loadCatalog();
  } catch (err) {
    msg.className = "msg err";
    msg.textContent = err.message;
  }
});

// ===========================================================================
// RANKING
// ===========================================================================
async function loadRanking() {
  const by = document.getElementById("ranking-by").value;
  const status = document.getElementById("ranking-status");
  const list = document.getElementById("ranking-lista");
  status.innerHTML = "";
  list.innerHTML = '<p class="muted">Calculando ranking…</p>';

  try {
    const body = await apiGet(`/api/ranking?by=${encodeURIComponent(by)}`);
    const payload = body.data || {};
    const ranking = payload.ranking || [];

    if (!payload.reviewsAvailable) {
      status.innerHTML = alertHtml(
        "As avaliações estão indisponíveis no momento — exibindo o ranking sem as notas.",
      );
    }

    if (ranking.length === 0) {
      list.innerHTML = '<p class="muted">Sem jogos para ranquear.</p>';
      return;
    }

    list.innerHTML = ranking
      .map(
        (game, index) => `
        <li class="rank__item">
          <div class="rank__pos">${index + 1}º</div>
          <div class="rank__info">
            <div class="rank__title">${esc(game.title)}</div>
            <div class="muted">${esc(game.genre)} · ${esc(game.releaseYear)} · ${money(game.priceCents)}</div>
          </div>
          <div class="rank__score">
            ${stars(game.average)}<br>
            <span class="muted">${game.reviewCount || 0} avaliação(ões)</span>
          </div>
        </li>`,
      )
      .join("");
  } catch (err) {
    list.innerHTML = "";
    status.innerHTML = alertHtml(err.message);
  }
}

document.getElementById("reload-ranking").addEventListener("click", loadRanking);
document.getElementById("ranking-by").addEventListener("change", loadRanking);

// ===========================================================================
// COLEÇÃO (biblioteca + desejos)
// ===========================================================================
async function loadCollection() {
  const status = document.getElementById("colecao-status");
  const lib = document.getElementById("biblioteca-grid");
  const wish = document.getElementById("desejos-grid");
  status.innerHTML = "";
  lib.innerHTML = "";
  wish.innerHTML = "";

  const pid = state.currentId;
  if (!pid) {
    status.innerHTML = alertHtml("Crie um jogador para ter uma coleção.");
    return;
  }

  lib.innerHTML = '<p class="muted">Carregando…</p>';
  try {
    const body = await apiGet(`/api/players/${pid}/library`);
    const entries = body.data || [];
    lib.innerHTML = entries.length
      ? entries.map(libraryCard).join("")
      : '<p class="muted">Você ainda não comprou jogos. Visite a loja!</p>';
  } catch (err) {
    lib.innerHTML = "";
    status.innerHTML = alertHtml(err.message);
  }

  try {
    const body = await apiGet(`/api/players/${pid}/wishlist`);
    const items = body.data || [];
    wish.innerHTML = items.length
      ? items.map(wishlistCard).join("")
      : '<p class="muted">Sua lista de desejos está vazia.</p>';
  } catch (_err) {
    wish.innerHTML = '<p class="muted">Não foi possível carregar a lista de desejos.</p>';
  }
}

function libraryCard(entry) {
  return `
    <article class="game">
      <div class="game__genre">comprado</div>
      <div class="game__title">${esc(entry.title)}</div>
      <div class="game__price">${money(entry.pricePaidCents)}</div>
      <span class="badge badge--own">✓ Na biblioteca</span>
    </article>`;
}

function wishlistCard(item) {
  const id = esc(item.gameId);
  return `
    <article class="game">
      <div class="game__genre">desejado</div>
      <div class="game__title">${esc(item.title)}</div>
      <div class="game__actions">
        <button class="btn btn--neon btn--mini" data-wish-buy="${id}">Comprar</button>
        <button class="btn btn--ghost btn--mini" data-wish-remove="${id}">Remover</button>
      </div>
    </article>`;
}

document.getElementById("desejos-grid").addEventListener("click", async (event) => {
  const buy = event.target.closest("[data-wish-buy]");
  const remove = event.target.closest("[data-wish-remove]");
  const pid = state.currentId;
  if (!pid) return;

  if (buy) {
    buy.disabled = true;
    try {
      await apiPost(`/api/players/${pid}/purchases`, { gameId: buy.dataset.wishBuy });
      flashToast("Compra concluída!");
      await refreshCurrentPlayer();
      loadCollection();
    } catch (err) {
      buy.disabled = false;
      document.getElementById("colecao-status").innerHTML = alertHtml(err.message);
    }
  } else if (remove) {
    try {
      await apiDelete(`/api/players/${pid}/wishlist/${remove.dataset.wishRemove}`);
      loadCollection();
    } catch (err) {
      document.getElementById("colecao-status").innerHTML = alertHtml(err.message);
    }
  }
});

document.getElementById("reload-colecao").addEventListener("click", loadCollection);

// ===========================================================================
// AMIGOS
// ===========================================================================
const amigosGrid = document.getElementById("amigos-grid");

async function loadFriends() {
  const status = document.getElementById("amigos-status");
  status.innerHTML = "";
  amigosGrid.innerHTML = "";

  const pid = state.currentId;
  if (!pid) {
    status.innerHTML = alertHtml("Crie um jogador para ter amigos.");
    document.getElementById("amigo-select").innerHTML = "";
    return;
  }

  amigosGrid.innerHTML = '<p class="muted">Carregando amigos…</p>';
  let friends = [];
  try {
    const body = await apiGet(`/api/players/${pid}/friends`);
    friends = body.data || [];
    amigosGrid.innerHTML = friends.length
      ? friends.map(friendCard).join("")
      : '<p class="muted">Você ainda não tem amigos. Adicione um abaixo!</p>';
  } catch (err) {
    amigosGrid.innerHTML = "";
    status.innerHTML = alertHtml(err.message);
  }

  // Preenche o seletor com jogadores que ainda não são amigos (e nem você).
  const friendIds = new Set(friends.map((f) => f.id));
  const options = state.players.filter((p) => p.id !== pid && !friendIds.has(p.id));
  const select = document.getElementById("amigo-select");
  select.innerHTML = options.length
    ? options.map((p) => `<option value="${esc(p.id)}">${esc(p.name)}</option>`).join("")
    : '<option value="">Ninguém para adicionar</option>';
}

function friendCard(friend) {
  return `
    <article class="game">
      <div class="game__genre">amigo</div>
      <div class="game__title">${esc(friend.name)}</div>
      <div class="game__actions">
        <button class="btn btn--ghost btn--mini" data-friend-remove="${esc(friend.id)}">Remover</button>
      </div>
    </article>`;
}

document.getElementById("add-amigo-btn").addEventListener("click", async () => {
  const pid = state.currentId;
  const friendId = document.getElementById("amigo-select").value;
  const msg = document.getElementById("amigo-msg");
  msg.className = "msg";
  if (!pid || !friendId) {
    msg.className = "msg err";
    msg.textContent = "Selecione um jogador para adicionar.";
    return;
  }
  msg.textContent = "Adicionando…";
  try {
    await apiPost(`/api/players/${pid}/friends`, { friendId });
    msg.className = "msg ok";
    msg.textContent = "Amigo adicionado!";
    loadFriends();
  } catch (err) {
    msg.className = "msg err";
    msg.textContent = err.message;
  }
});

amigosGrid.addEventListener("click", async (event) => {
  const remove = event.target.closest("[data-friend-remove]");
  if (!remove || !state.currentId) return;
  try {
    await apiDelete(`/api/players/${state.currentId}/friends/${remove.dataset.friendRemove}`);
    loadFriends();
  } catch (err) {
    document.getElementById("amigos-status").innerHTML = alertHtml(err.message);
  }
});

document.getElementById("reload-amigos").addEventListener("click", loadFriends);

// ----- Toast ---------------------------------------------------------------
function flashToast(message) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.add("toast--on");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove("toast--on"), 2600);
}

// ----- Início --------------------------------------------------------------
(async function init() {
  await loadPlayers();
  loadStore();
})();
