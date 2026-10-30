/* 그림 확대 보기: 그림을 누르면 같은 화면 위에 크게 뜨고, ✕ 닫기(또는 바깥·ESC·뒤로가기)로 돌아와요 */
(function(){
  if(window.__lbx)return;window.__lbx=1;
  var css=
  'img.lbx-ok{cursor:zoom-in}'+
  'html.lbx-lock{overflow:hidden}'+
  '#lbx{position:fixed;left:0;top:0;right:0;bottom:0;z-index:99999;background:rgba(12,18,34,.92);display:none;align-items:center;justify-content:center;padding:74px 10px 52px;box-sizing:border-box}'+
  '#lbx.on{display:flex}'+
  '.lbx-box{max-width:100%;max-height:100%;overflow:auto;-webkit-overflow-scrolling:touch;border-radius:10px}'+
  '.lbx-box img{display:block;margin:0 auto;background:#fff;border-radius:10px;width:auto;height:auto;max-width:min(96vw,1400px);max-height:calc(100vh - 120px);cursor:zoom-in}'+
  '.lbx-box.full img{max-width:none;max-height:none;cursor:zoom-out}'+
  '.lbx-x{position:absolute;top:10px;right:10px;display:flex;align-items:center;gap:8px;background:#fff;color:#111827;border:0;border-radius:50px;padding:12px 22px 12px 16px;font-size:19px;font-weight:900;min-height:52px;font-family:inherit;box-shadow:0 4px 14px rgba(0,0,0,.35);cursor:pointer}'+
  '.lbx-x b{font-size:28px;line-height:1}'+
  '.lbx-hint{position:absolute;left:0;right:0;bottom:14px;text-align:center;color:#d6deea;font-size:13px;font-weight:600;padding:0 12px}';
  var st=document.createElement('style');st.textContent=css;document.head.appendChild(st);

  var ov=null,box=null,imgEl=null,isOpen=false;
  var LANG=(window.I18N_LANG||document.documentElement.lang||'ko').slice(0,2);
  var T={
    en:['Close','Tap the picture to zoom in or out. Tap ✕ (top right) or outside to close.'],
    zh:['关闭','点图片可放大或缩小。点右上角 ✕ 或图片外面即可关闭。'],
    vi:['Đóng','Chạm vào hình để phóng to/thu nhỏ. Chạm ✕ (góc trên bên phải) hoặc bên ngoài để đóng.']
  }[LANG]||['닫기','그림을 누르면 더 크게·작게 볼 수 있어요. 오른쪽 위 ✕나 바깥을 누르면 닫혀요.'];
  function build(){
    ov=document.createElement('div');ov.id='lbx';ov.setAttribute('role','dialog');ov.setAttribute('aria-label','확대한 그림');
    ov.innerHTML='<button type="button" class="lbx-x" aria-label="'+T[0]+'"><b>✕</b>'+T[0]+'</button>'+
      '<div class="lbx-box"><img alt=""></div>'+
      '<div class="lbx-hint">'+T[1]+'</div>';
    document.body.appendChild(ov);
    box=ov.querySelector('.lbx-box');imgEl=ov.querySelector('img');
    ov.addEventListener('click',function(e){
      if(e.target===imgEl){box.classList.toggle('full');return;}
      if(e.target.closest&&e.target.closest('.lbx-x'))return;
      close();
    });
    ov.querySelector('.lbx-x').addEventListener('click',function(e){e.stopPropagation();close();});
  }
  function show(src,alt){
    if(!ov)build();
    box.classList.remove('full');box.scrollTop=0;box.scrollLeft=0;
    imgEl.src=src;imgEl.alt=alt||'';
    ov.classList.add('on');document.documentElement.classList.add('lbx-lock');isOpen=true;
    try{history.pushState({lbx:1},'');}catch(e){}
  }
  function close(fromPop){
    if(!isOpen)return;
    isOpen=false;ov.classList.remove('on');document.documentElement.classList.remove('lbx-lock');
    imgEl.removeAttribute('src');
    if(fromPop!==true){try{if(history.state&&history.state.lbx)history.back();}catch(e){}}
  }
  window.addEventListener('popstate',function(){if(isOpen)close(true);});
  document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});

  var IMG_RE=/\.(jpe?g|png|webp|gif)(\?|#|$)/i;
  /* 본문 그림은 모두 크게 볼 수 있게 — 로고·메뉴·작은 아이콘·다른 페이지로 가는 그림 링크만 빼요 */
  var SKIP='nav,header,footer,button,.logo-img,.faq-ico,[aria-hidden="true"],.no-zoom,#lbx';
  function linkTo(im){
    var a=im.closest('a');if(!a)return null;
    var h=a.getAttribute('href')||'';
    if(IMG_RE.test(h))return a.href;   // 원본 그림이 따로 있으면 그걸 크게
    if(h&&h.charAt(0)!=='#')return false; // 다른 페이지로 가는 링크는 그대로 둬요
    return null;
  }
  function ok(im){
    if(!im||im.closest(SKIP))return false;
    if(im.matches('.step-photo,.faq-img,.zoomable'))return linkTo(im)!==false;
    if(im.offsetWidth&&im.offsetWidth<60)return false;   // 작은 아이콘은 빼요
    return linkTo(im)!==false;
  }
  function mark(){var a=document.querySelectorAll('img');for(var i=0;i<a.length;i++){if(ok(a[i]))a[i].classList.add('lbx-ok');}}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mark);else mark();
  window.addEventListener('load',mark);
  document.addEventListener('mouseover',function(e){var im=e.target;if(im&&im.tagName==='IMG'&&!im.classList.contains('lbx-ok')&&ok(im))im.classList.add('lbx-ok');});

  document.addEventListener('click',function(e){
    var im=e.target&&e.target.closest?e.target.closest('img'):null;
    if(!im||!ok(im))return;
    var big=linkTo(im);
    e.preventDefault();e.stopPropagation();
    show(big||im.currentSrc||im.src,im.alt);
  },true);
})();
