/* ZZZeroUID 控制台页：抽卡 / 角色列表 + PIL 预览 */
(function () {
  const P = window.GsHubPlugin;
  const state = {
    players: [],
    uid: '',
    tab: 'gacha',
    pool: '',
    gacha: null,
    chars: [],
    previewUrl: '',
    previewSeq: 0,
  };

  const $ = (id) => document.getElementById(id);

  function t(key, vars) {
    return P ? P.t(key, vars) : key;
  }

  function tokenSrc(path) {
    const token = P && P.token ? P.token : '';
    const join = path.indexOf('?') >= 0 ? '&' : '?';
    return token ? path + join + 'token=' + encodeURIComponent(token) : path;
  }

  function showError(err) {
    const msg = err && err.message ? err.message : String(err);
    $('empty-main').hidden = false;
    $('workspace').hidden = true;
    $('empty-main').textContent = msg.indexOf('401') >= 0 || msg.indexOf('未授权') >= 0
      ? t('loginRequired')
      : t('error') + ' · ' + msg;
  }

  function fillStatic() {
    $('title').textContent = t('title');
    document.title = t('title');
    $('subtitle').textContent = t('subtitle');
    $('players-label').textContent = t('players');
    $('search').placeholder = t('searchUid');
    $('tab-gacha').textContent = t('tabGacha');
    $('tab-chars').textContent = t('tabChars');
    $('btn-preview-gacha').textContent = t('previewCard');
    $('btn-del-gacha').textContent = t('deleteGacha');
    $('modal-close').textContent = t('close');
    $('modal-loading-text').textContent = t('loading');
    $('empty-main').textContent = t('pickPlayer');
  }

  function renderPlayers() {
    const q = $('search').value.trim();
    const box = $('player-list');
    box.innerHTML = '';
    const rows = state.players.filter((p) => !q || String(p.uid).indexOf(q) >= 0);
    if (!rows.length) {
      const empty = document.createElement('div');
      empty.className = 'hint';
      empty.textContent = t('emptyPlayers');
      box.appendChild(empty);
      return;
    }
    rows.forEach((p) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'player' + (p.uid === state.uid ? ' active' : '');
      btn.innerHTML =
        '<div class="uid">' + p.uid + '</div>' +
        '<div class="meta">' + t('gachaTotal') + ' ' + p.gacha_total +
        ' · ' + t('chars') + ' ' + p.char_count + '</div>';
      btn.addEventListener('click', () => selectPlayer(p.uid));
      box.appendChild(btn);
    });
  }

  function stat(label, value) {
    return '<div class="stat"><span>' + label + '</span><b>' + value + '</b></div>';
  }

  function renderGacha() {
    const data = state.gacha;
    const stats = $('gacha-stats');
    const pools = $('pools');
    const body = $('gacha-body');
    if (!data) {
      stats.innerHTML = '';
      pools.innerHTML = '';
      body.innerHTML = '<p class="empty">' + t('noGacha') + '</p>';
      return;
    }
    let sCount = 0;
    (data.pools || []).forEach((p) => { sCount += p.s_count; });
    stats.innerHTML =
      stat(t('gachaTotal'), data.gacha_total) +
      stat(t('sCount'), sCount) +
      stat(t('updated'), data.data_time || '—');
    pools.innerHTML = '';
    (data.pools || []).forEach((p) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'pool' + (state.pool === p.name ? ' active' : '');
      b.textContent = p.name + ' · ' + p.total;
      b.addEventListener('click', () => {
        state.pool = p.name;
        renderGacha();
      });
      pools.appendChild(b);
    });
    const current = (data.pools || []).find((p) => p.name === state.pool) || (data.pools || [])[0];
    if (!current) {
      body.innerHTML = '<p class="empty">' + t('noGacha') + '</p>';
      return;
    }
    state.pool = current.name;
    let html = '<div class="stats">' +
      stat(t('poolTotal'), current.total) +
      stat(t('sCount'), current.s_count) +
      stat(t('remain'), current.remain) +
      '</div><table class="records"><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Rank</th><th>Time</th></tr></thead><tbody>';
    current.records.forEach((r) => {
      const cls = r.rank_type === '4' ? 'rank-s' : r.rank_type === '3' ? 'rank-a' : '';
      html += '<tr><td>' + r.id + '</td><td class="' + cls + '">' + r.name +
        '</td><td>' + r.item_type + '</td><td class="' + cls + '">' + r.rank_type +
        '</td><td>' + r.time + '</td></tr>';
    });
    html += '</tbody></table>';
    body.innerHTML = html;
  }

  function renderChars() {
    $('char-stats').innerHTML = stat(t('chars'), state.chars.length);
    const grid = $('char-grid');
    grid.innerHTML = '';
    if (!state.chars.length) {
      grid.innerHTML = '<p class="empty">' + t('noChars') + '</p>';
      return;
    }
    state.chars.forEach((c) => {
      const card = document.createElement('article');
      card.className = 'char' + (c.rarity === 'S' ? ' s' : '');
      const art = document.createElement('div');
      art.className = 'art';
      art.style.backgroundImage = 'url("' + tokenSrc('/api/zzzerouid/assets/avatar/' + c.id) + '")';
      const body = document.createElement('div');
      body.className = 'body';
      body.innerHTML =
        '<div class="name">' + (c.full_name || c.name) + '</div>' +
        '<div class="tags">' + t('level') + c.level +
        ' · ' + t('mindscape') + ' ' + c.rank +
        (c.weapon_name ? ' · ' + c.weapon_name : '') + '</div>' +
        '<div class="toolbar" style="margin-top:8px">' +
        '<button type="button" class="btn gold preview">' + t('previewChar') + '</button>' +
        '<button type="button" class="btn danger del">' + t('deleteChar') + '</button></div>';
      body.querySelector('.preview').addEventListener('click', (ev) => {
        ev.stopPropagation();
        openPreview('/api/zzzerouid/players/' + state.uid + '/characters/' + c.id + '/preview');
      });
      body.querySelector('.del').addEventListener('click', (ev) => {
        ev.stopPropagation();
        if (!window.confirm(t('confirmDelete'))) return;
        P.api('/api/zzzerouid/players/' + state.uid + '/characters/' + c.id, { method: 'DELETE' })
          .then(loadChars)
          .then(loadPlayers)
          .catch(showError);
      });
      card.appendChild(art);
      card.appendChild(body);
      grid.appendChild(card);
    });
  }

  function setTab(tab) {
    state.tab = tab;
    $('tab-gacha').classList.toggle('active', tab === 'gacha');
    $('tab-chars').classList.toggle('active', tab === 'chars');
    $('panel-gacha').hidden = tab !== 'gacha';
    $('panel-chars').hidden = tab !== 'chars';
  }

  async function selectPlayer(uid) {
    state.uid = uid;
    state.pool = '';
    $('empty-main').hidden = true;
    $('workspace').hidden = false;
    renderPlayers();
    try {
      await Promise.all([loadGacha(), loadChars()]);
    } catch (err) {
      showError(err);
    }
  }

  async function loadPlayers() {
    state.players = await P.api('/api/zzzerouid/players');
    renderPlayers();
  }

  async function loadGacha() {
    try {
      state.gacha = await P.api('/api/zzzerouid/players/' + state.uid + '/gacha');
    } catch (err) {
      state.gacha = null;
      if (err && String(err.message).indexOf('not found') < 0) throw err;
    }
    renderGacha();
  }

  async function loadChars() {
    try {
      state.chars = await P.api('/api/zzzerouid/players/' + state.uid + '/characters');
    } catch (err) {
      state.chars = [];
      if (err && String(err.message).indexOf('not found') < 0) throw err;
    }
    renderChars();
  }

  function closePreview() {
    state.previewSeq += 1;
    $('modal').classList.remove('show');
    $('modal-loading').hidden = true;
    $('modal-error').hidden = true;
    const img = $('modal-img');
    img.onload = null;
    img.onerror = null;
    img.hidden = true;
    img.removeAttribute('src');
    if (state.previewUrl) {
      URL.revokeObjectURL(state.previewUrl);
      state.previewUrl = '';
    }
  }

  async function openPreview(path) {
    const seq = state.previewSeq + 1;
    state.previewSeq = seq;
    const modal = $('modal');
    const img = $('modal-img');
    const loading = $('modal-loading');
    const errorEl = $('modal-error');
    if (state.previewUrl) {
      URL.revokeObjectURL(state.previewUrl);
      state.previewUrl = '';
    }
    img.onload = null;
    img.onerror = null;
    img.hidden = true;
    img.removeAttribute('src');
    errorEl.hidden = true;
    errorEl.textContent = '';
    loading.hidden = false;
    modal.classList.add('show');
    try {
      const blob = await P.blob(path);
      if (seq !== state.previewSeq) return;
      const url = URL.createObjectURL(blob);
      state.previewUrl = url;
      await new Promise((resolve, reject) => {
        img.onload = () => resolve();
        img.onerror = () => reject(new Error(t('previewFailed')));
        img.src = url;
      });
      if (seq !== state.previewSeq) return;
      loading.hidden = true;
      img.hidden = false;
    } catch (err) {
      if (seq !== state.previewSeq) return;
      loading.hidden = true;
      img.hidden = true;
      errorEl.hidden = false;
      errorEl.textContent = t('previewFailed');
    }
  }

  function bind() {
    $('search').addEventListener('input', renderPlayers);
    $('tab-gacha').addEventListener('click', () => setTab('gacha'));
    $('tab-chars').addEventListener('click', () => setTab('chars'));
    $('btn-preview-gacha').addEventListener('click', () => {
      if (!state.uid) return;
      openPreview('/api/zzzerouid/players/' + state.uid + '/gacha/preview');
    });
    $('btn-del-gacha').addEventListener('click', () => {
      if (!state.uid) return;
      if (!window.confirm(t('confirmDelete'))) return;
      P.api('/api/zzzerouid/players/' + state.uid + '/gacha', { method: 'DELETE' })
        .then(loadGacha)
        .then(loadPlayers)
        .catch(showError);
    });
    $('modal-close').addEventListener('click', closePreview);
    $('modal').addEventListener('click', (ev) => {
      if (ev.target.id === 'modal') closePreview();
    });
  }

  P.ready.then(function () {
    fillStatic();
    bind();
    return loadPlayers();
  }).catch(showError);
})();
