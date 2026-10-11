/* 프린트샵미니 퀵메뉴 — 모든 페이지에서 화면을 따라다니는 바로가기
   - PC(901px 이상): 오른쪽 가운데에 세로로 (한국 사이트에서 가장 흔한 위치)
   - 모바일·태블릿: 화면 아래쪽 가로 막대
   메뉴를 바꾸려면 아래 ITEMS 만 고치면 모든 페이지에 반영돼요. */
(function(){
  if(window.__qmLoaded)return;
  window.__qmLoaded=true;

  var ITEMS=[
    {href:'guide.html',            img:'images/quick/qm-guide.png',  label:'사용방법'},
    {href:'faq.html#faq-12',       img:'images/quick/qm-refund.png', label:'환불'},
    {href:'faq.html#faq-4',        img:'images/quick/qm-broken.png', label:'고장 났어요'},
    {href:'faq.html#faq-22',       img:'images/quick/qm-phone-kakao.png',  label:'핸드폰에 있는 파일 인쇄하기'}
  ];

  var css=
  '#qm{position:fixed;z-index:280;display:flex;gap:10px;margin:0;padding:0;list-style:none}'+
  '#qm a{display:block;line-height:0;border-radius:18px;transition:transform .15s,box-shadow .15s;-webkit-tap-highlight-color:transparent}'+
  '#qm img{display:block;width:100%;height:auto;border-radius:18px}'+
  '@media(min-width:901px){'+
    '#qm{right:12px;top:50%;transform:translateY(-50%);flex-direction:column}'+
    '#qm a{width:68px;box-shadow:0 4px 14px rgba(0,0,0,.18)}'+
    '#qm a:hover{transform:translateX(-4px) scale(1.06);box-shadow:0 8px 20px rgba(0,0,0,.25)}'+
  '}'+
  '@media(max-width:900px){'+
    '#qm{left:0;right:0;bottom:0;justify-content:space-around;align-items:center;gap:6px;'+
      'background:rgba(255,255,255,.97);border-top:1px solid #E5E7EB;box-shadow:0 -4px 16px rgba(0,0,0,.08);'+
      'padding:6px 10px calc(6px + env(safe-area-inset-bottom))}'+
    '#qm a{width:min(22%,58px)}'+
    'body{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}'+
  '}'+
  '@media print{#qm{display:none!important}}';

  function build(){
    if(document.getElementById('qm'))return;
    var st=document.createElement('style');
    st.id='qm-style';
    st.textContent=css;
    document.head.appendChild(st);

    var nav=document.createElement('div');   /* nav 태그는 페이지 위쪽 메뉴 스타일과 겹쳐서 div 사용 */
    nav.id='qm';
    nav.setAttribute('role','navigation');
    nav.setAttribute('aria-label','바로가기 퀵메뉴');
    ITEMS.forEach(function(it){
      var a=document.createElement('a');
      a.href=it.href;
      a.title=it.label;
      a.setAttribute('aria-label',it.label);
      var im=document.createElement('img');
      im.src=it.img;
      im.alt=it.label;
      im.width=192;im.height=192;
      im.decoding='async';
      a.appendChild(im);
      nav.appendChild(a);
    });
    document.body.appendChild(nav);
  }

  if(document.body)build();
  else document.addEventListener('DOMContentLoaded',build);
})();
