'use strict';
// Stock is a catalog snapshot, never a reservation.
function variantFor(data, slot) {
  return data.models.find(m => m.id === slot.model)?.variants.find(v => v.colorId === slot.color);
}
function eligible(v, slots, index, data, otherSlots=[]) {
  if (!v || !v.available || !v.sku || !Number.isInteger(v.stock) || v.stock < 1) return false;
  return slots.filter((s,i) => i !== index && variantFor(data,s)?.sku === v.sku).length + otherSlots.filter(s=>variantFor(data,s)?.sku===v.sku).length < v.stock;
}
function summary(data,slots,preview=false,otherSlots=[]) {
  const groups = new Map(); let done=0;
  slots.forEach((slot,i) => {
    const m=data.models.find(x=>x.id===slot.model); if (!m) return;
    const v=variantFor(data,slot);
    if (preview ? Boolean(v) : eligible(v,slots,i,data,otherSlots)) done++;
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
    const face=el('span',null,'swatch');
    if(v.hex){const dot=el('i');dot.style.backgroundColor=v.hex;face.append(dot)}
    face.append(el('span',v.label+(disabled?' · niedostępny':'')));return face;
  }
  for (const block of document.querySelectorAll('[data-color-model]')) {
    const m=data.models.find(x=>x.id===block.dataset.colorModel);
    const wrap=block.querySelector('[data-swatches]'),status=block.querySelector('[data-variant-status]');
    if (!m?.variants.length) continue;
    wrap.setAttribute('role','radiogroup');wrap.setAttribute('aria-label','Wybierz kolor: '+m.name);
    status.textContent='Wybierz wykończenie.';
    const host=block.closest('.product-card,.store-layout'),cover=host.querySelector('.store-cover,.store-gallery');
    const preview=el('figure',null,'variant-photo');preview.hidden=true;cover.before(preview);
    for(const v of m.variants) {
      wrap.append(radio('color-'+m.id,v.colorId,swatch(v,false),false,()=>{
        status.textContent=[v.label,v.grossGrosz==null?'':money(v.grossGrosz)+' brutto',
          v.photo?'':'Zdjęcie tego koloru w przygotowaniu.'].filter(Boolean).join(' · ');
        if(v.photo) {
          const img=picture(v.photo.image,v.photo.alt), a=el('a');
          a.href=host.classList.contains('product-card')?'winter-'+m.id+'.html?color='+encodeURIComponent(v.colorId):v.photo.image;
          a.append(img);preview.replaceChildren(a,el('figcaption',m.name+' / '+v.label));cover.hidden=true;preview.hidden=false;
        } else {
          preview.replaceChildren();cover.hidden=false;preview.hidden=true;
        }
        const dest=host.querySelector('.premiere-action a');
        if(dest)dest.href='winter-'+m.id+'.html?color='+encodeURIComponent(v.colorId);
        for(const link of host.querySelectorAll('[data-single-entry]'))link.href='winter-zestaw-4.html?size=1&model='+encodeURIComponent(m.id)+'&color='+encodeURIComponent(v.colorId)+'#kompozycja';
      }));
    }
    const requested=new URLSearchParams(location.search).get('color');
    if(requested && host.classList.contains('store-layout'))[...wrap.querySelectorAll('input')].find(r=>r.value===requested)?.click();
  }

  const root=document.querySelector('[data-builder]');
  if(root) {
    root.hidden=false;
    const get=s=>root.querySelector(s),empty=()=>({model:null,color:null});
    const query=new URLSearchParams(location.search),request=Number(query.get('size'));
    let commerceMode='closed', busy=false, attempt=null, smallShipping=null, liveInfo=null, expectedTotal=null;
    const commerceOpen=()=>commerceMode!=='closed';
    const acceptance=get('[data-accept-terms]');acceptance.onchange=()=>draw();
    function validateLive(info){
      const has=(v)=>typeof v==='string'&&Boolean(v.trim());
      if(location.protocol!=='https:'||!/^[a-f0-9]{64}$/i.test(info.approvalVersion||'')||
          ![info.sellerName,info.sellerContact,info.returnsSummary,info.complaintsSummary,info.dispatchNotice].every(has))return false;
      const urls=[info.termsUrl,info.returnsUrl,info.privacyUrl];
      if(!urls.every(u=>has(u)&&u.startsWith('/')&&!u.startsWith('//')&&new URL(u,location.href).origin===location.origin))return false;
      return data.models.every(m=>{
        const p=info.productInfo?.[m.id];
        return p&&['name','material','dimensions','producer','address','email','warnings'].every(k=>has(p[k]));
      });
    }
    function showLive(info){
      for(const [selector,key] of [['[data-terms-link]','termsUrl'],['[data-returns-link]','returnsUrl'],['[data-privacy-link]','privacyUrl']]){
        const a=get(selector);a.href=info[key];a.target='_blank';a.rel='noopener';
      }
      get('[data-live-seller]').textContent='Sprzedawca: '+info.sellerName+' · '+info.sellerContact;
      get('[data-live-dispatch]').textContent=info.dispatchNotice;
      get('[data-live-returns]').textContent='Zwroty: '+info.returnsSummary;
      get('[data-live-complaints]').textContent='Reklamacje: '+info.complaintsSummary;
    }
    let size=data.sizes.some(s=>s.size===request)?request:data.featured, slots=Array.from({length:size},empty), active=0;
    const saved=[];
    const quotedPacks=()=>saved.length && !slots.some(s=>s.model)?[...saved]:[...saved,slots];
    const priceFor=pack=>data.sizes.find(r=>r.size===pack.length).grossGrosz;
    function removeCurrent(){
      if(saved.length){slots=saved.pop();size=slots.length;}else{slots=Array.from({length:size},empty)}
      active=0;acceptance.checked=false;draw();
    }
    if(size===1){
      const model=data.models.find(m=>m.id===query.get('model'));
      if(model)slots[0]={model:model.id,color:model.variants.find(v=>v.colorId===query.get('color'))?.colorId||null};
    }
    const codeField=get('[data-coupon]'),codeStatus=get('[data-coupon-status]');
    const showCode=()=>{codeStatus.textContent=codeField.value.trim()?'Brak aktywnej promocji. Usuń kod, aby kontynuować w cenie regularnej.':'Wpisz kod, który chcesz sprawdzić.'};
    get('[data-apply-code]').onclick=showCode;
    codeField.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();showCode()}};
    codeField.oninput=()=>{codeStatus.textContent='';draw()};
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
      root.inert=busy;
      const previous=saved.flat();
      get('[data-sizes]').replaceChildren(...data.sizes.map(({size:n})=>radio('size',n,el('span',(n===data.featured?'Polecamy · ':'')+n+' szt.'),n===size,()=>{
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
        const ok=!commerceOpen() || eligible(v,slots,active,data,previous);
        return radio('slot-color',v.colorId,swatch(v,!ok),slot.color===v.colorId,id=>{
          if(!commerceOpen() || eligible(v,slots,active,data,previous)){slot.color=id;draw();focusRadio('slot-color',id)}
        },!ok);
      }));
      const next=get('[data-next]');next.disabled=active===size-1;
      next.onclick=()=>{active++;draw();get('[data-slots]').children[active].focus()};
      const {done,groups}=summary(data,slots,!commerceOpen(),previous);
      const models=groups.reduce((count,group)=>count+group.count,0);
      get('[data-count]').textContent='Modele: '+models+'/'+size+' · Kolory: '+done+'/'+size;
      get('.progress-line span').style.width=((models+done)/(2*size)*100)+'%';
      get('[data-summary-note]').textContent=done===size?'Kompozycja kompletna.':groups.length?'Pozycję dopełnia wybór dostępnego koloru.':'Twoje formy pojawią się tutaj.';
      get('[data-summary]').replaceChildren(...groups.map(g=>{const li=el('li');li.append(el('strong',g.name),el('span',g.label+' · '+g.count+' szt.'));return li}));
      const packs=quotedPacks(), all=packs.flat(), count=all.length;
      const merchandise=packs.reduce((sum,p)=>sum+priceFor(p),0);
      const ready=summary(data,all,!commerceOpen()).done===count;
      const add=get('[data-add-pack]');add.disabled=busy||done!==size||saved.length+1>=10;
      add.onclick=()=>{
        if(add.disabled)return;
        saved.push(slots);slots=Array.from({length:1},empty);size=1;active=0;acceptance.checked=false;draw();
        get('[data-sizes]').querySelectorAll('input')[0]?.focus();
      };
      get('[data-basket]').replaceChildren(...packs.map((p,i)=>{
        const li=el('li'), current=p===slots;
        const completed=summary(data,p,!commerceOpen(),all.filter(s=>!p.includes(s))).done===p.length;
        li.append(el('strong',(p.length===1?'Pojedyncza ozdoba':'Komplet '+p.length+' szt.')+' · '+money(priceFor(p))));
        const labels=summary(data,p,true).groups.map(g=>g.count+' × '+g.name+' / '+g.label).join('; ');
        li.append(el('span',(labels||'Wybierz wzór i kolor')+(completed?'': ' · do uzupełnienia')));
        const remove=el('button','Usuń','reset-set');remove.type='button';
        remove.setAttribute('aria-label','Usuń pozycję '+(i+1)+' z koszyka');
        remove.onclick=()=>{if(current)removeCurrent();else{saved.splice(i,1);acceptance.checked=false;draw()}};
        if(p.some(s=>s.model))li.append(remove);
        return li;
      }));
      const shipping=count>=data.freeFrom?0:(commerceOpen()?smallShipping:data.sizes[0].shippingGrosz);
      const total=shipping==null?null:merchandise+shipping;
      get('[data-totals]').textContent=[count+' szt. · Ozdoby: '+money(merchandise)+' brutto',
        shipping===0?'Kurier InPost w Polsce w cenie':shipping==null?'Dostawa płatna osobno':'Kurier InPost: '+money(shipping),
        total===null?'':'Razem: '+money(total)].filter(Boolean).join(' · ');
      expectedTotal=total;
      const live=commerceMode==='live';get('[data-live-facts]').hidden=!live;
      if(live){
        const picked=[...new Set(all.map(s=>s.model).filter(Boolean))];
        get('[data-live-products]').replaceChildren(...picked.map(id=>{
          const p=liveInfo.productInfo[id];
          return el('p',p.name+' · '+p.material+' · '+p.dimensions+'. Producent: '+p.producer+', '+p.address+' · '+p.email+'. '+p.warnings);
        }));
      }
      const btn=get('[data-checkout]'), payment=get('[data-payment-status]');
      btn.hidden=!commerceOpen();get('[data-notify]').hidden=commerceOpen();
      btn.textContent=live?'Przejdź do płatności — '+(total===null?'':money(total)):'Przejdź do płatności testowej';
      btn.disabled=busy || !ready || total===null || Boolean(codeField.value.trim()) || (live&&!acceptance.checked);
      payment.textContent=!commerceOpen()?'Możesz ułożyć kompozycję. Zapisz się, aby otrzymać informację o rozpoczęciu sprzedaży.':
        busy?'Przygotowujemy płatność…':(live?'Zamówienie z obowiązkiem zapłaty potwierdzisz w następnym kroku na stronie Stripe. ':'Tryb testowy — bez pobrania pieniędzy. ')+(!ready?'Wybierz dostępny kolor każdej ozdoby.':total===null?'Koszt dostawy nie został ustawiony.':codeField.value.trim()?'Usuń nieaktywny kod, aby przejść dalej.':live&&!acceptance.checked?'Zapoznaj się z regulaminem i zaakceptuj go.':'Sprawdź skład i kwotę przed przejściem do płatności.');
      get('[data-reset]').disabled=!groups.length;
      get('[data-reset]').onclick=()=>confirmEdit('Wyczyścić wszystkie wybory w zestawie?', 'Wyczyść',yes=>{
        if(yes){slots=Array.from({length:size},empty);active=0;draw();get('[data-slots]').children[0].focus()}
      });
    }
    get('[data-checkout]').onclick=async()=>{
      if(!commerceOpen()||busy||get('[data-checkout]').disabled)return;
      const orderPacks=quotedPacks().map(p=>p.map(s=>({modelId:s.model,colorId:s.color})));
      const contents=orderPacks.length===1?{selections:orderPacks[0]}:{packs:orderPacks}, checkoutTotal=expectedTotal;
      const acceptanceProof=commerceMode==='live'?{termsAccepted:acceptance.checked,approvalVersion:liveInfo.approvalVersion}:{};
      const signature=JSON.stringify([contents,checkoutTotal,acceptanceProof]);
      if(!attempt||attempt.signature!==signature)attempt={signature,id:crypto.randomUUID()};
      busy=true;draw();
      try{
        const res=await fetch('api/checkout.php',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','Accept':'application/json'},
          body:JSON.stringify({...contents,code:codeField.value.trim(),requestId:attempt.id,...acceptanceProof})});
        const json=await res.json();
        if(!res.ok)throw new Error(json.message||'Próba nie została przyjęta. Sprawdź dostępność i spróbuj ponownie.');
        if(!Number.isInteger(checkoutTotal)||json.totalGrosz!==checkoutTotal)throw new Error('Kwota zamówienia uległa zmianie. Wróć do wyboru i sprawdź podsumowanie.');
        const next=new URL(json.url);
        if(next.origin!=='https://checkout.stripe.com')throw new Error('Nie można otworzyć strony płatności.');
        location.assign(next.href);
      }catch(e){busy=false;draw();get('[data-payment-status]').textContent=e instanceof Error?e.message:'Nie udało się rozpocząć próby.'}
    };
    async function availability(){
      try{
        const res=await fetch('api/status.php',{credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}});
        if(!res.ok||!res.headers.get('content-type')?.includes('application/json'))return;
        const info=await res.json();
        if(!['test','live'].includes(info.mode)||info.available!==true||info.currency!=='PLN'||info.freeCourierFromOrnaments!==data.freeFrom||typeof info.stock!=='object'||!info.stock)return;
        if(info.mode==='live'&&!validateLive(info))return;
        for(const model of data.models)for(const v of model.variants){
          const n=info.stock[model.id+':'+v.colorId];
          v.stock=Number.isInteger(n)&&n>0?n:0;v.available=v.stock>0;
        }
        smallShipping=Number.isInteger(info.smallOrderCourierGrosz)&&info.smallOrderCourierGrosz>=0?info.smallOrderCourierGrosz:null;
        if(info.mode==='live'){
          if(smallShipping===null)return;
          liveInfo=info;showLive(info);
        }
        commerceMode=info.mode;draw();
      }catch{/* A static catalog works without the private checkout. */}
    }
    draw();availability();
  }
}
