'use strict';
// Stock is a catalog snapshot, never a reservation.
function variantFor(data, slot) {
  return data.models.find(m => m.id === slot.model)?.variants.find(v => v.colorId === slot.color);
}
function eligible(v, slots, index, data) {
  if (!v || !v.available || !v.sku || !Number.isInteger(v.stock) || v.stock < 1) return false;
  return slots.filter((s,i) => i !== index && variantFor(data,s)?.sku === v.sku).length < v.stock;
}
function summary(data,slots) {
  const groups = new Map(); let done=0;
  slots.forEach((slot,i) => {
    const m=data.models.find(x=>x.id===slot.model); if (!m) return;
    const v=variantFor(data,slot);
    if (eligible(v,slots,i,data)) done++;
    const key=JSON.stringify([m.id,v?.colorId]), g=groups.get(key);
    if (g) g.count++; else groups.set(key,{name:m.name,label:v?.label||'Bez wybranego koloru',count:1});
  });
  return {done,groups:[...groups.values()]};
}
if (typeof module !== 'undefined') module.exports={variantFor,eligible,summary};
if (typeof document !== 'undefined') {
  const data=JSON.parse(document.querySelector('#winter-options').textContent);
  const el=(tag,txt,cls)=>{const n=document.createElement(tag);if(txt!=null)n.textContent=txt;if(cls)n.className=cls;return n};
  const money=g=>new Intl.NumberFormat('pl-PL',{style:'currency',currency:'PLN'}).format(g/100);
  const picture=(src,alt='')=>{const i=el('img');i.src=src;i.alt=alt;i.decoding='async';return i};
  function radio(name,val,label,on,change,disabled=false) {
    const wrap=el('label',null,'choice'),r=el('input');r.type='radio';r.name=name;r.value=val;r.checked=on;r.disabled=disabled;
    r.onchange=()=>change(val);wrap.append(r,label);return wrap;
  }
  function swatch(v,disabled) {
    const face=el('span',null,'swatch'),dot=el('i');dot.style.backgroundColor=v.hex;
    face.append(dot,el('span',v.label+(disabled?' · niedostępny':'')));return face;
  }
  for (const block of document.querySelectorAll('[data-color-model]')) {
    const m=data.models.find(x=>x.id===block.dataset.colorModel);
    const wrap=block.querySelector('[data-swatches]'),status=block.querySelector('[data-variant-status]');
    if (!m?.variants.length) continue;
    wrap.setAttribute('role','radiogroup');wrap.setAttribute('aria-label','Wybierz kolor: '+m.name);
    status.textContent='Wybierz próbkę, aby obejrzeć wariant.';
    const host=block.closest('.product-card,.store-layout'),cover=host.querySelector('.store-cover,.store-gallery');
    const preview=el('figure',null,'variant-photo');preview.hidden=true;cover.before(preview);
    for(const v of m.variants) {
      wrap.append(radio('color-'+m.id,v.colorId,swatch(v,!v.available),false,()=>{
        status.textContent=[v.label,v.grossGrosz==null?'':money(v.grossGrosz)+' brutto',v.available?'Dostępny':'Niedostępny',
          v.photo?'':'Zdjęcie tego koloru w przygotowaniu.'].filter(Boolean).join(' · ');
        if(v.photo) {
          const img=picture(v.photo.image,v.photo.alt), a=el('a');
          a.href=host.classList.contains('product-card')?'winter-'+m.id+'.html?color='+encodeURIComponent(v.colorId):v.photo.image;
          a.append(img);preview.replaceChildren(a,el('figcaption',m.name+' / '+v.label));cover.hidden=true;preview.hidden=false;
        } else {
          preview.replaceChildren(el('p','Fotografia wariantu w przygotowaniu.','photo-pending'));
          cover.hidden=true;preview.hidden=false;
        }
        const dest=host.querySelector('.premiere-action a');
        if(dest)dest.href='winter-'+m.id+'.html?color='+encodeURIComponent(v.colorId);
      }));
    }
    const requested=new URLSearchParams(location.search).get('color');
    if(requested && host.classList.contains('store-layout'))[...wrap.querySelectorAll('input')].find(r=>r.value===requested)?.click();
  }

  const root=document.querySelector('[data-builder]');
  if(root) {
    root.hidden=false;
    const get=s=>root.querySelector(s),empty=()=>({model:null,color:null});
    const request=Number(new URLSearchParams(location.search).get('size'));
    let size=data.sizes.some(s=>s.size===request)?request:4, slots=Array.from({length:size},empty), active=0;
    const nameOf=s=>data.models.find(m=>m.id===s.model)?.name;
    function focusRadio(name,value){const r=[...root.querySelectorAll('input')].find(i=>i.name===name && i.value===String(value));r?.focus({preventScroll:true});}
    function confirmEdit(text,action,done){
      const dialog=get('.atelier-confirm');
      dialog.querySelector('h2').textContent=text;
      dialog.querySelector('[data-confirm-ok]').textContent=action;
      dialog.returnValue='cancel';
      dialog.addEventListener('close',()=>done(dialog.returnValue==='ok'),{once:true});
      dialog.showModal();
    }
    function draw(){
      get('[data-sizes]').replaceChildren(...data.sizes.map(({size:n})=>radio('size',n,el('span',n+' szt.'),n===size,()=>{
        const lost=slots.slice(n).filter(s=>s.model).length;
        const resize=yes=>{
          if(yes){slots=Array.from({length:n},(_,i)=>slots[i]||empty());size=n;active=Math.min(active,n-1)}
          draw();focusRadio('size',size);
        };
        if(lost)confirmEdit('Usunąć wybory z miejsc poza nowym zestawem?', 'Zmień rozmiar',resize);
        else resize(true);
      })));
      get('[data-slots]').replaceChildren(...slots.map((slot,i)=>{
        const b=el('button',null,'slot');b.type='button';b.setAttribute('aria-pressed',String(i===active));
        const model=data.models.find(m=>m.id===slot.model),v=variantFor(data,slot),src=v?.photo?.thumb||model?.thumb;
        b.append(el('small','Nº '+String(i+1).padStart(2,'0')));
        if(src)b.append(picture(src));else b.append(el('span','＋','slot-mark'));
        b.append(el('strong',nameOf(slot)||'Wybierz formę'),el('small',model?(v?.label||'Wybierz kolor'):''));
        b.setAttribute('aria-label','Bombka '+(i+1)+': '+(nameOf(slot)||'puste miejsce')+(v?' / '+v.label:''));
        b.onclick=()=>{active=i;draw();get('[data-slots]').children[i].focus({preventScroll:true})};return b;
      }));
      const slot=slots[active],model=data.models.find(m=>m.id===slot.model);
      get('[data-edit-title]').textContent='Bombka '+String(active+1).padStart(2,'0')+' / '+String(size).padStart(2,'0');
      get('[data-models]').replaceChildren(...data.models.map(m=>{
        const tile=el('span',null,'model-tile');if(m.thumb)tile.append(picture(m.thumb));
        tile.append(el('small',m.family),el('strong',m.name));
        return radio('model',m.id,tile,slot.model===m.id,id=>{slots[active]={model:id,color:null};draw();focusRadio('model',id)});
      }));
      const colors=get('[data-colors]');
      if(!model?.variants.length)colors.replaceChildren(el('p',model?'Paletę tego modelu pokażemy po zatwierdzeniu próbek.':'Najpierw wybierz formę.','help'));
      else colors.replaceChildren(...model.variants.map(v=>{
        const ok=eligible(v,slots,active,data);
        return radio('slot-color',v.colorId,swatch(v,!ok),slot.color===v.colorId,id=>{
          if(eligible(v,slots,active,data)){slot.color=id;draw();focusRadio('slot-color',id)}
        },!ok);
      }));
      const next=get('[data-next]');next.disabled=active===size-1;
      next.onclick=()=>{active++;draw();get('[data-slots]').children[active].focus()};
      const {done,groups}=summary(data,slots);
      const models=groups.reduce((count,group)=>count+group.count,0);
      get('[data-count]').textContent='Modele: '+models+'/'+size+' · Kolory: '+done+'/'+size;
      get('.progress-line span').style.width=((models+done)/(2*size)*100)+'%';
      get('[data-summary-note]').textContent=done===size?'Kompozycja kompletna.':groups.length?'Pozycję dopełnia wybór dostępnego koloru.':'Twoje formy pojawią się tutaj.';
      get('[data-summary]').replaceChildren(...groups.map(g=>{const li=el('li');li.append(el('strong',g.name),el('span',g.label+' · '+g.count+' szt.'));return li}));
      const rule=data.sizes.find(s=>s.size===size);
      get('[data-totals]').textContent=[rule.grossGrosz==null?'':'Zestaw: '+money(rule.grossGrosz)+' brutto',
        rule.shippingGrosz==null?'':'Kurier: '+money(rule.shippingGrosz)+' brutto'].filter(Boolean).join(' · ');
      get('[data-reset]').disabled=!groups.length;
      get('[data-reset]').onclick=()=>confirmEdit('Wyczyścić wszystkie wybory w zestawie?', 'Wyczyść',yes=>{
        if(yes){slots=Array.from({length:size},empty);active=0;draw();get('[data-slots]').children[0].focus()}
      });
    }
    draw();
  }
}
