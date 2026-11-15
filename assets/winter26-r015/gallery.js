import {catalog} from './catalog.js';
import {variantMedia} from './variant-media.js';
import {selectGallery,nextFrame} from './gallery-state.js';
import {ownerApprovalFor} from './approval-state.js';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const previewMedia=variantMedia;

let instance=0;
export function createGallery(root,{compact=false}={}){
  const id='photo-gallery-'+(++instance);
  root.classList.add('photo-gallery');
  if(compact)root.classList.add('gallery-compact');
  root.innerHTML=`<div class="photo-tabs" aria-label="Rodzaj fotografii"><button type="button" data-section="lifestyle" aria-pressed="true">W aranżacji</button><button type="button" data-section="product" aria-pressed="false">Zdjęcia produktu</button></div>
    <div class="gallery-caption-line"><p class="gallery-scope" data-scope role="status" aria-live="polite"></p><span class="proposal-badge" data-proposal>Aranżacja</span></div>
    <div class="gallery-empty" data-empty hidden><p>Brak zdjęcia tego wykończenia.</p><span>Możesz obejrzeć pozostałe kolory.</span></div>
    <button class="gallery-stage" type="button" data-open aria-label="Powiększ fotografię" aria-haspopup="dialog" aria-describedby="${id}-caption"><img data-main alt="" decoding="async"><span class="zoom-hint">Powiększ</span></button>
    <div class="photo-controls"><button type="button" data-photo-prev aria-label="Poprzednie zdjęcie">Poprzednie</button><p id="${id}-caption" data-caption aria-live="polite"></p><button type="button" data-photo-next aria-label="Następne zdjęcie">Następne</button></div>
    <div class="photo-thumbnails" data-thumbs aria-label="Ujęcia produktu"></div>`;
  const dialog=document.createElement('dialog');dialog.className='photo-lightbox';
  dialog.setAttribute('aria-label','Fotografia w powiększeniu');
  dialog.innerHTML=`<div class="lightbox-head"><p data-zoom-title></p><button type="button" data-close>Zamknij</button></div><div class="lightbox-image" tabindex="0" aria-label="Powiększona fotografia; po powiększeniu można przewijać"><img data-zoom-image alt=""></div><div class="lightbox-controls"><button type="button" data-zoom-prev aria-label="Poprzednie zdjęcie w powiększeniu">Poprzednie</button><button type="button" data-scale aria-pressed="false">Powiększ 2×</button><button type="button" data-zoom-next aria-label="Następne zdjęcie w powiększeniu">Następne</button></div><p class="lightbox-caption" data-zoom-caption aria-live="polite"></p>`;
  document.body.append(dialog);
  const q=s=>root.querySelector(s),z=s=>dialog.querySelector(s);
  const imageReady=()=>{root.dataset.loaded=String([...root.querySelectorAll('img')].every(i=>i.complete&&i.naturalWidth>0));};
  root.addEventListener('load',imageReady,true);
  let currentModel,currentColor,selection,section='lifestyle',frame=0,touch=null;
  const frames=()=>selection?.[section]||[];
  function scope(){
    if(section==='lifestyle')return `${currentModel.name} · Inspiracja — niezależnie od wybranego koloru`;
    const color=catalog.colors.find(c=>c.id===currentColor);
    return color?`${currentModel.name} / ${color.label}`:`${currentModel.name} · wybierz wykończenie`;
  }
  function image(node,item,zoom=false){
    node.src=zoom?item.zoom:item.src;node.alt=item.alt;
    if(zoom)node.removeAttribute('srcset');
    else {node.srcset=item.srcset;node.sizes=compact?'(max-width:760px) 100vw, 48vw':'(max-width:760px) 100vw, 55vw';}
    node.width=item.width;node.height=item.height;
  }
  function render(){
    const items=frames(),item=items[frame];
    q('[data-scope]').textContent=scope();
    root.dataset.scope=selection.scope;root.dataset.section=section;
    q('[data-thumbs]').setAttribute('aria-label',section==='lifestyle'?'Ujęcia aranżacyjne':'Ujęcia produktu');
    root.querySelectorAll('[data-section]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.section===section)));
    q('[data-empty] p').textContent=section==='lifestyle'?'Brak zdjęć aranżacyjnych tego modelu.':'Brak zdjęcia tego wykończenia.';
    q('[data-empty] span').textContent=section==='lifestyle'?'Możesz obejrzeć zdjęcia produktu.':'Możesz obejrzeć pozostałe kolory.';
    q('[data-empty]').hidden=Boolean(item);q('[data-open]').hidden=!item;
    q('.photo-controls').hidden=!item;q('[data-thumbs]').hidden=!item;q('[data-proposal]').hidden=!item;
    if(!item){q('[data-main]').removeAttribute('src');q('[data-main]').removeAttribute('srcset');q('[data-main]').removeAttribute('data-asset');q('[data-main]').alt='';q('[data-thumbs]').innerHTML='';root.dataset.loaded='true';return;}
    const owner=ownerApprovalFor(item);q('[data-proposal]').textContent=owner?'OWNER APPROVED':section==='lifestyle'?'Aranżacja':'';q('[data-proposal]').hidden=!owner&&section!=='lifestyle';q('[data-proposal]').dataset.ownerApproved=String(Boolean(owner));
    image(q('[data-main]'),item);q('[data-main]').dataset.asset=item.id;
    q('[data-caption]').textContent=`${frame+1} / ${items.length} · ${item.role==='detail'?'Detal':'Fotografia'}`;
    q('[data-thumbs]').innerHTML=items.map((p,i)=>`<button type="button" data-frame="${i}" aria-pressed="${frame===i}" aria-label="Ujęcie ${i+1}: ${esc(p.label)}"><img src="${esc(p.thumb)}" alt="" width="72" height="72" loading="lazy"></button>`).join('');
    q('[data-photo-prev]').disabled=q('[data-photo-next]').disabled=items.length<2;
    imageReady();
    if(dialog.open)renderZoom();
  }
  function resetScale(){dialog.classList.remove('is-magnified');z('[data-scale]').setAttribute('aria-pressed','false');z('[data-scale]').textContent='Powiększ 2×';z('.lightbox-image').scrollTo(0,0);}
  function renderZoom(){const item=frames()[frame];image(z('[data-zoom-image]'),item,true);z('[data-zoom-title]').textContent=currentModel.name;z('[data-zoom-caption]').textContent=`${frame+1} / ${frames().length} · ${scope()}`;z('[data-zoom-prev]').disabled=z('[data-zoom-next]').disabled=frames().length<2;resetScale();}
  function move(delta){const fromThumb=document.activeElement?.hasAttribute('data-frame');frame=nextFrame(frame,delta,frames().length);render();if(!dialog.open){const thumb=q(`[data-frame="${frame}"]`);if(fromThumb)thumb?.focus({preventScroll:true});thumb?.scrollIntoView({block:'nearest',inline:'nearest'});}}
  root.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
    if(b.dataset.section){section=b.dataset.section;frame=0;render();}
    else if(b.hasAttribute('data-frame')){frame=Number(b.dataset.frame);render();q(`[data-frame="${frame}"]`).focus({preventScroll:true});}
    else if(b.hasAttribute('data-photo-prev'))move(-1);
    else if(b.hasAttribute('data-photo-next'))move(1);
    else if(b.hasAttribute('data-open')){dialog.showModal();document.documentElement.classList.add('gallery-modal-open');renderZoom();z('[data-close]').focus();}
  });
  function keys(e){
    if(e.key==='Tab'&&dialog.open){
      const focusable=[...dialog.querySelectorAll('button:not(:disabled),[tabindex="0"]')];
      const first=focusable[0],last=focusable.at(-1);
      if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
      else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
      return;
    }
    if(dialog.classList.contains('is-magnified')&&e.target===z('.lightbox-image'))return;
    if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();move(e.key==='ArrowRight'?1:-1);}
  }
  root.addEventListener('keydown',keys);dialog.addEventListener('keydown',keys);
  q('[data-thumbs]').addEventListener('wheel',e=>{const strip=e.currentTarget;if(Math.abs(e.deltaX)>=Math.abs(e.deltaY))return;const delta=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?strip.clientWidth:1);const next=Math.max(0,Math.min(strip.scrollWidth-strip.clientWidth,strip.scrollLeft+delta));if(next!==strip.scrollLeft){e.preventDefault();strip.scrollLeft=next;}},{passive:false});
  // A horizontal swipe changes frames. Vertical page/pinch gestures remain native.
  q('[data-open]').addEventListener('touchstart',e=>{touch=e.touches.length===1?{x:e.touches[0].clientX,y:e.touches[0].clientY}:null;},{passive:true});
  let swiped=false;
  q('[data-open]').addEventListener('touchend',e=>{if(!touch)return;const p=e.changedTouches[0],dx=p.clientX-touch.x,dy=p.clientY-touch.y;touch=null;if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.4){swiped=true;move(dx<0?1:-1);setTimeout(()=>swiped=false,450);}},{passive:true});
  q('[data-open]').addEventListener('click',e=>{if(swiped){e.preventDefault();e.stopPropagation();swiped=false;}});
  z('[data-close]').addEventListener('click',()=>dialog.close());
  z('[data-zoom-prev]').addEventListener('click',()=>move(-1));z('[data-zoom-next]').addEventListener('click',()=>move(1));
  z('[data-scale]').addEventListener('click',()=>{const on=dialog.classList.toggle('is-magnified');z('[data-scale]').setAttribute('aria-pressed',String(on));z('[data-scale]').textContent=on?'Dopasuj zdjęcie':'Powiększ 2×';});
  dialog.addEventListener('close',()=>{document.documentElement.classList.remove('gallery-modal-open');resetScale();q('[data-open]').focus({preventScroll:true});});
  return {update(model,color=null){if(currentModel?.id===model.id&&currentColor===color)return;currentModel=model;currentColor=color;selection=selectGallery(previewMedia,model.id,color);frame=0;render();}};
}
