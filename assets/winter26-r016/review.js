import {catalog} from '../winter26-r015/catalog.js';
import {variantMedia} from './variant-media.js';
const root=document.querySelector('[data-photo-matrix]');
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const roles={main:'Zdjęcie główne',gallery:'Dodatkowe ujęcie',detail:'Detal',lifestyle:'Aranżacja lifestyle'};
const test=new URLSearchParams(location.search).get('test')==='1';
const key='pf-photo-review-r016-v1';let decisions={};
try{if(!test)decisions=JSON.parse(localStorage.getItem(key)||'{}')}catch{}
const selected=new Map();
const status=document.querySelector('[data-review-status]');
if(test)status.textContent='Tryb testu przycisków — oceny nie są zapisywane.';
const decisionKey=item=>[item.id,item.modelId,item.colorId,item.role,item.sourceSha256].join('|');
function save(){
  if(test)return;
  try{localStorage.setItem(key,JSON.stringify(decisions));status.textContent='Zapisano w tej przeglądarce. Pobierz decyzje, aby przekazać je do rejestru.'}
  catch{status.textContent='Przeglądarka nie pozwala zapisać ocen. Pobierz decyzje przed zamknięciem strony.'}
}
function cell(model,color){
  const pair=model.id+':'+color.id,items=variantMedia.filter(m=>m.modelId===model.id&&m.colorId===color.id);
  const index=Math.min(selected.get(pair)||0,Math.max(0,items.length-1)),item=items[index];
  const confirmed=items.filter(x=>x.colorConfirmed).length,proposal=items.length-confirmed;
  const head=`<article class="matrix-cell" data-pair="${pair}" aria-label="${model.name} / ${color.label}"><h3>${color.label}</h3><p class="matrix-count">${model.name} · ${confirmed} potwierdzonych · ${proposal} propozycji</p>`;
  if(!item)return head+`<div class="matrix-missing">Brak materiału w istniejącym wyborze zdjęć.</div><p class="matrix-note">Nie znaleziono zdjęcia głównego, dodatkowego ujęcia, detalu ani aranżacji tego wariantu.</p><a href="/winter-${model.id}.html?color=${color.id}">Sprawdź widok wariantu</a></article>`;
  const decision=decisions[decisionKey(item)];
  const local=decision?`${test?'Test: ':''}${decision.action==='approve'?'Zatwierdzono zdjęcie i jego obecną rolę':'Odrzucono kandydaturę'} — ocena lokalna, bez publikacji.`:'';
  return head+`<button class="matrix-picture" data-zoom="${item.id}" aria-label="Powiększ ${model.name} / ${color.label}"><img src="${item.src}" srcset="${item.srcset}" sizes="(max-width:560px) 100vw, (max-width:1000px) 45vw, 23vw" alt="${esc(item.alt)}" loading="lazy"></button>
  <div class="matrix-thumbs" aria-label="Ujęcia ${model.name} / ${color.label}">${items.map((p,i)=>`<button data-frame="${i}" aria-pressed="${i===index}" aria-label="${i+1}. ${roles[p.role]}: ${esc(p.sourceFile)}"><img src="${p.thumb}" alt="" loading="lazy"></button>`).join('')}</div>
  <dl class="matrix-meta"><dt>Plik źródłowy</dt><dd>${esc(item.sourceFile)}</dd><dt>Rola bez zmiany</dt><dd>${roles[item.role]} (${item.role})</dd><dt>Status rejestru</dt><dd>${item.ownerStatus}</dd></dl>
  <p class="matrix-note">${esc(item.reviewOnly?'Tylko panel akceptacji: wcześniejszy audyt wymaga potwierdzenia modelu/geometrii. '+item.note:item.note)}</p>
  <div class="matrix-decisions"><button data-decision="approve" data-asset="${item.id}" ${item.ownerStatus==='OWNER APPROVED'?'disabled':''}>Zatwierdź zdjęcie i rolę</button><button data-decision="reject" data-asset="${item.id}" ${item.colorConfirmed?'disabled':''}>Odrzuć</button>${decision?`<button data-decision="undo" data-asset="${item.id}">Cofnij ocenę lokalną</button>`:''}</div><p class="matrix-local" aria-live="polite">${esc(local)}</p><a href="/winter-${model.id}.html?color=${color.id}">Sprawdź widok wariantu</a></article>`;
}
function render(){root.innerHTML=catalog.models.map(m=>`<h2 class="matrix-model">${m.name}</h2>`+catalog.colors.map(c=>cell(m,c)).join('')).join('')}
const zoom=document.querySelector('[data-review-zoom]');let zoomTrigger;
root.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  const pair=b.closest('[data-pair]').dataset.pair;
  if(b.hasAttribute('data-frame')){selected.set(pair,Number(b.dataset.frame));render();root.querySelector(`[data-pair="${pair}"] [data-frame="${b.dataset.frame}"]`).focus({preventScroll:true})}
  if(b.dataset.decision){
    const item=variantMedia.find(m=>m.id===b.dataset.asset);
    if(!item||item.ownerStatus==='OWNER APPROVED'||b.dataset.decision==='reject'&&item.colorConfirmed)return;
    if(b.dataset.decision==='undo')delete decisions[decisionKey(item)];
    else decisions[decisionKey(item)]={action:b.dataset.decision,assetId:item.id,modelId:item.modelId,colorId:item.colorId,role:item.role,sourceFile:item.sourceFile,sourceSha256:item.sourceSha256,recordedAt:new Date().toISOString()};
    save();render();root.querySelector(`[data-pair="${pair}"] [data-decision="${b.dataset.decision==='undo'?'approve':b.dataset.decision}"]`).focus({preventScroll:true});
  }
  if(b.dataset.zoom){const item=variantMedia.find(m=>m.id===b.dataset.zoom);zoomTrigger=item.id;zoom.querySelector('img').src=item.zoom;zoom.querySelector('img').alt=item.alt;zoom.querySelector('p').textContent=item.sourceFile+' · '+item.ownerStatus;zoom.showModal();zoom.querySelector('button').focus()}
});
root.addEventListener('keydown',e=>{
  if(!e.target.hasAttribute('data-frame')||!['ArrowRight','ArrowLeft'].includes(e.key))return;
  e.preventDefault();const card=e.target.closest('[data-pair]'),pair=card.dataset.pair,frames=card.querySelectorAll('[data-frame]');
  selected.set(pair,((selected.get(pair)||0)+(e.key==='ArrowRight'?1:-1)+frames.length)%frames.length);render();root.querySelector(`[data-pair="${pair}"] [data-frame="${selected.get(pair)}"]`).focus({preventScroll:true});
});
zoom.querySelector('button').addEventListener('click',()=>zoom.close());zoom.addEventListener('close',()=>root.querySelector(`[data-zoom="${zoomTrigger}"]`)?.focus({preventScroll:true}));
document.querySelector('[data-export-decisions]').addEventListener('click',()=>{
 const data={schema:'PF-R016-owner-review-v1',testOnly:test,appliesAutomatically:false,scope:'Exact image, color and existing role; requires registry import before publication',decisions:Object.values(decisions)};
 const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),link=document.createElement('a');link.href=url;link.download='PF-R016-decyzje'+(test?'-TEST':'')+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Przygotowano plik decyzji. Sklep i katalog nie zostały zmienione.';
});
render();
