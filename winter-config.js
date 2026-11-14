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
function missingChoice(data,slot,slots,index,preview=false,others=[]) {
  if(!data.models.some(m=>m.id===slot.model))return 'Wybierz model';
  const v=variantFor(data,slot);
  if(!v)return 'Wybierz kolor';
  return !preview&&!eligible(v,slots,index,data,others)?'Wybierz dostępny kolor':'';
}
if (typeof module !== 'undefined') module.exports={variantFor,eligible,summary,missingChoice};
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
    if(v.hex||['dual','red-matte','white','marble'].includes(v.colorId)){const dot=el('i',null,'color-chip color-chip-'+v.colorId);dot.setAttribute('aria-hidden','true');if(v.hex)dot.style.backgroundColor=v.hex;face.append(dot)}
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
    let delivery='courier', lockerAvailable=false, lockerFee=null, geoToken='', selectedPoint=null;
    const mockNotice='TEST / MOCK — bez połączenia z InPost';
    let mockPoints=false, localMockDemo=false;
    let pointSeq=0, mapSeq=0, mapTimer=null, sdk=null, checking=false, pointMessage='';
    const courier=get('[data-delivery-courier]'), locker=get('[data-delivery-locker]'), pointInput=get('[data-point-id]');
    const mapDialog=get('[data-map-dialog]'), mapButton=get('[data-open-map]'), mapHost=get('[data-map-host]');
    const mockBanner=el('p',null,'point-receipt'), mockPicker=el('label'), mockSelect=el('select');
    mockBanner.append(el('small','Dostawa testowa — bez nadania przesyłki.'));mockBanner.hidden=true;mockBanner.setAttribute('data-points-mock-notice','');
    mockPicker.append(el('span','Wybierz punkt odbioru'),mockSelect);mockPicker.hidden=true;
    mockPicker.style.flexWrap='wrap';mockSelect.style.maxWidth='100%';mockSelect.style.width='100%';mockSelect.style.minHeight='44px';mockSelect.style.font='inherit';
    mockSelect.setAttribute('data-test-point-picker','');mockSelect.setAttribute('aria-label','Wybierz testowy punkt odbioru');
    get('[data-delivery-picker]').append(mockBanner);get('[data-locker-panel]').append(mockPicker);
    const normalizePoint=id=>typeof id==='string'?id.trim().toUpperCase():'';
    const validId=id=>/^[A-Z0-9][A-Z0-9_-]{2,31}$/.test(id);
    function setMethod(method){
      if(busy||method==='locker'&&!lockerAvailable)return;
      delivery=method;checking=false;pointSeq++;pointMessage='';acceptance.checked=false;
      draw();
    }
    courier.onchange=()=>setMethod('courier');locker.onchange=()=>setMethod('locker');
    function resetPoint(){
      pointSeq++;checking=false;selectedPoint=null;pointMessage='';acceptance.checked=false;draw();
    }
    pointInput.oninput=resetPoint;
    async function checkPoint(){
      if(delivery!=='locker'||!lockerAvailable||busy)return;
      const id=normalizePoint(pointInput.value),seq=++pointSeq;selectedPoint=null;acceptance.checked=false;
      if(!validId(id)){checking=false;pointMessage='Wpisz kod automatu Paczkomat®.';draw();return}
      checking=true;pointMessage='Sprawdzamy punkt odbioru…';draw();
      try{
        const res=await fetch('api/pickup-point.php?id='+encodeURIComponent(id),{credentials:'same-origin',cache:'no-store',headers:{Accept:'application/json'}});
        const result=await res.json().catch(()=>null);
        if(seq!==pointSeq||delivery!=='locker')return;
        if(!res.ok||!result||result.id!==id||typeof result.address!=='string'||!result.address.trim()||
            (mockPoints&&(result.provider!=='mock'||result.notice!==mockNotice||!id.startsWith('TEST')||!result.address.includes(mockNotice)))){
          throw new Error(!res.ok&&typeof result?.message==='string'?result.message:'Nie udało się potwierdzić adresu. Sprawdź kod lub wybierz inny automat.');
        }
        selectedPoint={id,address:result.address.trim()};pointInput.value=id;pointMessage='';
      }catch(e){if(seq===pointSeq)pointMessage=mockPoints?'Nie udało się wybrać punktu. Wybierz inny lub spróbuj ponownie.':e instanceof Error&&e.name==='Error'?e.message:'Nie udało się połączyć z wyszukiwarką automatów. Spróbuj ponownie.'}
      finally{if(seq===pointSeq){checking=false;draw()}}
    }
    get('[data-find-point]').onclick=checkPoint;
    mockSelect.onchange=()=>{if(busy||checking||!mockPoints)return;pointInput.value=mockSelect.value;resetPoint();if(pointInput.value)return checkPoint()};
    pointInput.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();checkPoint()}};
    function loadMapSdk(){
      if(mockPoints)return Promise.reject(new Error(mockNotice));
      if(sdk)return sdk;
      const host=commerceMode==='test'?'https://sandbox-easy-geowidget-sdk.easypack24.net':'https://geowidget.inpost.pl';
      sdk=new Promise((resolve,reject)=>{
        const script=el('script'),css=el('link');css.rel='stylesheet';css.href=host+'/inpost-geowidget.css';
        script.src=host+'/inpost-geowidget.js';script.async=true;script.referrerPolicy='strict-origin-when-cross-origin';
        script.onload=resolve;script.onerror=()=>{script.remove();css.remove();reject(new Error('sdk'))};
        document.head.append(css,script);
      }).catch(e=>{sdk=null;throw e});
      return sdk;
    }
    mapDialog.onclose=()=>{clearTimeout(mapTimer);mapSeq++;mapHost.replaceChildren();mapButton.focus()};
    get('[data-close-map]').onclick=()=>mapDialog.close();
    mapButton.onclick=async()=>{
      if(mockPoints||!geoToken||!lockerAvailable||delivery!=='locker'||busy)return;
      const seq=++mapSeq,mapStatus=get('[data-map-status]');
      mapDialog.showModal();mapStatus.textContent='Ładowanie mapy InPost…';
      const trouble='Mapa nie odpowiada. Zamknij ją i wpisz kod automatu w koszyku.';
      const timer=mapTimer=setTimeout(()=>{if(seq===mapSeq&&mapDialog.open)mapStatus.textContent=trouble},15000);
      try{
        await loadMapSdk();if(seq!==mapSeq||!mapDialog.open){clearTimeout(timer);return}
        const widget=el('inpost-geowidget');
        for(const [key,val] of Object.entries({token:geoToken,language:'pl',country:'PL',config:'parcelCollect'}))widget.setAttribute(key,val);
        widget.addEventListener('inpost.geowidget.init',event=>{
          const api=event.detail?.api;if(seq!==mapSeq||!mapDialog.open||typeof api?.addPointSelectedCallback!=='function')return;
          clearTimeout(timer);mapStatus.textContent='';
          api.changePointsType?.('PARCEL_LOCKER');
          api.addPointSelectedCallback(point=>{
            if(seq!==mapSeq||!mapDialog.open||!validId(normalizePoint(point?.name)))return;
            mapDialog.close();pointInput.value=normalizePoint(point.name);checkPoint();
          });
        },{once:true});
        mapHost.replaceChildren(widget);
      }catch{clearTimeout(timer);if(seq===mapSeq&&mapDialog.open)mapStatus.textContent=trouble}
    };
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
    let step=1;
    function goStep(n){if(busy)return;step=n;draw();const panel=get('[data-stage="'+n+'"]');panel.focus?.({preventScroll:true});panel.scrollIntoView?.({block:'start',behavior:'instant'});}
    function editSlot(pack,index,missing=false){
      if(busy)return;
      if(pack!==slots){const i=saved.indexOf(pack);if(i<0)return;if(slots.some(s=>s.model))saved[i]=slots;else saved.splice(i,1);slots=pack;size=pack.length;}
      active=index;step=2;draw();const editor=get(missing&&nameOf(slots[index])?'[data-colors]':'.edit-position');editor.setAttribute('tabindex','-1');editor.focus?.({preventScroll:true});editor.scrollIntoView?.({block:missing?'center':'start',behavior:'instant'});
    }
    const issueFor=(slot,i,pack)=>missingChoice(data,slot,pack,i,!commerceOpen(),quotedPacks().filter(p=>p!==pack).flat());
    function firstMissing(){for(const pack of quotedPacks())for(let i=0;i<pack.length;i++)if(issueFor(pack[i],i,pack))return {pack,index:i};return null;}
    get('[data-start]').onclick=()=>goStep(2);get('[data-review]').onclick=()=>goStep(3);
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
      for(let n=1;n<=3;n++)get('[data-stage="'+n+'"]').hidden=step!==n;
      get('.workspace').hidden=step!==2;
      get('[data-steps]').replaceChildren(...['Rozmiar','Komponowanie','Podsumowanie'].map((label,i)=>{const b=el('button',(i+1)+'. '+label);b.type='button';b.setAttribute('aria-current',step===i+1?'step':'false');b.onclick=()=>goStep(i+1);return b}));
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
        const issue=issueFor(slot,i,slots);b.setAttribute('data-complete',String(!issue));b.append(el('span',issue||'✓ Gotowa','slot-state'));
        b.setAttribute('aria-label','Bombka '+(i+1)+': '+(nameOf(slot)||'puste miejsce')+(v?' / '+v.label:'')+' — '+(issue||'gotowa'));
        b.onclick=()=>editSlot(slots,i);return b;
      }));
      const slot=slots[active],model=data.models.find(m=>m.id===slot.model);
      get('[data-edit-title]').textContent='Bombka '+String(active+1).padStart(2,'0')+' / '+String(size).padStart(2,'0');
      get('[data-edit-status]').textContent=issueFor(slot,active,slots)||'Model i kolor wybrane. Możesz przejść dalej.';
      const colorField=get('[data-color-field]');
      get('[data-models]').replaceChildren(...data.models.map(m=>{
        const tile=el('span',null,'model-tile');if(m.thumb)tile.append(picture(m.thumb));
        tile.append(el('small',m.family),el('strong',m.name));
        const card=el('div',null,'model-card');card.setAttribute('data-selected',String(slot.model===m.id));
        card.append(radio('model',m.id,tile,slot.model===m.id,id=>{slots[active]={model:id,color:null};draw();focusRadio('model',id)}));
        if(slot.model===m.id)card.append(colorField);
        return card;
      }));
      colorField.hidden=!model;if(!model)get('[data-color-home]').append(colorField);
      const colors=get('[data-colors]');
      if(!model?.variants.length)colors.replaceChildren(el('p',model?'Paletę tego modelu pokażemy po zatwierdzeniu próbek.':'Najpierw wybierz formę.','help'));
      else colors.replaceChildren(...model.variants.map(v=>{
        const ok=!commerceOpen() || eligible(v,slots,active,data,previous);
        return radio('slot-color',v.colorId,swatch(v,!ok),slot.color===v.colorId,id=>{
          if(!commerceOpen() || eligible(v,slots,active,data,previous)){slot.color=id;draw();focusRadio('slot-color',id)}
        },!ok);
      }));
      const next=get('[data-next]');next.disabled=false;next.textContent=active===size-1?'Zobacz podsumowanie →':'Następna bombka →';
      next.onclick=()=>{if(active===size-1)goStep(3);else editSlot(slots,active+1)};
      const prev=get('[data-prev]');prev.disabled=active===0;prev.onclick=()=>{if(active>0)editSlot(slots,active-1)};
      const {done,groups}=summary(data,slots,!commerceOpen(),previous);
      const models=groups.reduce((count,group)=>count+group.count,0);
      get('[data-count]').textContent='Modele: '+models+'/'+size+' · Kolory: '+done+'/'+size;
      get('[data-compose-count]').textContent='Gotowe bombki: '+done+' z '+size;
      get('.progress-line span').style.width=((models+done)/(2*size)*100)+'%';
      get('[data-summary-note]').textContent=done===size?'Kompozycja kompletna.':'Uzupełnij wskazane pozycje. Każda bombka potrzebuje modelu i koloru.';
      get('[data-summary]').replaceChildren(...groups.map(g=>{const li=el('li');li.append(el('strong',g.name),el('span',g.label+' · '+g.count+' szt.'));return li}));
      const packs=quotedPacks(), all=packs.flat(), count=all.length;
      const merchandise=packs.reduce((sum,p)=>sum+priceFor(p),0);
      const ready=summary(data,all,!commerceOpen()).done===count;
      const issues=[];
      packs.forEach((pack,pi)=>pack.forEach((s,i)=>{const reason=issueFor(s,i,pack);if(reason){const li=el('li'),b=el('button',(packs.length>1?'Zestaw '+(pi+1)+' · ':'')+'Bombka '+(i+1)+(nameOf(s)?' · '+nameOf(s):'')+': '+reason,'issue-link');b.type='button';b.onclick=()=>editSlot(pack,i,true);li.append(b);issues.push(li)}}));
      get('[data-issues]').replaceChildren(...issues);get('[data-issues]').hidden=!issues.length;
      const add=get('[data-add-pack]');add.disabled=busy||done!==size||saved.length+1>=10;
      add.onclick=()=>{
        if(add.disabled)return;
        saved.push(slots);slots=Array.from({length:1},empty);size=1;active=0;acceptance.checked=false;draw();
        goStep(1);
      };
      get('[data-basket]').replaceChildren(...packs.map((p,i)=>{
        const li=el('li'), current=p===slots;
        const completed=summary(data,p,!commerceOpen(),all.filter(s=>!p.includes(s))).done===p.length;
        li.append(el('strong',(p.length===1?'Pojedyncza ozdoba':'Komplet '+p.length+' szt.')+' · '+money(priceFor(p))));
        const labels=summary(data,p,true).groups.map(g=>g.count+' × '+g.name+' / '+g.label).join('; ');
        li.append(el('span',completed?'Wszystkie bombki gotowe':'Uzupełnij oznaczone bombki'));
        const items=el('ol',null,'individual-items');p.forEach((s,j)=>{const item=el('li'),v=variantFor(data,s),m=data.models.find(m=>m.id===s.model),src=v?.photo?.thumb||m?.thumb;
          if(src)item.append(picture(src));const copy=el('div');copy.append(el('strong','Bombka '+(j+1)+' · '+(m?.name||'Wybierz model')),el('span',v?.label||'Kolor nie został wybrany'));
          const reason=issueFor(s,j,p);copy.append(el('small',reason||'✓ Gotowa',reason?'needs-choice':'complete-choice'));item.append(copy);
          const edit=el('button','Edytuj','reset-set');edit.type='button';edit.setAttribute('aria-label','Edytuj bombkę '+(j+1)+(packs.length>1?' w zestawie '+(i+1):''));edit.onclick=()=>editSlot(p,j);item.append(edit);items.append(item)});li.append(items);
        const remove=el('button','Usuń','reset-set');remove.type='button';
        remove.setAttribute('aria-label','Usuń pozycję '+(i+1)+' z koszyka');
        remove.onclick=()=>{if(current)removeCurrent();else{saved.splice(i,1);acceptance.checked=false;draw()}};
        if(p.some(s=>s.model))li.append(remove);
        return li;
      }));
      const free=count>=data.freeFrom;
      const shipping=free?0:delivery==='locker'?lockerFee:(commerceOpen()?smallShipping:data.sizes[0].shippingGrosz);
      const shippingName=delivery==='locker'?'Paczkomat® InPost':'Kurier InPost';
      const pointRequired=delivery==='locker'&&!selectedPoint;
      get('[data-delivery-picker]').hidden=!commerceOpen();
      courier.checked=delivery==='courier';locker.checked=delivery==='locker';locker.disabled=!lockerAvailable;
      get('[data-courier-fee]').textContent=free?'w cenie':smallShipping===null?'brak wyceny':money(smallShipping);
      get('[data-locker-fee]').textContent=(!lockerAvailable?'obecnie niedostępny':free?'w cenie':money(lockerFee));
      mockBanner.hidden=!mockPoints||!commerceOpen();mockPicker.hidden=!mockPoints;
      mockSelect.disabled=busy||checking;mockSelect.value=normalizePoint(pointInput.value);
      get('[data-locker-panel]').hidden=delivery!=='locker';mapButton.hidden=mockPoints||!geoToken;
      mapButton.textContent=selectedPoint?'Zmień Paczkomat na mapie':'Wybierz Paczkomat na mapie';
      get('[data-locker-directory]').hidden=mockPoints||commerceMode!=='live';
      get('.locker-id').hidden=mockPoints;get('.locker-search').hidden=mockPoints;get('#point-help').hidden=mockPoints;
      get('[data-point-summary]').textContent=selectedPoint?'Wybrany automat: '+selectedPoint.id+' · '+selectedPoint.address.replace(mockNotice+' — ',''):'';
      get('[data-point-status]').textContent=pointMessage;
      get('[data-find-point]').disabled=checking||!pointInput.value.trim();
      const total=shipping==null?null:merchandise+shipping;
      get('[data-totals]').textContent=[count+' szt. · Ozdoby: '+money(merchandise)+' brutto',
        shipping===0?shippingName+' w Polsce w cenie':shipping==null?'Dostawa płatna osobno':shippingName+': '+money(shipping),
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
      btn.textContent=localMockDemo?'Zapisz lokalną próbę — bez płatności':live?'Przejdź do płatności — '+(total===null?'':money(total)):'Przejdź do płatności testowej';
      btn.disabled=busy;btn.setAttribute('data-ready',String(Boolean(ready&&!pointRequired&&total!==null&&!codeField.value.trim()&&(!live||acceptance.checked))));
      if(!ready)btn.textContent='Uzupełnij wybór — '+issues.length+' do poprawy';
      else if(pointRequired)btn.textContent='Wybierz punkt odbioru';
      payment.textContent=!commerceOpen()?'Możesz ułożyć kompozycję. Zapisz się, aby otrzymać informację o rozpoczęciu sprzedaży.':
        busy?'Przygotowujemy płatność…':(live?'Zamówienie z obowiązkiem zapłaty potwierdzisz w następnym kroku na stronie Stripe. ':'Zakup testowy — bez pobrania pieniędzy. ')+(!ready?'Wskażemy Ci brakujący wybór.':pointRequired?'Wybierz punkt odbioru.':total===null?'Nie udało się ustalić kosztu dostawy. Spróbuj ponownie później.':codeField.value.trim()?'Usuń nieaktywny kod, aby przejść dalej.':live&&!acceptance.checked?'Zapoznaj się z regulaminem i zaakceptuj go.':'Sprawdź skład i kwotę przed przejściem do płatności.');
      const sticky=get('[data-sticky-action]');sticky.disabled=busy;sticky.textContent=step===1?'Komponuj →':step===2?'Podsumowanie →':btn.hidden?'Uzupełnij zestaw':btn.textContent;
      get('[data-sticky-copy]').textContent=summary(data,all,!commerceOpen()).done+'/'+count+' gotowych · '+money(total??merchandise);
      sticky.onclick=()=>{if(step<3)goStep(step+1);else if(commerceOpen())btn.onclick();else{const missing=firstMissing();if(missing)editSlot(missing.pack,missing.index)}};
      get('[data-reset]').disabled=!groups.length;
      get('[data-reset]').onclick=()=>confirmEdit('Wyczyścić wszystkie wybory w zestawie?', 'Wyczyść',yes=>{
        if(yes){slots=Array.from({length:size},empty);active=0;draw();get('[data-slots]').children[0].focus()}
      });
    }
    get('[data-checkout]').onclick=async()=>{
      if(!commerceOpen()||busy||get('[data-checkout]').disabled)return;
      const missing=firstMissing();if(missing){editSlot(missing.pack,missing.index,true);return;}
      if(delivery==='locker'&&!selectedPoint){goStep(3);const target=mockPoints?mockSelect:pointInput;target.focus?.();target.scrollIntoView?.({block:'center',behavior:'instant'});return;}
      if(expectedTotal===null||codeField.value.trim())return;
      if(commerceMode==='live'&&!acceptance.checked){acceptance.focus();return;}
      const orderPacks=quotedPacks().map(p=>p.map(s=>({modelId:s.model,colorId:s.color})));
      const contents=orderPacks.length===1?{selections:orderPacks[0]}:{packs:orderPacks}, checkoutTotal=expectedTotal;
      const acceptanceProof=commerceMode==='live'?{termsAccepted:acceptance.checked,approvalVersion:liveInfo.approvalVersion}:{};
      const destination={delivery_method:delivery,...(delivery==='locker'?{pickup_point:selectedPoint.id}:{})};
      const signature=JSON.stringify([contents,checkoutTotal,acceptanceProof,destination]);
      if(!attempt||attempt.signature!==signature)attempt={signature,id:crypto.randomUUID()};
      busy=true;draw();
      try{
        const res=await fetch('api/checkout.php',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','Accept':'application/json'},
          body:JSON.stringify({...contents,...destination,code:codeField.value.trim(),requestId:attempt.id,...acceptanceProof})});
        const json=await res.json();
        if(!res.ok)throw new Error(json.message||'Próba nie została przyjęta. Sprawdź dostępność i spróbuj ponownie.');
        if(!Number.isInteger(checkoutTotal)||json.totalGrosz!==checkoutTotal)throw new Error('Kwota zamówienia uległa zmianie. Wróć do wyboru i sprawdź podsumowanie.');
        if(localMockDemo){
          if(json.local_demo!==true||!/^w26_[a-f0-9]{24}$/.test(json.orderId||''))throw new Error('Nie potwierdzono zapisu lokalnej próby.');
          busy=false;draw();get('[data-payment-status]').textContent=mockNotice+' — zapisano '+json.orderId+'. Bez płatności, Stripe i nadania przesyłki.';return;
        }
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
        const mock=info.points_provider==='mock';
        if(info.points_provider&&!['mock','inpost'].includes(info.points_provider))return;
        if(mock){
          if(info.mode!=='test'||info.points_notice!==mockNotice||info.geowidget_token!==null||
              !Array.isArray(info.test_points)||!info.test_points.length||info.test_points.length>20||
              !info.test_points.every(p=>p&&validId(p.id)&&p.id.startsWith('TEST')&&typeof p.label==='string'&&p.label.length<160))return;
        }else if(info.test_points!==undefined||info.points_notice!==undefined||info.local_mock_demo!==undefined)return;
        if(info.mode==='live'&&!validateLive(info))return;
        for(const model of data.models)for(const v of model.variants){
          const n=info.stock[model.id+':'+v.colorId];
          v.stock=Number.isInteger(n)&&n>0?n:0;v.available=v.stock>0;
        }
        smallShipping=Number.isInteger(info.smallOrderCourierGrosz)&&info.smallOrderCourierGrosz>=0?info.smallOrderCourierGrosz:null;
        lockerFee=Number.isInteger(info.locker_amount_grosze)&&info.locker_amount_grosze>0?info.locker_amount_grosze:null;
        lockerAvailable=info.locker_available===true&&lockerFee!==null;
        mockPoints=mock;localMockDemo=mock&&info.local_mock_demo===true&&['localhost','127.0.0.1','[::1]'].includes(location.hostname);
        geoToken=!mockPoints&&lockerAvailable&&typeof info.geowidget_token==='string'?info.geowidget_token.trim():'';
        if(mockPoints){
          const placeholder=el('option','Wybierz testowy punkt…');placeholder.value='';
          mockSelect.replaceChildren(placeholder,...info.test_points.filter(p=>['TEST01M','TEST02M'].includes(p.id)).map(p=>{const o=el('option',p.id+' — punkt testowy '+(p.id==='TEST01M'?'A':'B'));o.value=p.id;return o}));
          get('#point-help').textContent='Wybierz jeden z dwóch punktów testowych.';
        }
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
