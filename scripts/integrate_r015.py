"""Generate the approved presentation around the existing checkout controller.
No network, secrets, database access or deployment.
"""
from pathlib import Path
import json,re,shutil,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1]
P=ROOT.parent/'winter26-design-r01-5/design-r01'
A=ROOT/'assets/winter26-r015';A.mkdir(parents=True,exist_ok=True)
BASE='ec8495f5716b001d43e81f078e7de2b97f16718d'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT).decode('utf-8')
def write(path,text):(ROOT/path).write_text(text,encoding='utf-8',newline='\n')
def replace(s,a,b):
    assert a in s,('Missing source fragment',a[:100])
    return s.replace(a,b)

old=original('winter-zestaw-4.html')
options=re.search(r'<script type="application/json" id="winter-options">.*?</script>',old,re.S).group()
data=json.loads(re.search(r'id="winter-options">(.*?)</script>',options,re.S).group(1))
consent=re.search(r'<script>\s*window.PF_GA_MEASUREMENT_ID.*?</script>',old,re.S).group()
cookie=re.search(r'<div class="cookie-banner".*?</div>\s*</div>',old,re.S).group()
delivery=re.search(r'<fieldset class="delivery-picker".*?</fieldset>',old,re.S).group()
legal=re.search(r'<section data-live-facts.*?</section>',old,re.S).group()
coupon=re.search(r'<div class="coupon-entry".*?</div>\s*<p.*?</p></div>',old,re.S).group()
dialogs=re.search(r'<dialog class="locker-map".*?</dialog>\s*<dialog class="atelier-confirm".*?</dialog>',old,re.S).group()

for name in ['r01.css','r012.css','r013.css','gallery.css','approval.css']:
    shutil.copyfile(P/name,A/name)
media=json.loads((P/'evidence-r01-5/media-manifest.json').read_text(encoding='utf-8'))
allowed=[m for m in media if m['galleryIncluded']]
assert len(allowed)==25 and sum(m['ownerStatus']=='OWNER APPROVED' for m in allowed)==1
for p in (P/'assets').glob('*'):
    if p.is_file():shutil.copyfile(p,A/p.name)
for m in allowed:
    paths=[m['zoom']]+[d['file'] for d in m['derivatives']]
    for name in paths:
        src=P/name;dest=A/name.removeprefix('assets/');dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(src,dest)
    assert hashlib.sha256((P/m['zoom']).read_bytes()).hexdigest()==m['sourceSha256']
minimal=[]
for m in allowed:
    item={k:m[k] for k in ('id','modelId','colorId','role','label','alt','width','height','galleryIncluded','colorConfirmed','ownerStatus','sourceSha256')}
    for k in ('src','thumb','zoom','srcset'):item[k]=m[k].replace('assets/','/assets/winter26-r015/')
    minimal.append(item)
