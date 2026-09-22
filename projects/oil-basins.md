---
layout: bare
title: "Which geological periods does the world's oil come from?"
permalink: /projects/oil-basins/
---

<style>
  .oil-app {
    --bg: #0d0d0d;
    --bg-panel: #141414;
    --ink: #f0ede6;
    --ink-soft: #9a958c;
    --line: #2e2c28;
    --accent: #fe9929;
    --shadow: 0 6px 24px rgba(0, 0, 0, .55);
    color: var(--ink);
    border: 1px solid var(--line);
    border-radius: 10px;
    overflow: hidden;
    background: var(--bg);
  }

  .oil-topbar {
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: 1.5rem; flex-wrap: wrap;
    padding: .7rem 1.1rem;
    border-bottom: 1px solid var(--line);
    background: linear-gradient(180deg, #171717, #101010);
  }
  .oil-topbar h1 { margin: 0; font-size: 1.2rem; letter-spacing: .2px; font-weight: 700; }
  .oil-topbar .subtitle { margin: .2rem 0 0; font-size: .82rem; color: var(--ink-soft); }
  .oil-controls { display: flex; align-items: center; gap: .5rem; }
  .oil-controls button {
    font: inherit; font-size: .82rem;
    padding: .3rem .75rem; border: 1px solid var(--line);
    background: #1d1d1d; border-radius: 999px; cursor: pointer; color: var(--ink);
  }
  .oil-controls button:hover { background: #262626; border-color: var(--accent); color: var(--accent); }

  /* The panel is a permanent column rather than an overlay. Most of the world's
     oil sits on the right-hand side of the map, so a panel that slid over it
     would cover the Middle East, and one that appeared on click would resize
     the map out from under the circle just clicked. */
  .oil-body { display: flex; align-items: stretch; }
  .oil-stage { position: relative; flex: 1 1 auto; min-width: 0; background: #0d0d0d; }
  .oil-stage video { display: block; width: 100%; height: auto; }
  .oil-stage svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
  .oil-stage.is-live svg { pointer-events: auto; }

  .oil-hit { fill: transparent; stroke: none; cursor: pointer; }
  .oil-stage.is-live .oil-hit:hover { fill: rgba(254, 153, 41, .28); }
  .oil-ring { fill: none; stroke: var(--accent); stroke-width: 2.5; opacity: 0; pointer-events: none; }
  .oil-ring.on { opacity: 1; }

  .oil-panel {
    position: relative;   /* anchors the close button inside the panel */
    flex: 0 0 320px; align-self: stretch;
    background: var(--bg-panel); border-left: 1px solid var(--line);
    overflow-y: auto; padding: 1.1rem 1.15rem 1.5rem;
  }
  .oil-panel .close {
    position: absolute; top: .5rem; right: .7rem; border: none; background: none;
    font-size: 1.4rem; line-height: 1; cursor: pointer; color: var(--ink-soft);
  }
  .oil-panel .close:hover { color: var(--accent); }
  .oil-empty { font-size: .84rem; color: var(--ink-soft); line-height: 1.5; }
  .oil-empty b { color: var(--ink); }
  .oil-panel h2 { margin: 0 0 .1rem; font-size: 1.15rem; padding-right: 1.4rem; font-weight: 700; }
  .oil-panel .where { font-size: .84rem; color: var(--accent); margin-bottom: .7rem; }
  .oil-panel dl { margin: 0 0 .9rem; font-size: .82rem; }
  .oil-panel dt { color: var(--ink-soft); margin-top: .5rem; }
  .oil-panel dd { margin: 0; font-weight: 600; }
  .oil-bar { display: flex; height: 9px; border-radius: 5px; overflow: hidden; margin: .35rem 0 .2rem; background: #2e2c28; }
  .oil-bar i { display: block; height: 100%; }
  .oil-split { font-size: .74rem; color: var(--ink-soft); }
  .oil-ints { list-style: none; padding: 0; margin: .2rem 0 0; font-size: .78rem; }
  .oil-ints li { display: flex; align-items: center; gap: .45rem; margin-bottom: .2rem; }
  .oil-ints span.sw { width: 11px; height: 11px; border-radius: 50%; border: 1px solid rgba(255,255,255,.35); flex: none; }
  .oil-hint {
    font-size: .78rem; color: var(--ink); line-height: 1.5;
    padding: .55rem 1.1rem; border-top: 1px solid var(--line); background: var(--bg-panel);
  }
  /* The site theme sets `body a { color: ... !important }`, so matching that
     is the only way to keep these credits black. */
  .oil-app .oil-hint a {
    color: var(--ink) !important;
    text-decoration: underline; text-underline-offset: 2px; text-decoration-color: #5f5a52;
  }
  .oil-app .oil-hint a:hover { color: var(--accent) !important; text-decoration-color: var(--accent); }

  @media (max-width: 860px) {
    .oil-body { flex-direction: column; }
    .oil-panel { flex: 1 1 auto; border-left: none; border-top: 1px solid var(--line); }
  }
</style>

<div class="oil-app" id="oil-app">
  <div class="oil-topbar">
    <div>
      <h1>Which geological periods does the world's oil come from?</h1>
      <p class="subtitle">A map of global oil basins over 500 million years of geology.</p>
    </div>
    <div class="oil-controls">
      <button type="button" id="oil-replay">Replay</button>
    </div>
  </div>

  <div class="oil-body">
    <div class="oil-stage" id="oil-stage">
      <!-- The ?v= tag is a cache buster. Browsers hold on to video hard, so
           bump it whenever the animation is re-rendered or returning visitors
           keep seeing the old clip. -->
      <video id="oil-animation" autoplay muted playsinline
             poster="{{ site.github.url }}/assets/img/projects/interval_present.png?v=2">
        <source src="{{ site.github.url }}/assets/img/projects/oil_history.mp4?v=2" type="video/mp4">
        <img src="{{ site.github.url }}/assets/img/projects/oil_history.gif?v=2"
             alt="Animated world map running from 460 million years ago to the present, with petroleum provinces appearing as their source rocks form.">
      </video>
      <svg id="oil-overlay" viewBox="0 0 2500 1480" preserveAspectRatio="none" aria-hidden="true"></svg>
    </div>
    <aside class="oil-panel" id="oil-panel" aria-live="polite"></aside>
  </div>

  <div class="oil-hint" id="oil-hint">
    Province outlines from the
    <a href="https://www.sciencebase.gov/catalog/item/60ad2fd7d34e4043c850edb3">USGS World Petroleum Assessment</a>.
    Field data scraped from
    <a href="https://en.wikipedia.org/wiki/List_of_oil_fields">Wikipedia</a>.
    Source-rock ages from
    <a href="https://www.searchanddiscovery.com/documents/animator/klemme2.htm">Klemme &amp; Ulmishek (1991)</a>.
    Plate tectonics based on
    <a href="https://doi.org/10.1016/j.earscirev.2020.103477">Merdith et al. (2021)</a>.
    Attribution of interval fractions by Claude based on a lit review.
  </div>
</div>

<script>
(function () {
  var video   = document.getElementById('oil-animation');
  var stage   = document.getElementById('oil-stage');
  var overlay = document.getElementById('oil-overlay');
  var panel   = document.getElementById('oil-panel');
  var replay  = document.getElementById('oil-replay');
  if (!video || !overlay) { return; }

  var SVGNS = 'http://www.w3.org/2000/svg';
  var data = null, ring = null;

  function fmt(n) {
    if (n === null || n === undefined) { return '—'; }
    return (n >= 100 ? Math.round(n) : Math.round(n * 10) / 10).toLocaleString();
  }

  var EMPTY_PLAYING = '<p class="oil-empty">The animation runs from 460 million ' +
    'years ago to today. Basins appear when their source rock was laid down, then ' +
    'drift with the continents.</p>';
  var EMPTY_LIVE = '<p class="oil-empty"><b>Click on any basin for more info!</b></p>';

  function closePanel() {
    panel.innerHTML = stage.classList.contains('is-live') ? EMPTY_LIVE : EMPTY_PLAYING;
    if (ring) { ring.classList.remove('on'); }
  }

  function showPanel(h, hit) {
    var pastPct = h.total > 0 ? (100 * h.past / h.total) : 0;
    var ints = h.intervals.map(function (p) {
      return '<li><span class="sw" style="background:' + p.color + '"></span>' +
             p.interval + ': ' + fmt(p.bbl) + ' BBO</li>';
    }).join('');

    panel.innerHTML =
      '<button class="close" type="button" aria-label="Close">&times;</button>' +
      '<h2>' + h.name + '</h2>' +
      '<div class="where">' + h.city + ', ' + h.country + '</div>' +
      '<dl>' +
        '<dt>Discovered</dt><dd>' + (h.discovered || '—') + '</dd>' +
        '<dt>Major fields</dt><dd>' + (h.fields || '—') + '</dd>' +
        '<dt>Recoverable oil (past and future)</dt>' +
        '<dd>' + fmt(h.total) + ' billion barrels' +
          '<div class="oil-bar">' +
            '<i style="width:' + pastPct + '%;background:#cc4c02"></i>' +
            '<i style="width:' + (100 - pastPct) + '%;background:#fec44f"></i>' +
          '</div>' +
          '<div class="oil-split">' + fmt(h.past) + ' already produced, ' +
            fmt(h.future) + ' still to come</div>' +
        '</dd>' +
        '<dt>Source rock</dt><dd><ul class="oil-ints">' + ints + '</ul></dd>' +
      '</dl>';

    panel.querySelector('.close').addEventListener('click', closePanel);

    if (ring) { ring.remove(); }
    ring = document.createElementNS(SVGNS, 'circle');
    ring.setAttribute('class', 'oil-ring on');
    ring.setAttribute('cx', hit.getAttribute('cx'));
    ring.setAttribute('cy', hit.getAttribute('cy'));
    ring.setAttribute('r', Number(hit.getAttribute('r')) + 4);
    overlay.appendChild(ring);
  }

  function buildOverlay() {
    var W = data.width, H = data.height;
    overlay.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    // Biggest first, so the smaller circles of a crowded region such as the
    // Persian Gulf end up painted on top and are the ones you hover.
    data.hotspots.forEach(function (h) {
      var c = document.createElementNS(SVGNS, 'circle');
      c.setAttribute('class', 'oil-hit');
      c.setAttribute('cx', h.x * W);
      c.setAttribute('cy', h.y * H);
      c.setAttribute('r', Math.max(h.r * W, 9));
      var t = document.createElementNS(SVGNS, 'title');
      t.textContent = h.name + ' · ' + fmt(h.total) + ' billion barrels';
      c.appendChild(t);
      h._el = c;
      overlay.appendChild(c);
    });
  }

  // Hit-test by hand rather than relying on which circle happens to be on top.
  // Basins overlap heavily around the Persian Gulf. Among the circles covering
  // the click, take the one whose centre is nearest, which is what "the circle
  // I am pointing at" means: the middle of a big basin still selects the big
  // basin, while the visible rim of a small one selects the small one.
  function pick(evt) {
    if (!data) { return null; }
    var box = overlay.getBoundingClientRect();
    if (!box.width || !box.height) { return null; }
    var px = (evt.clientX - box.left) / box.width * data.width;
    var py = (evt.clientY - box.top) / box.height * data.height;
    var best = null, bestD = Infinity;
    data.hotspots.forEach(function (h) {
      var r = Math.max(h.r * data.width, 9);
      var dx = px - h.x * data.width, dy = py - h.y * data.height;
      var d2 = dx * dx + dy * dy;
      if (d2 <= r * r && d2 < bestD) { best = h; bestD = d2; }
    });
    return best;
  }

  function goLive() {
    if (!data) { return; }
    stage.classList.add('is-live');
    if (!panel.querySelector('h2')) { closePanel(); }
  }

  video.addEventListener('ended', goLive);
  replay.addEventListener('click', function () {
    stage.classList.remove('is-live');
    closePanel();
    video.currentTime = 0;
    video.play();
  });
  overlay.addEventListener('click', function (e) {
    if (!stage.classList.contains('is-live')) { return; }
    var h = pick(e);
    if (h) { showPanel(h, h._el); } else { closePanel(); }
  });

  panel.innerHTML = EMPTY_PLAYING;

  fetch('{{ site.github.url }}/assets/data/oil_hotspots.json')
    .then(function (r) { return r.json(); })
    .then(function (j) {
      data = j;
      buildOverlay();
      // If autoplay was blocked or the clip already finished, go straight to
      // the clickable state rather than waiting for an 'ended' that never fires.
      if (video.ended || video.paused) { goLive(); }
    })
    .catch(function () {
      panel.innerHTML = '<p class="oil-empty">The basin data could not be loaded.</p>';
    });
})();
</script>
