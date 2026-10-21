/* 복사하는 방법 — 움직이는 그림 영상 장면 (guide-copy.html 안내와 같은 순서·같은 말) */
(function () {
  var K = .55;                                   // 윗면(위에서 비스듬히 본 면) 기울기
  function P(u, v) { return (10 + u + K * v).toFixed(1) + ',' + (-38 - v).toFixed(1); }
  function poly(u, v, w, d) { return P(u, v) + ' ' + P(u + w, v) + ' ' + P(u + w, v + d) + ' ' + P(u, v + d); }
  function A(an, d, du, extra) { return 'class="a" style="--an:' + an + ';--d:' + (d || 0) + 's;--du:' + (du || .6) + 's;' + (extra || '') + '"'; }
  var F = "font-family:'Noto Sans KR',sans-serif;font-weight:900;";

  // 종이(글씨가 보이는 면이 위)
  function paper(u, v, w, d, o) {
    o = o || {};
    var s = '<polygon points="' + poly(u, v, w, d) + '" fill="#fff" stroke="#94A3B8" stroke-width="2.5" stroke-linejoin="round"/>';
    for (var i = 1; i <= 4; i++) {
      var vv = v + d * (0.18 * i + .02), a = P(u + w * .14, vv).split(','), b = P(u + w * (i % 2 ? .86 : .66), vv).split(',');
      s += '<line x1="' + a[0] + '" y1="' + a[1] + '" x2="' + b[0] + '" y2="' + b[1] + '" stroke="#64748B" stroke-width="3" stroke-linecap="round"/>';
    }
    if (o.edge) { var p = P(u, v).split(','), q = P(u, v + d).split(','); s += '<line x1="' + p[0] + '" y1="' + p[1] + '" x2="' + q[0] + '" y2="' + q[1] + '" stroke="#1B8AC4" stroke-width="5" stroke-linecap="round"/>'; }
    return s;
  }
  // 복합기 (왼쪽 위 모서리가 0,0 / 폭 420)
  function mfp(o) {
    o = o || {};
    var s = '<ellipse cx="210" cy="184" rx="224" ry="15" fill="rgba(30,45,80,.13)"/>' +
      '<rect x="0" y="0" width="420" height="170" rx="16" fill="#F3F6FA" stroke="#8795A8" stroke-width="3"/>' +
      '<rect x="22" y="106" width="258" height="46" rx="8" fill="#DCE4EE" stroke="#A5B2C3" stroke-width="2"/>' +
      '<rect x="308" y="14" width="96" height="78" rx="9" fill="#1F2A3A"/>' +
      '<rect x="316" y="22" width="38" height="28" rx="5" fill="#018FFB"/><rect x="358" y="22" width="38" height="28" rx="5" fill="#22B24C"/>' +
      '<rect x="316" y="54" width="38" height="28" rx="5" fill="#12BDB0"/><rect x="358" y="54" width="38" height="28" rx="5" fill="#F3732C"/>' +
      '<rect x="0" y="-40" width="420" height="42" rx="11" fill="#E1E8F1" stroke="#8795A8" stroke-width="3"/>' +
      '<line x1="14" y1="-8" x2="406" y2="-8" stroke="#B6C3D3" stroke-width="2"/>' +
      '<polygon points="' + poly(0, 0, 236, 80) + '" fill="#CFD9E6" stroke="#8795A8" stroke-width="2.5" stroke-linejoin="round"/>' +
      (o.slotArrow ? '' : '');
    return s;
  }
  function guards(open, anim) {            // 문서 가드(주황 막대 2개)
    var fy = open ? 0 : 1;
    var front = '<polygon points="' + poly(0, -4, 236, 5) + '" fill="#F3732C"/>';
    var back = '<polygon points="' + poly(0, 68 + 12, 236, 5) + '" fill="#F3732C"/>';
    return '<g ' + (anim ? A('gvMove', anim.d, anim.du, '--fx:0px;--fy:0px;--tx:3.3px;--ty:-6px') : '') + '>' + front + '</g>' +
      '<g ' + (anim ? A('gvMove', anim.d, anim.du, '--fx:0px;--fy:0px;--tx:-6px;--ty:12px') : '') + '>' + back + '</g>';
  }
  function pill(x, y, w, text, color, d) {
    return '<g ' + A('gvPop', d, .45) + '><rect x="' + (x - w / 2) + '" y="' + (y - 26) + '" width="' + w + '" height="52" rx="26" fill="' + color + '"/><text x="' + x + '" y="' + (y + 9) + '" text-anchor="middle" fill="#fff" style="' + F + 'font-size:25px">' + text + '</text></g>';
  }
  function zcard(x, y, w, h, inner, d, color) {
    return '<g ' + A('gvPop', d, .5) + '><rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="18" fill="#fff" stroke="' + (color || '#E3182D') + '" stroke-width="5"/>' + inner + '</g>';
  }
  function finger(x, y, d, tx, ty) {      // 손가락이 이동해서 누르기
    return '<g ' + A('gvMoveIn', d, .7, '--fx:' + (tx || 60) + 'px;--fy:' + (ty || 50) + 'px;--tx:0px;--ty:0px') + '><text x="' + x + '" y="' + y + '" font-size="44">👆</text></g>';
  }
  function ripple(cx, cy, d, color) {
    return '<circle cx="' + cx + '" cy="' + cy + '" r="30" fill="none" stroke="' + (color || '#E3182D') + '" stroke-width="5" ' + A('gvRipple', d, .7, 'opacity:0') + '/>';
  }
  function btn(x, y, w, h, text, fill, size, d) {
    return '<g><rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="12" fill="' + fill + '"/><text x="' + (x + w / 2) + '" y="' + (y + h / 2 + (size || 22) * .35) + '" text-anchor="middle" fill="#fff" style="' + F + 'font-size:' + (size || 22) + 'px">' + text + '</text></g>';
  }
  function svg(inner) { return '<svg viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">' + inner + '</svg>'; }
  function place(x, y, s, inner) { return '<g transform="translate(' + x + ',' + y + ') scale(' + (s || 1) + ')">' + inner + '</g>'; }
  function check(cx, cy, d) {
    return '<g ' + A('gvPop', d, .5) + '><circle cx="' + cx + '" cy="' + cy + '" r="38" fill="#22B24C"/><path d="M' + (cx - 18) + ' ' + cy + 'l12 14 24-28" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" pathLength="1" style="stroke-dasharray:1;stroke-dashoffset:1;animation:gvDraw .5s ease-out ' + (d + .15) + 's both"/></g>';
  }
  function xmark(cx, cy, r, d) {
    return '<g ' + A('gvPop', d, .45) + '><circle cx="' + cx + '" cy="' + cy + '" r="' + r + '" fill="#E3182D"/><path d="M' + (cx - r * .45) + ' ' + (cy - r * .45) + 'l' + (r * .9) + ' ' + (r * .9) + 'M' + (cx + r * .45) + ' ' + (cy - r * .45) + 'l' + (-r * .9) + ' ' + (r * .9) + '" stroke="#fff" stroke-width="' + (r * .26) + '" stroke-linecap="round"/></g>';
  }

  // ───── 장면 ─────
  var scenes = [];

  // 1. 원본을 ADF에 올리기 (글씨가 위로)
  scenes.push({
    dur: 7, cap: '먼저 <b>원본</b>을 복합기 위쪽 <b>원본 넣는 곳(ADF)</b>에 올려요', sub: '<b>복사할 내용이 위로 보이게</b> 올려요.',
    svg: svg(
      place(40, 232, .98, mfp() +
        '<g ' + A('gvMoveIn', .4, 1.1, '--fx:-150px;--fy:-80px;--tx:0px;--ty:0px') + '>' + paper(64, 6, 50, 66) + '</g>' +
        guards(true)) +
      '<g ' + A('gvPop', 1.6, .5) + '><rect x="250" y="96" width="250" height="56" rx="28" fill="#1B8AC4"/><text x="375" y="134" text-anchor="middle" fill="#fff" style="' + F + 'font-size:28px">👀 글씨가 위로!</text></g>' +
      '<g ' + A('gvFade', 2.2, .5) + '><rect x="40" y="30" width="270" height="52" rx="26" fill="#fff" stroke="#1B8AC4" stroke-width="4"/><text x="175" y="65" text-anchor="middle" fill="#1B8AC4" style="' + F + 'font-size:25px">원본 넣는 곳 (ADF)</text></g>' +
      zcard(530, 60, 250, 150, '<text x="655" y="100" text-anchor="middle" fill="#111827" style="' + F + 'font-size:30px">A4</text>' +
        '<g transform="translate(552,118)"><polygon points="0,0 40,0 40,60 0,60" fill="#fff" stroke="#94A3B8" stroke-width="2.5"/><line x1="0" y1="0" x2="0" y2="60" stroke="#1B8AC4" stroke-width="7"/></g>' +
        '<text x="604" y="156" fill="#1B8AC4" style="' + F + 'font-size:22px">긴 쪽 ← 먼저</text>', 3.2, '#1B8AC4') +
      zcard(530, 232, 250, 150, '<text x="655" y="272" text-anchor="middle" fill="#111827" style="' + F + 'font-size:30px">B4 · A3</text>' +
        '<g transform="translate(552,298)"><polygon points="0,0 62,0 62,38 0,38" fill="#fff" stroke="#94A3B8" stroke-width="2.5"/><line x1="0" y1="0" x2="0" y2="38" stroke="#1B8AC4" stroke-width="7"/></g>' +
        '<text x="624" y="326" fill="#1B8AC4" style="' + F + 'font-size:21px">짧은 쪽 ← 먼저</text>', 4.6, '#1B8AC4')
    )
  });

  // 2. 왼쪽 끝까지 밀고 가드 맞추기
  scenes.push({
    dur: 5, cap: '<b>왼쪽 끝까지 쭉</b> 밀고, 위·아래 <b>가드</b>를 종이에 딱 맞춰요', sub: '살짝만 넣으면 종이가 빨려 들어가지 않아 백지가 나와요.',
    svg: svg(
      place(40, 232, .98, mfp() +
        '<g ' + A('gvMove', .4, 1.2, '--fx:60px;--fy:0px;--tx:0px;--ty:0px') + '>' + paper(4, 6, 50, 66) + '</g>' +
        guards(true, { d: 1.9, du: .9 })) +
      '<g ' + A('gvPop', 1.2, .5) + '><path d="M250 150 L120 150" stroke="#1B8AC4" stroke-width="8" stroke-linecap="round"/><path d="M142 130 L116 150 L142 170" fill="none" stroke="#1B8AC4" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></g>' +
      pill(390, 100, 250, '가드를 딱 맞게', '#F3732C', 2.2) +
      '<g ' + A('gvFade', 3.2, .5) + '><rect x="510" y="120" width="270" height="140" rx="18" fill="#fff" stroke="#22B24C" stroke-width="5"/><text x="645" y="170" text-anchor="middle" fill="#15803D" style="' + F + 'font-size:27px">여러 장이면</text><text x="645" y="208" text-anchor="middle" fill="#15803D" style="' + F + 'font-size:27px">가지런히!</text><text x="645" y="240" text-anchor="middle" fill="#6B7280" style="' + F + 'font-size:21px">(최대 100장)</text></g>')
  });

  // 3. [복사] 누르기
  var kiosk = function (inner) { return '<rect x="470" y="40" width="300" height="250" rx="22" fill="#1F2A3A" stroke="#E3182D" stroke-width="5"/>' + inner; };
  scenes.push({
    dur: 5, cap: '복합기 화면에서 <b>[복사]</b>를 눌러요', sub: '반드시 <b>원본을 먼저 놓은 뒤</b> 눌러요.',
    svg: svg(
      place(30, 250, .86, mfp() + paper(0, 6, 50, 66) + guards(true)) +
      '<g ' + A('gvPop', .2, .5) + '>' + kiosk(
        btn(494, 66, 120, 90, '복사', '#018FFB', 30) + btn(626, 66, 120, 90, '인쇄', '#22B24C', 30) +
        btn(494, 172, 120, 90, '스캔', '#12BDB0', 30) + btn(626, 172, 120, 90, '팩스', '#F3732C', 30)) + '</g>' +
      '<g ' + A('gvTap', 1.9, .5) + '><rect x="490" y="62" width="128" height="98" rx="14" fill="none" stroke="#fff" stroke-width="5" opacity=".9"/></g>' +
      ripple(554, 111, 1.9, '#fff') + finger(540, 150, .6, 70, 60))
  });

  // 4. 설정하고 [시작]
  scenes.push({
    dur: 7, cap: '<b>몇 번 복사할지 · 용지 · 컬러/흑백 · 양면</b>을 정하고 <b>[시작]</b>을 눌러요', sub: '숫자는 <b>몇 번 복사할지</b>예요. 원본이 10장이어도 숫자는 <b>1</b>이면 돼요!',
    svg: svg(
      place(30, 250, .86, mfp() + paper(0, 6, 50, 66) + guards(true)) +
      '<g ' + A('gvPop', .2, .5) + '>' + kiosk(
        '<rect x="488" y="58" width="274" height="34" rx="8" fill="#E8F4FC"/><text x="625" y="82" text-anchor="middle" fill="#1B8AC4" style="' + F + 'font-size:17px">기본복사</text>' +
        '<text x="500" y="124" fill="#fff" style="' + F + 'font-size:17px"></text><rect x="570" y="102" width="70" height="30" rx="7" fill="#fff"/><text x="605" y="125" text-anchor="middle" fill="#111827" style="' + F + 'font-size:19px">1</text>' +
        '<text x="660" y="124" fill="#9CA3AF" style="' + F + 'font-size:14px">부 (장 ✕)</text>' +
        '<text x="500" y="162" fill="#fff" style="' + F + 'font-size:17px">용지 A4 · 컬러 · 단면</text>' +
        btn(560, 206, 150, 62, '시작', '#22B24C', 28)) + '</g>' +
      '<g ' + A('gvPop', 1.2, .5) + '><rect x="562" y="98" width="86" height="40" rx="10" fill="none" stroke="#E3182D" stroke-width="5"/></g>' +
      '<g ' + A('gvFade', 2.2, .4) + '><rect x="556" y="200" width="162" height="74" rx="14" fill="none" stroke="#E3182D" stroke-width="5"/></g>' +
      ripple(635, 237, 3.2, '#fff') + finger(612, 262, 2.4, 60, 60) +
      '<g ' + A('gvPop', 4.4, .5) + '><rect x="30" y="40" width="420" height="104" rx="18" fill="#FEF2F2" stroke="#E3182D" stroke-width="4"/><text x="240" y="82" text-anchor="middle" fill="#B31E16" style="' + F + 'font-size:27px">원본 10장이어도 숫자는 1</text><text x="240" y="122" text-anchor="middle" fill="#B31E16" style="' + F + 'font-size:24px">10으로 바꾸면 100장 복사!</text></g>')
  });

  // 5. 정상: 원본이 들어갔다 나옴
  scenes.push({
    dur: 7, cap: '원본이 기계 안으로 <b>쏙 들어갔다 나오면 정상</b>이에요', sub: '들어간 뒤 자동으로 금액 확인 화면(과금정보)이 나와요.',
    svg: svg(
      place(60, 232, .98, mfp() +
        '<g ' + A('gvMoveOut', .6, 1.6, '--fx:0px;--fy:0px;--tx:-80px;--ty:0px') + '>' + paper(4, 6, 50, 66) + '</g>' +
        guards(true) +
        '<g ' + A('gvMoveIn', 2.6, 1.4, '--fx:-40px;--fy:0px;--tx:30px;--ty:0px') + '><polygon points="40,118 130,118 130,142 40,142" fill="#fff" stroke="#94A3B8" stroke-width="2.5"/><line x1="52" y1="127" x2="110" y2="127" stroke="#64748B" stroke-width="3" stroke-linecap="round"/><line x1="52" y1="135" x2="96" y2="135" stroke="#64748B" stroke-width="3" stroke-linecap="round"/></g>') +
      check(660, 150, 4.0) +
      '<g ' + A('gvFade', 4.4, .5) + '><text x="660" y="230" text-anchor="middle" fill="#15803D" style="' + F + 'font-size:30px">잘 되고 있어요!</text></g>')
  });

  // 6. 경고: 안 들어가면 결제 금지
  scenes.push({
    warn: true, dur: 6, cap: '원본이 안 들어가면 <b>절대 결제하지 마세요!</b>', sub: '화면에서 <b>작업을 취소</b>하고 처음부터 다시 해요. 백지로 복사돼도 환불되지 않아요.',
    svg: svg(
      place(40, 232, .98, mfp() + paper(30, 6, 50, 66) + guards(true)) +
      '<g ' + A('gvPop', .5, .5) + '><rect x="30" y="56" width="290" height="52" rx="26" fill="#E3182D"/><text x="175" y="90" text-anchor="middle" fill="#fff" style="' + F + 'font-size:24px">원본이 그대로예요!</text></g>' +
      '<g ' + A('gvShake', 1.4, .8) + '>' +
      '<rect x="500" y="60" width="270" height="130" rx="18" fill="#fff" stroke="#E3182D" stroke-width="5"/>' +
      btn(520, 84, 230, 84, '결제 ✕', '#9CA3AF', 34) + '</g>' +
      xmark(740, 70, 30, 1.2) +
      '<g ' + A('gvPop', 3.2, .5) + '><rect x="500" y="226" width="270" height="92" rx="18" fill="#fff" stroke="#1B8AC4" stroke-width="5"/>' + btn(520, 244, 230, 56, '작업 취소', '#1B8AC4', 28) + '</g>')
  });

  // 7. 금액 확인
  scenes.push({
    dur: 6, cap: '<b>금액(과금정보)</b>을 꼼꼼히 보고, 맞으면 <b>[확인]</b>', sub: '확인하지 않고 결제해서 생긴 문제는 환불·보상하지 않아요.',
    svg: svg(
      zcard(150, 40, 500, 330, '<path d="M152 104 V60 a18 18 0 0 1 18-18 H630 a18 18 0 0 1 18 18 V104 Z" fill="#EEF1F5"/><text x="180" y="84" fill="#374151" style="' + F + 'font-size:28px">과금정보</text>' +
        '<text x="200" y="178" fill="#374151" style="' + F + 'font-size:30px">총 가격</text><text x="600" y="178" text-anchor="end" fill="#111827" style="' + F + 'font-size:48px">250원</text>' +
        '<text x="200" y="232" fill="#6B7280" style="' + F + 'font-size:23px">컬러 · A4 · 단면 · 1부</text>' + btn(430, 266, 180, 72, '확인', '#1B8AC4', 30), .2, '#9AA8BA') +
      '<g ' + A('gvPop', 1.2, .5) + '><rect x="420" y="258" width="200" height="88" rx="16" fill="none" stroke="#E3182D" stroke-width="5"/></g>' +
      ripple(520, 302, 3.0, '#E3182D') + finger(496, 336, 2.2, 60, 60))
  });

  // 8. 카드 결제
  scenes.push({
    dur: 6, cap: '<b>카드</b>로 결제해요', sub: 'IC 카드는 <b>뒤에 꽂고</b>, 삼성·애플 페이는 <b>앞면 넓은 곳</b>에 대세요. 말소리가 나오면 꽂아요.',
    svg: svg(
      '<rect x="300" y="60" width="260" height="290" rx="24" fill="#F3F6FA" stroke="#8795A8" stroke-width="4"/>' +
      '<rect x="326" y="86" width="208" height="76" rx="12" fill="#1F2A3A"/><text x="430" y="134" text-anchor="middle" fill="#E5E7EB" style="' + F + 'font-size:22px">카드를 꽂아 주세요</text>' +
      '<rect x="326" y="190" width="208" height="64" rx="12" fill="#E8F4FC" stroke="#9CC9E8" stroke-width="3"/><text x="430" y="230" text-anchor="middle" fill="#1B8AC4" style="' + F + 'font-size:22px">📱 삼성·애플 페이</text>' +
      '<rect x="296" y="290" width="12" height="40" rx="4" fill="#6B7A90"/>' +
      '<g ' + A('gvMoveIn', .6, 1.4, '--fx:-130px;--fy:0px;--tx:46px;--ty:0px') + '><rect x="150" y="280" width="154" height="60" rx="10" fill="#1B8AC4"/><rect x="164" y="294" width="30" height="22" rx="4" fill="#FFD835"/><rect x="164" y="324" width="100" height="8" rx="4" fill="#BFE3F6"/></g>' +
      '<g ' + A('gvPop', 2.8, .5) + '><rect x="40" y="110" width="240" height="120" rx="18" fill="#FEF2F2" stroke="#E3182D" stroke-width="4"/><text x="160" y="156" text-anchor="middle" fill="#B31E16" style="' + F + 'font-size:26px">미리 꽂거나</text><text x="160" y="196" text-anchor="middle" fill="#B31E16" style="' + F + 'font-size:26px">중간에 빼지 마세요!</text></g>')
  });

  // 9. 경고: ADF에 넣으면 안 되는 것 → 유리판
  var icon = {
    id: '<rect x="0" y="12" width="84" height="56" rx="8" fill="#fff" stroke="#94A3B8" stroke-width="3"/><circle cx="24" cy="34" r="9" fill="#94A3B8"/><rect x="14" y="46" width="22" height="14" rx="6" fill="#94A3B8"/><line x1="48" y1="30" x2="74" y2="30" stroke="#94A3B8" stroke-width="4" stroke-linecap="round"/><line x1="48" y1="44" x2="68" y2="44" stroke="#94A3B8" stroke-width="4" stroke-linecap="round"/>',
    bank: '<rect x="8" y="2" width="68" height="76" rx="6" fill="#F59E0B"/><rect x="18" y="14" width="48" height="8" rx="3" fill="#fff"/><rect x="18" y="30" width="48" height="6" rx="3" fill="#FDE68A"/><rect x="18" y="44" width="36" height="6" rx="3" fill="#FDE68A"/>',
    pass: '<rect x="8" y="2" width="68" height="76" rx="6" fill="#1E3A8A"/><circle cx="42" cy="34" r="14" fill="none" stroke="#FDE68A" stroke-width="4"/><rect x="24" y="58" width="36" height="6" rx="3" fill="#FDE68A"/>',
    book: '<path d="M2 14 L42 22 L82 14 L82 68 L42 76 L2 68 Z" fill="#fff" stroke="#64748B" stroke-width="3" stroke-linejoin="round"/><line x1="42" y1="22" x2="42" y2="76" stroke="#64748B" stroke-width="3"/>'
  };
  function item(x, key, label, d) {
    return '<g ' + A('gvPop', d, .45) + '><g transform="translate(' + x + ',150)">' + '<rect x="-16" y="-14" width="116" height="136" rx="16" fill="#fff" stroke="#E5E7EB" stroke-width="3"/><g transform="translate(8,6)">' + icon[key] + '</g><text x="42" y="108" text-anchor="middle" fill="#374151" style="' + F + 'font-size:23px">' + label + '</text></g></g>' + xmark(x + 84, 146, 20, d + .5);
  }
  scenes.push({
    warn: true, dur: 7, cap: '<b>신분증 · 통장 · 여권 · 책</b>은 ADF에 넣지 마세요!', sub: '기계가 고장 날 수 있어요. 복합기 덮개를 열고 <b>유리판</b>에 올려요. (아래 &lsquo;유리판 복사&rsquo; 안내를 보세요)',
    svg: svg(
      item(60, 'id', '신분증', .3) + item(230, 'bank', '통장', 1.2) + item(400, 'pass', '여권', 2.1) + item(570, 'book', '책', 3.0) +
      '<g ' + A('gvPop', 4.4, .5) + '><rect x="110" y="316" width="580" height="72" rx="36" fill="#1B8AC4"/><text x="400" y="364" text-anchor="middle" fill="#fff" style="' + F + 'font-size:28px">➜ 덮개를 열고 유리판에 올려요</text></g>')
  });

  // 10. 마무리
  scenes.push({
    dur: 5, cap: '복사가 끝나면 <b>복사본</b>과 <b>원본</b>을 꼭 챙겨 가세요!', sub: '',
    svg: svg(
      place(190, 232, .98, mfp() + guards(false) +
        '<g ' + A('gvMoveIn', .4, 1.0, '--fx:0px;--fy:-24px;--tx:0px;--ty:0px') + '><polygon points="40,114 130,114 130,138 40,138" fill="#fff" stroke="#94A3B8" stroke-width="2.5"/><line x1="52" y1="123" x2="110" y2="123" stroke="#64748B" stroke-width="3" stroke-linecap="round"/></g>') +
      '<g ' + A('gvPop', 1.2, .5) + '><rect x="80" y="50" width="230" height="56" rx="28" fill="#22B24C"/><text x="195" y="88" text-anchor="middle" fill="#fff" style="' + F + 'font-size:28px">복사본 ✔</text></g>' +
      '<g ' + A('gvPop', 2.0, .5) + '><rect x="470" y="50" width="230" height="56" rx="28" fill="#1B8AC4"/><text x="585" y="88" text-anchor="middle" fill="#fff" style="' + F + 'font-size:28px">원본도 ✔</text></g>')
  });

  window.GV_COPY_SCENES = scenes;
})();