(A/'variant-media.js').write_text('export const variantMedia = '+json.dumps(minimal,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
approved=next(m for m in minimal if m['ownerStatus']=='OWNER APPROVED')
(A/'approval-state.js').write_text('const approved='+json.dumps({k:approved[k] for k in ('id','modelId','colorId','role','sourceSha256')})+';\nexport const ownerApprovalFor = item => Object.entries(approved).every(([k,v])=>item[k]===v)?approved:null;\n',encoding='utf-8')
for name in ('gallery.js','gallery-state.js'):
    content=(P/name).read_text(encoding='utf-8')
    # Gallery navigation must never collide with the checkout controller's selectors.
    content=content.replace('data-prev','data-photo-prev').replace('data-next','data-photo-next')
    (A/name).write_text(content,encoding='utf-8')
catalog=json.loads((P/'catalog.js').read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
catalog={'models':[{k:m[k] for k in ('id','name','family','description','photos')} for m in catalog['models']], 'colors':catalog['colors']}
(A/'catalog.js').write_text('export const catalog = '+json.dumps(catalog,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')

def shell(html,kind):
    html=re.sub(r'<div class="preview-bar">.*?</div>','<div class="preview-bar"><span>WINTER 26 / Test sklepu</span><a href="/api/test-access.php">Dostęp testera</a></div>',html,flags=re.S)
    html=re.sub(r'<a[^>]*href="review.html"[^>]*>.*?</a>','',html)
    html=html.replace(' — Pracownia Form R01.5',' — Pracownia Form')
    html=html.replace('Do przejścia przez interaktywny prototyp włącz JavaScript.','Do korzystania z konfiguratora i galerii włącz JavaScript.')
    html=html.replace('href="compose.html"','href="/winter-zestaw-4.html"')
    html=html.replace('href="index.html','href="/winter-26.html')
    for m in catalog['models']:html=html.replace('product.html?model='+m['id'],'/winter-'+m['id']+'.html')
    html=html.replace('assets/','/assets/winter26-r015/')
    for name in ('r01.css','r012.css','r013.css','gallery.css','approval.css'):html=html.replace('href="'+name+'"','href="/assets/winter26-r015/'+name+'"')
    html=html.replace('<script type="module" src="r01.js"></script>','<link rel="stylesheet" href="/assets/winter26-r015/integration.css"><script type="module" src="/assets/winter26-r015/ui.js"></script>')
    html=html.replace('</head>',consent+'</head>')
    html=html.replace('</nav><a href="#top" class="back-top"','<button type="button" class="text-button cookie-settings-link" data-cookie-settings aria-controls="cookie-settings" aria-expanded="false">Ustawienia cookies</button></nav><a href="#top" class="back-top"')
    html=html.replace('</body>',cookie+'<script src="/script.js"></script></body>')
    return html

landing=shell((P/'index.html').read_text(encoding='utf-8'),'landing')
write('winter-26.html',landing)
# The root landing is a staging overlay in the release builder; portfolio source stays intact.
for model in catalog['models']:
    page=shell((P/'product.html').read_text(encoding='utf-8'),'product')
    page=page.replace('data-page="product"','data-page="product" data-model="'+model['id']+'"')
    write('winter-'+model['id']+'.html',page)

page=(P/'compose.html').read_text(encoding='utf-8')
page=page.replace('<ol class="steps" aria-label="Etapy kompozycji">','<ol class="steps" data-steps aria-label="Etapy kompozycji">')
page=page.replace('<main id="main" class="compose-page">','<main id="main" class="compose-page"><div data-builder hidden id="kompozycja">')
page=page.replace('class="wrap compose-stage"','class="wrap compose-stage workspace"')
page=page.replace('class="composer-panel"','class="composer-panel edit-position"')
page=page.replace('data-position-state','data-position-state data-edit-status').replace('data-position></p>','data-position data-edit-title></p>')
page=page.replace('<span data-set-size></span>','<span data-set-size></span><span class="rail-progress" data-compose-count aria-live="polite"></span>')
page=page.replace('<fieldset class="finish-field" data-finish-field>','<div data-color-home><fieldset class="finish-field" data-finish-field data-color-field>')
page=page.replace('<div data-colors class="finish-grid"></div></fieldset>','<div data-colors class="finish-grid"></div></fieldset></div>')
page=page.replace('data-summary-progress','data-summary-progress data-summary-note')
start=page.index('<div class="summary-grid">');end=page.index('</section>',start)
summary='''<div class="summary-grid"><div class="summary-collection"><p data-count role="status"></p><div class="progress-line" hidden><span></span></div><ul data-issues class="issues" hidden></ul><ul data-summary hidden></ul><ul data-basket class="r015-packs"></ul><p class="photo-note">Fotografie pokazują formę. Wykończenie podano przy każdej ozdobie.</p><div class="pack-actions"><button data-add-pack class="text-button" type="button">Dodaj kolejną kompozycję</button><button data-reset class="text-button" type="button">Wyczyść wybór</button></div></div><aside class="order-panel" id="delivery-summary" aria-label="Dostawa i kwota"><p class="eyebrow">Ostatni krok</p><h3>Dostawa i kwota</h3>'''+delivery+'''<dl class="totals"><div><dt>Wartość ozdób</dt><dd data-r015-merchandise></dd></div><div><dt>Dostawa</dt><dd data-r015-shipping></dd></div><div class="grand-total"><dt>Razem <small>brutto</small></dt><dd data-r015-total></dd></div></dl><p data-totals class="sr-only" aria-live="polite"></p>'''+coupon+legal+'''<p data-payment-status role="status" aria-live="polite"></p><button data-checkout class="r015-internal-action" type="button" hidden>Przejdź do płatności</button><a data-notify href="/winter-26.html" hidden>Wróć do kolekcji</a><div class="dispatch-small"><span class="eyebrow">Planowane nadania</span><p>Od 1 grudnia 2026 r.</p><small>Samo ułożenie kompozycji nie rezerwuje ozdób.</small></div></aside></div>'''
page=page[:start]+summary+page[end:]
page=page.replace('data-dock-back','data-dock-back data-prev').replace('data-dock-action','data-dock-action data-sticky-action')
page=page.replace('<span data-dock-progress','<span data-sticky-copy hidden></span><span data-dock-progress')
page=page.replace('</main><dialog class="confirm-dialog"', '<div class="r015-internal-action" hidden><button type="button" data-start></button><button type="button" data-review></button><button type="button" data-next></button></div>'+dialogs+'</div></main><dialog class="confirm-dialog"')
page=re.sub(r'<dialog class="confirm-dialog".*?</dialog>','',page,flags=re.S)
page=shell(page,'compose').replace('</body>',options+'</body>')
write('winter-zestaw-4.html',page)

# Preserve every PHP executable block from the old return page; change only HTML wrappers.
result=original('api/result.php');prefix=result.split('?>',1)[0]+'?>'
old_title=re.search(r'<h1>(.*?)</h1>',result,re.S).group(1)
old_copy=re.search(r'<p>(.*?)</p>',result,re.S).group(1)
return_page=(P/'return.html').read_text(encoding='utf-8')
main=f'''<main id="main" class="return-page wrap"><p class="eyebrow">WINTER 26 / Płatność</p><div class="return-panel"><p class="result-kicker">Twoja kompozycja</p><h1>{old_title}</h1><p class="result-copy">{old_copy}</p><a class="button primary" href="/winter-zestaw-4.html?size=6#kompozycja">Powrót do konfiguratora</a><p class="caption">Sam powrót na tę stronę nie potwierdza płatności.</p></div></main>'''
return_page=re.sub(r'<main.*?</main>',lambda _:main,return_page,flags=re.S)
return_page=shell(return_page,'return')
write('api/result.php',prefix+return_page)
assert re.findall(r'<\?php.*?\?>|<\?=.*?\?>',result,re.S)==re.findall(r'<\?php.*?\?>|<\?=.*?\?>',prefix+return_page,re.S)

js=original('winter-config.js')
js=replace(js,"el('label',null,'choice')","el('label',null,'choice '+(name==='size'?'size-choice':name==='model'?'model-choice':'finish-choice'))")
js=replace(js,"const face=el('span',null,'swatch');","const face=el('span',null,'finish-face');")
js=replace(js,"'color-chip color-chip-'+v.colorId","'swatch color-chip color-chip-'+v.colorId+' '+v.colorId")
js=js.replace("'model-tile'","'model-face'")
js=js.replace("return 'Wybierz kolor'","return 'Wybierz wykończenie'")
js=js.replace("'✓ Gotowa'","''").replace("'gotowa'","'wybrane model i wykończenie'")
js=js.replace("'Gotowe bombki: '+done+' z '+size","done+' z '+size+' ozdób skonfigurowanych'")
js=js.replace("'Wszystkie bombki gotowe'","'Model i wykończenie wybrane'")
js=replace(js,"get('[data-steps]').replaceChildren(...['Rozmiar','Komponowanie','Podsumowanie'].map((label,i)=>{const b=el('button',(i+1)+'. '+label);b.type='button';b.setAttribute('aria-current',step===i+1?'step':'false');b.onclick=()=>goStep(i+1);return b}));","get('[data-steps]').replaceChildren(...['Rozmiar','Komponowanie','Podsumowanie'].map((label,i)=>{const b=el('li');b.append(el('span','0'+(i+1)),el('span',label));b.setAttribute('aria-current',step===i+1?'step':'false');return b}));")
js=replace(js,"get('[data-sizes]').replaceChildren(...data.sizes.map(({size:n})=>radio('size',n,el('span',(n===data.featured?'Polecamy · ':'')+n+' szt.'),n===size,()=>{","get('[data-sizes]').replaceChildren(...data.sizes.map(({size:n,grossGrosz})=>{const face=el('span',null,'size-face');if(n===data.featured)face.append(el('em','Wybór pracowni'));face.append(el('b',String(n)),el('span',n===1?'ozdoba':n<5?'ozdoby':'ozdób'),el('small',money(grossGrosz)));return radio('size',n,face,n===size,()=>{")
js=replace(js,"else resize(true);\n      })));","else resize(true);\n      })}));")
js=js.replace("el('small','Nº '+String(i+1).padStart(2,'0'))","el('small',String(i+1).padStart(2,'0'),'slot-number')")
js=js.replace("el('strong',nameOf(slot)||'Wybierz formę'),el('small',model?(v?.label||'Wybierz kolor'):'')","el('strong',nameOf(slot)||'Wybierz model','slot-model'),el('small',model?(v?.label||'Wybierz wykończenie'):'','slot-finish')")
js=replace(js,"if(slot.model===m.id)card.append(colorField);",'')
js=replace(js,"colorField.hidden=!model;if(!model)get('[data-color-home]').append(colorField);","colorField.hidden=!model;get('[data-color-home]').append(colorField);")
js=replace(js,"next.textContent=active===size-1?'Zobacz podsumowanie →':'Następna bombka →';","next.textContent=active===size-1?'Podsumowanie':'Następna ozdoba';")
js=replace(js,"next.onclick=()=>{if(active===size-1)goStep(3);else editSlot(slots,active+1)};","next.onclick=()=>{if(issueFor(slots[active],active,slots)){editSlot(slots,active,true);return;}if(active===size-1)goStep(3);else editSlot(slots,active+1)};")
js=replace(js,"prev.disabled=active===0;prev.onclick=()=>{if(active>0)editSlot(slots,active-1)};","prev.disabled=step===1;prev.textContent=step===3?'Edytuj kompozycję':active===0?'Zmień rozmiar':'Poprzednia ozdoba';prev.onclick=()=>{if(step===3)goStep(2);else if(active>0)editSlot(slots,active-1);else goStep(1)};")
start=js.index("      get('[data-basket]').replaceChildren(")
end=js.index('      const free=count>=data.freeFrom;',start)
basket='''      get('[data-basket]').replaceChildren(...packs.map((p,i)=>{
        const li=el('li',null,'r015-pack'),current=p===slots;
        const heading=el('div',null,'summary-set-price');heading.append(el('span',p.length+' '+(p.length===1?'ozdoba':'ozdób')+' w Twojej kompozycji'),el('strong',money(priceFor(p))));li.append(heading);
        const items=el('ol',null,'summary-items');p.forEach((s,j)=>{
          const item=el('li'),v=variantFor(data,s),m=data.models.find(m=>m.id===s.model),src=v?.photo?.thumb||m?.thumb;
          const top=el('div',null,'summary-card-head'),edit=el('button','Edytuj','text-button');edit.type='button';edit.setAttribute('aria-label','Edytuj bombkę '+(j+1)+(packs.length>1?' w zestawie '+(i+1):''));edit.onclick=()=>editSlot(p,j);
          top.append(el('span','Ozdoba '+String(j+1).padStart(2,'0'),'item-index'),edit);item.append(top);
          const photo=el('div',null,'summary-card-photo');if(src)photo.append(picture(src,m?.name||''));item.append(photo);
          const copy=el('div',null,'summary-card-copy');copy.append(el('h3',m?.name||'Wybierz model'));const reason=issueFor(s,j,p),finish=el('p',null,reason?'item-incomplete':'summary-finish');if(!reason)finish.append(el('i',null,'swatch '+s.color));finish.append(el('span',reason||v.label));copy.append(finish);item.append(copy);items.append(item);
        });li.append(items);
        const remove=el('button','Usuń kompozycję','text-button');remove.type='button';remove.setAttribute('aria-label','Usuń pozycję '+(i+1)+' z koszyka');remove.onclick=()=>{if(current)removeCurrent();else{saved.splice(i,1);acceptance.checked=false;draw()}};
        if(p.some(s=>s.model))li.append(remove);return li;
      }));
'''
js=js[:start]+basket+js[end:]
js=js.replace("'Przejdź do płatności testowej'","'Przejdź do płatności'")
js=replace(js,"sticky.textContent=step===1?'Komponuj →':step===2?'Podsumowanie →':btn.hidden?'Uzupełnij zestaw':btn.textContent;","sticky.textContent=step===1?'Wybierz modele':step===2?next.textContent:btn.hidden?'Uzupełnij zestaw':btn.textContent;")
js=replace(js,"sticky.onclick=()=>{if(step<3)goStep(step+1);else if(commerceOpen())btn.onclick();","sticky.onclick=()=>{if(step===1)goStep(2);else if(step===2)next.onclick();else if(commerceOpen())btn.onclick();")
js=replace(js,"else{const missing=firstMissing();if(missing)editSlot(missing.pack,missing.index)}};","else{const missing=firstMissing();if(missing)editSlot(missing.pack,missing.index);else location.assign('/api/test-access.php')}};")
js=js.replace("btn.hidden?'Uzupełnij zestaw':btn.textContent","btn.hidden?'Dostęp testera':btn.textContent")
js=js.replace('Możesz ułożyć kompozycję. Zapisz się, aby otrzymać informację o rozpoczęciu sprzedaży.','Możesz ułożyć kompozycję. Aby wykonać zakup Sandbox, zaloguj się jako tester.')
js=replace(js,"get('[data-sticky-copy]').textContent=summary(data,all,!commerceOpen()).done+'/'+count+' gotowych · '+money(total??merchandise);","get('[data-sticky-copy]').textContent=summary(data,all,!commerceOpen()).done+' z '+count+' ozdób skonfigurowanych · '+money(total??merchandise);\n      document.body?.setAttribute('data-step',String(step));\n      document.dispatchEvent?.(new CustomEvent('pf:composition',{detail:{step,size,active,model:slot.model,color:slot.color,done:summary(data,all,!commerceOpen()).done,count,total,merchandise,shipping,commerceMode,busy}}));")
write('winter-config.js',js)
print('R01.5 presentation generated; checkout handler and availability contracts preserved.')
