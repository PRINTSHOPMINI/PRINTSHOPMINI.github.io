/* 방문 통계 (구글 애널리틱스 GA4) — 페이지 조회수는 자동, 영상 재생·사용방법 클릭은 아래에서 기록
   video_play(재생 시작) / video_complete(끝까지 봄): video_name=영상 파일 이름
   guide_click(사용방법으로 가는 링크 클릭): guide_name=가는 페이지 */
(function(){
  if(window.__ga4)return;window.__ga4=1;
  if(!/(^|\.)printshopmini\.com$/.test(location.hostname))return; // 내 PC 미리보기는 세지 않아요
  var ID='G-33MG5YT83X';
  var s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+ID;document.head.appendChild(s);
  window.dataLayer=window.dataLayer||[];
  function gtag(){dataLayer.push(arguments);}
  window.gtag=gtag;
  gtag('js',new Date());
  gtag('config',ID);

  function vname(v){
    var u=v.currentSrc||v.src||'';
    if(!u){var so=v.querySelector('source');u=so?so.src:'';}
    return decodeURIComponent(u.split('?')[0].split('/').pop().replace(/\.[^.]+$/,''))||'unknown';
  }
  document.addEventListener('play',function(e){
    var v=e.target;
    if(!v||v.tagName!=='VIDEO'||v.autoplay||v.__gaPlay)return;  // 자동 재생(메인 홍보)은 세지 않아요
    v.__gaPlay=1;gtag('event','video_play',{video_name:vname(v)});
  },true);
  document.addEventListener('ended',function(e){
    var v=e.target;
    if(!v||v.tagName!=='VIDEO'||v.autoplay||v.__gaEnd)return;
    v.__gaEnd=1;gtag('event','video_complete',{video_name:vname(v)});
  },true);
  document.addEventListener('click',function(e){
    var a=e.target&&e.target.closest?e.target.closest('a[href]'):null;
    if(!a)return;
    var m=(a.getAttribute('href')||'').match(/(^|\/)(guide[a-z-]*)\.html(#[\w-]+)?/);
    if(m)gtag('event','guide_click',{guide_name:m[2]+(m[3]||'')});
  },true);
})();
