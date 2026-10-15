/* 그림 확대 보기: 그림을 누르면 같은 화면 위에 크게 뜨고, ✕ 닫기(또는 바깥·ESC·뒤로가기)로 돌아와요 */
(function(){
  if(window.__lbx)return;window.__lbx=1;
  var css=
  '.step-photo,.faq-img,.pfig img,.est-fig img,.zoomable{cursor:zoom-in}'+
  'html.lbx-lock{overflow:hidden}'+
  '#lbx{position:fixed;left:0;top:0;right:0;bottom:0;z-index:99999;background:rgba(12,18,34,.92);display:none;align-items:center;justify-content:center;padding:64px 10px 52px;box-sizing:border-box}'+
  '#lbx.on{display:flex}'+
  '.lbx-box{max-width:100%;max-height:100%;overflow:auto;-webkit-overflow-scrolling:touch;border-radius:10px}'+
  '.lbx-box img{display:block;margin:0 auto;background:#fff;border-radius:10px;width:auto;height:auto;max-width:min(96vw,1400px);max-height:calc(100vh - 120px);cursor:zoom-in}'+
  '.lbx-box.full img{max-width:none;max-height:none;cursor:zoom-out}'+
  '.lbx-x{position:absolute;top:10px;right:10px;display:flex;align-items:center;gap:8px;background:#fff;color:#111827;border:0;border-radius:50px;padding:10px 18px 10px 14px;font-size:17px;font-weight:900;font-family:inherit;box-shadow:0 4px 14px rgba(0,0,0,.35);cursor:pointer}'+
  '.lbx-x b{font-size:22px;line-height:1}'+
  '.lbx-hint{position:absolute;left:0;right:0;bottom:14px;text-align:center;color:#d6deea;font-size:13px;font-weight:600;padding:0 12px}';
  var st=document.createElement('style');st.textContent=css;document.head.appendChild(st);

  var ov=null,box=null,imgEl=null,isOpen=false;
  function build(){
    ov=document.createElement('div');ov.id='lbx';ov.setAttribute('role','dialog');ov.setAttribute('aria-label','확대한 그림');
    ov.innerHTML='<button type="button" class="lbx-x" aria-label="닫기"><b>✕</b>닫기</button>'+
      '<div class="lbx-box"><img alt=""></div>'+
      '<div class="lbx-hint">그림을 누르면 더 크게·작게 볼 수 있어요. 오른쪽 위 ✕나 바깥을 누르면 닫혀요.</div>';
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
  document.addEventListener('click',function(e){
    var im=e.target&&e.target.closest?e.target.closest('img'):null;
    if(!im||(ov&&ov.contains(im)))return;
    if(!im.matches('.step-photo,.faq-img,.pfig img,.est-fig img,.zoomable'))return;
    if(im.matches('.faq-ico'))return;
    var a=im.closest('a'),src=im.currentSrc||im.src;
    if(a){
      var h=a.getAttribute('href')||'';
      if(IMG_RE.test(h))src=a.href;      // 원본 그림이 따로 있으면 그걸 크게
      else if(h&&h.charAt(0)!=='#')return; // 다른 페이지로 가는 링크는 그대로 둬요
    }
    e.preventDefault();e.stopPropagation();
    show(src,im.alt);
  },true);
})();
