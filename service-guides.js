/* 이용안내 파일(PDF·이미지·영상) 표시 — 관리자(admin.html)에서 올린 파일을 서비스별 사용방법 페이지에 보여줍니다.
 * 사용법: 페이지에  <script>window.GUIDE_SERVICE='print';</script>  와  <div id="guideFiles"></div>  를 두고 이 파일을 불러오면 됩니다.
 * service_key: print / copy / scan / fax / coat / bind  (admin.html 의 이용안내 탭과 동일)
 */
(function(){
  var SB_URL='https://wbcfciiuiootbdezxfwy.supabase.co';
  var SB_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndiY2ZjaWl1aW9vdGJkZXp4Znd5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc1MjkyMTQsImV4cCI6MjA5MzEwNTIxNH0.UV4ukUXuAYKAqq85B4FTHO2BtIOqPaBHgAJN5lqyU5s';
  var HDR={'apikey':SB_KEY,'Authorization':'Bearer '+SB_KEY};

  function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

  var modalReady=false, box, hdr, titleEl, bodyEl, overlay, drag=null;

  function buildModal(){
    if(modalReady)return;
    overlay=document.createElement('div');
    overlay.style.cssText='display:none;position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:9997';
    overlay.addEventListener('click',closeGuideModal);
    box=document.createElement('div');
    box.style.cssText='display:none;position:fixed;z-index:9998;background:white;border-radius:16px;flex-direction:column;overflow:hidden;box-shadow:0 24px 80px rgba(0,0,0,0.3);resize:both;min-width:320px;min-height:200px';
    box.innerHTML=
      '<div class="sg-hdr" style="padding:13px 20px;border-bottom:1px solid #E5E7EB;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;cursor:move;user-select:none;-webkit-user-select:none">'+
        '<div style="display:flex;align-items:center;gap:10px;overflow:hidden">'+
          '<span style="color:#9CA3AF;font-size:15px;flex-shrink:0">⠿⠿</span>'+
          '<span class="sg-title" style="font-weight:900;font-size:15px;color:#111827;font-family:\'Noto Sans KR\',sans-serif;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></span>'+
        '</div>'+
        '<button type="button" class="sg-close" style="background:none;border:none;font-size:26px;cursor:pointer;color:#6B7280;line-height:1;flex-shrink:0;margin-left:12px">×</button>'+
      '</div>'+
      '<div class="sg-body" style="flex:1;overflow:auto;min-height:0"></div>';
    document.body.appendChild(overlay);
    document.body.appendChild(box);
    hdr=box.querySelector('.sg-hdr');
    titleEl=box.querySelector('.sg-title');
    bodyEl=box.querySelector('.sg-body');
    box.querySelector('.sg-close').addEventListener('click',closeGuideModal);

    hdr.addEventListener('mousedown',function(e){
      if(e.target.tagName==='BUTTON')return;
      var r=box.getBoundingClientRect();
      drag={sx:e.clientX,sy:e.clientY,sl:r.left,st:r.top};
      e.preventDefault();
    });
    hdr.addEventListener('touchstart',function(e){
      if(e.target.tagName==='BUTTON')return;
      var t=e.touches[0],r=box.getBoundingClientRect();
      drag={sx:t.clientX,sy:t.clientY,sl:r.left,st:r.top};
      e.preventDefault();
    },{passive:false});
    document.addEventListener('mousemove',function(e){
      if(!drag)return;
      box.style.left=(drag.sl+e.clientX-drag.sx)+'px';
      box.style.top=(drag.st+e.clientY-drag.sy)+'px';
    });
    document.addEventListener('touchmove',function(e){
      if(!drag)return;
      var t=e.touches[0];
      box.style.left=(drag.sl+t.clientX-drag.sx)+'px';
      box.style.top=(drag.st+t.clientY-drag.sy)+'px';
      e.preventDefault();
    },{passive:false});
    document.addEventListener('mouseup',function(){drag=null;});
    document.addEventListener('touchend',function(){drag=null;});
    modalReady=true;
  }

  function openGuideModal(url,name){
    buildModal();
    titleEl.textContent=name;
    if(/\.pdf$/i.test(name)){
      bodyEl.innerHTML='<iframe src="'+esc(url)+'" style="width:100%;height:100%;border:none;display:block"></iframe>';
    }else if(/\.(jpg|jpeg|png|gif|webp)$/i.test(name)){
      bodyEl.innerHTML='<div style="padding:20px;text-align:center;overflow:auto;height:100%;box-sizing:border-box"><img src="'+esc(url)+'" style="max-width:100%;height:auto;border-radius:8px"></div>';
    }else if(/\.(mp4|mov|webm|avi)$/i.test(name)){
      bodyEl.innerHTML='<video src="'+esc(url)+'" controls style="width:100%;height:100%;background:#000;display:block"></video>';
    }else{
      bodyEl.innerHTML='<div style="padding:40px;text-align:center"><a href="'+esc(url)+'" target="_blank" rel="noopener" style="color:#1B8AC4;font-weight:700">파일 열기 →</a></div>';
    }
    var w=Math.min(window.innerWidth*0.92,900);
    var h=Math.round(window.innerHeight*0.88);
    box.style.width=w+'px';
    box.style.height=h+'px';
    box.style.left=Math.round((window.innerWidth-w)/2)+'px';
    box.style.top=Math.round((window.innerHeight-h)/2)+'px';
    box.style.display='flex';
    overlay.style.display='block';
  }
  function closeGuideModal(){
    if(!modalReady)return;
    box.style.display='none';
    overlay.style.display='none';
    bodyEl.innerHTML='';
  }
  window.openGuideModal=openGuideModal;
  window.closeGuideModal=closeGuideModal;

  async function loadGuideFiles(){
    var key=window.GUIDE_SERVICE;
    var holder=document.getElementById('guideFiles');
    if(!key||!holder)return;
    try{
      var r=await fetch(SB_URL+'/rest/v1/service_guides?service_key=eq.'+encodeURIComponent(key)+'&order=sort_order',{headers:HDR});
      var data=await r.json();
      if(!Array.isArray(data)||!data.length)return;
      var cols=data.length===1?'1fr':'repeat(auto-fit,minmax(200px,1fr))';
      holder.style.cssText='display:grid;grid-template-columns:'+cols+';gap:8px;margin:0 0 26px;max-width:720px';
      holder.innerHTML=data.map(function(f){
        var icon=/\.pdf$/i.test(f.file_name)?'📄':/\.(mp4|mov|webm|avi)$/i.test(f.file_name)?'🎬':'🖼️';
        return '<button type="button" data-url="'+esc(f.file_url)+'" data-name="'+esc(f.file_name)+'" '+
          'style="background:#E8F4FC;color:#1B8AC4;border:1.5px solid #1B8AC4;border-radius:10px;padding:9px 14px;font-size:13px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:7px;font-family:\'Noto Sans KR\',sans-serif;min-width:0;overflow:hidden;text-align:left">'+
          '<span style="flex-shrink:0">'+icon+'</span>'+
          '<span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+esc(f.file_name)+'</span></button>';
      }).join('');
      holder.querySelectorAll('button').forEach(function(b){
        b.addEventListener('click',function(){openGuideModal(b.getAttribute('data-url'),b.getAttribute('data-name'));});
      });
    }catch(e){}
  }

  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',loadGuideFiles);}else{loadGuideFiles();}
})();
