/* 움직이는 그림 영상 플레이어
 * GV.init({root:'#gv', scenes:[{dur:초, n:번호, cap:'큰 글', sub:'작은 글', warn:true/false, svg:'<svg>…</svg>'}]})
 * - 자동 재생(한 번), 끝나면 [다시 보기]. 일시정지·이전·다음·진행 막대 클릭·스페이스/좌우 키.
 */
(function () {
  function el(h) { var d = document.createElement('div'); d.innerHTML = h.trim(); return d.firstChild; }
  window.GV = {
    init: function (cfg) {
      var root = typeof cfg.root === 'string' ? document.querySelector(cfg.root) : cfg.root;
      var S = cfg.scenes, idx = 0, elapsed = 0, playing = false, timer = null, TICK = 100;
      var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
      root.innerHTML =
        '<div class="gv-card"><div class="gv-stage"><div class="gv-chip"></div>' +
        S.map(function (s) { return '<div class="gv-scene">' + s.svg + '</div>'; }).join('') +
        '<div class="gv-over"><b>▶</b><span>눌러서 시작</span></div></div>' +
        '<div class="gv-cap"><div class="gv-n"></div><div><div class="gv-ct"></div><div class="gv-cs"></div></div></div>' +
        '<div class="gv-ctl"><button class="gv-btn" data-a="prev" title="이전">⏮</button><button class="gv-btn main" data-a="play" title="재생/멈춤">⏸</button>' +
        '<button class="gv-btn" data-a="next" title="다음">⏭</button><button class="gv-btn" data-a="re" title="처음부터">↺</button>' +
        '<div class="gv-bar">' + S.map(function (s, i) { return '<div class="gv-seg' + (s.warn ? ' w' : '') + '" data-i="' + i + '"><i></i></div>'; }).join('') + '</div></div></div>';
      var scenes = root.querySelectorAll('.gv-scene'), segs = root.querySelectorAll('.gv-seg'), chip = root.querySelector('.gv-chip'),
        cap = root.querySelector('.gv-cap'), n = root.querySelector('.gv-n'), ct = root.querySelector('.gv-ct'), cs = root.querySelector('.gv-cs'),
        over = root.querySelector('.gv-over'), pbtn = root.querySelector('[data-a=play]'), card = root.querySelector('.gv-card');

      function show(i, keep) {
        idx = Math.max(0, Math.min(S.length - 1, i)); elapsed = 0;
        scenes.forEach(function (sc, k) { sc.classList.toggle('on', k === idx); });
        void card.offsetWidth;
        var s = S[idx];
        chip.textContent = (idx + 1) + ' / ' + S.length;
        cap.classList.toggle('warn', !!s.warn);
        n.textContent = s.n || (idx + 1); ct.innerHTML = s.cap; cs.innerHTML = s.sub || ''; cs.style.display = s.sub ? '' : 'none';
        segs.forEach(function (g, k) { g.classList.toggle('done', k < idx); g.firstChild.style.width = k < idx ? '100%' : '0'; });
        over.classList.remove('show');
      }
      function tick() {
        elapsed += TICK / 1000;
        var s = S[idx], p = Math.min(1, elapsed / s.dur);
        segs[idx].firstChild.style.width = (p * 100) + '%';
        if (elapsed >= s.dur) {
          if (idx < S.length - 1) show(idx + 1);
          else { segs[idx].firstChild.style.width = '100%'; stop(); over.querySelector('span').textContent = '다시 보기'; over.classList.add('show'); }
        }
      }
      function play() { if (playing) return; playing = true; card.classList.remove('gv-paused'); pbtn.textContent = '⏸'; over.classList.remove('show'); timer = setInterval(tick, TICK); }
      function stop() { playing = false; clearInterval(timer); card.classList.add('gv-paused'); pbtn.textContent = '▶'; }
      function go(i) { var was = playing; show(i); if (was) { /* 계속 재생 */ } else { play(); } }
      root.addEventListener('click', function (e) {
        var b = e.target.closest('[data-a],.gv-seg,.gv-over'); if (!b) return;
        if (b.classList.contains('gv-over')) { go(idx >= S.length - 1 && elapsed >= S[idx].dur ? 0 : idx); return; }
        if (b.classList.contains('gv-seg')) { go(+b.getAttribute('data-i')); return; }
        var a = b.getAttribute('data-a');
        if (a === 'play') { playing ? stop() : play(); }
        else if (a === 'prev') go(idx - 1);
        else if (a === 'next') go(idx + 1);
        else if (a === 're') go(0);
      });
      root.querySelector('.gv-stage').addEventListener('click', function (e) { if (e.target.closest('.gv-over')) return; playing ? stop() : play(); });
      document.addEventListener('keydown', function (e) {
        if (/input|textarea|select/i.test((e.target.tagName || ''))) return;
        if (e.key === ' ') { e.preventDefault(); playing ? stop() : play(); }
        else if (e.key === 'ArrowRight') go(idx + 1);
        else if (e.key === 'ArrowLeft') go(idx - 1);
      });
      document.addEventListener('visibilitychange', function () { if (document.hidden && playing) stop(); });
      show(0);
      var qs = /[?&]scene=(\d+)/.exec(location.search);   // 점검용: ?scene=3 → 3번 장면을 완성된 모습으로 멈춰 보기
      if (qs) { show(+qs[1] - 1); stop(); setTimeout(function () { document.getAnimations().forEach(function (an) { try { an.finish(); } catch (e) {} }); }, 60); return; }
      if (reduce) { stop(); over.classList.add('show'); } else { setTimeout(play, 350); }
    }
  };
})();
