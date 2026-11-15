import {catalog} from './catalog.js';
import {createGallery} from './gallery.js';
import {variantMedia} from './variant-media.js';
const q=s=>document.querySelector(s);
const money=n=>new Intl.NumberFormat('pl-PL',{style:'currency',currency:'PLN',minimumFractionDigits:n%100?2:0,maximumFractionDigits:2}).format(n/100);
const menu=q('.menu-dialog');
q('[data-menu]')?.addEventListener('click',()=>menu.showModal());
q('[data-close-menu]')?.addEventListener('click',()=>menu.close());
menu?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>menu.close()));
menu?.addEventListener('close',()=>q('[data-menu]').focus({preventScroll:true}));
const color=id=>catalog.colors.find(c=>c.id===id);
if(document.body.dataset.page==='product'){
  const model=catalog.models.find(m=>m.id===document.body.dataset.model);
  const requested=new URLSearchParams(location.search).get('color');
  let selected=color(requested)?requested:variantMedia.find(m=>m.modelId===model.id&&m.role==='main'&&m.colorConfirmed)?.colorId||null;
  document.title=model.name+' · WINTER 26 — Pracownia Form';
  for(const s of ['[data-product-crumb]','[data-product-name]','[data-gallery-title]'])q(s).textContent=model.name;
  q('[data-product-family]').textContent=model.family+' / WINTER 26';q('[data-product-family-short]').textContent=model.family;
  q('[data-product-description]').textContent=model.description;
  document.querySelectorAll('[data-model-link]').forEach(a=>a.setAttribute('aria-current',a.dataset.modelLink===model.id?'page':'false'));
  const gallery=createGallery(q('[data-product-gallery]'));
  function draw(){gallery.update(model,selected);q('[data-product-color]').textContent=color(selected)?.label||'—';q('[data-product-status]').textContent=selected?model.name+' / '+color(selected).label:'Wybierz wykończenie, aby dodać ozdobę do kompozycji.';}
  for(const c of catalog.colors){
    const label=document.createElement('label');label.className='finish-choice';const input=document.createElement('input');input.type='radio';input.name='product-color';input.value=c.id;input.checked=selected===c.id;
    const face=document.createElement('span');face.className='finish-face';const dot=document.createElement('i');dot.className='swatch '+c.id;dot.setAttribute('aria-hidden','true');const text=document.createElement('span');text.textContent=c.label;face.append(dot,text);label.append(input,face);q('[data-product-colors]').append(label);
    input.addEventListener('change',()=>{selected=c.id;draw()});
  }
  q('[data-product-add]').addEventListener('click',()=>{if(!selected){q('[data-product-status]').textContent='Wybierz wykończenie.';q('input[name="product-color"]').focus();return}location.assign('/winter-zestaw-4.html?size=1&model='+encodeURIComponent(model.id)+'&color='+encodeURIComponent(selected)+'#kompozycja')});
  draw();
}
if(document.body.dataset.page==='compose'){
  const options=JSON.parse(q('#winter-options').textContent);
  const gallery=createGallery(q('[data-compose-picture]'),{compact:true});
  const set=(s,text)=>{q(s).textContent=text;};
  document.addEventListener('pf:composition',({detail:d})=>{
    const model=catalog.models.find(m=>m.id===d.model),display=model||catalog.models[0];
    gallery.update(display,model?d.color:null);
    set('[data-photo-caption]',model?.name||'VASE / Inspiracja — wybierz własną formę');
    set('[data-active-family]',model?model.family+' / WINTER 26':'Trzy formy do wyboru');set('[data-active-name]',model?.name||'Wybierz formę.');set('[data-active-description]',model?.description||'Miękka spirala czy ażurowy splot? Zacznij od modelu, potem nadaj mu wykończenie.');
    set('[data-set-size]',d.size+' '+(d.size===1?'ozdoba':d.size<5?'ozdoby':'ozdób'));
    set('[data-size-detail]',d.size>=options.freeFrom?'Dostawa w Polsce w cenie. Kurier lub Paczkomat®.':'Dostawa od '+money(options.smallOrderLockerGrosz)+'. Bezpłatna od '+options.freeFrom+' ozdób.');
    set('[data-dock-step]',d.step+' / 3 · '+['Rozmiar','Komponowanie','Podsumowanie'][d.step-1]);set('[data-dock-progress]',d.done+' z '+d.count+' ozdób skonfigurowanych');set('[data-dock-price-label]','Razem');set('[data-dock-total]',money(d.total??d.merchandise));
    set('[data-r015-merchandise]',money(d.merchandise));set('[data-r015-shipping]',d.shipping===null?'Do potwierdzenia':money(d.shipping));set('[data-r015-total]',d.total===null?'Do potwierdzenia':money(d.total));
    q('[data-prev]').hidden=d.step===1;
  });
  // Install the view listener before the unchanged checkout initializer runs.
  await import('/winter-config.js');
}
