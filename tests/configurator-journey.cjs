// Exercise the actual UI controller, with isolated inventory and deferred checkout.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const options=fs.readFileSync('winter-zestaw-4.html','utf8').match(/id="winter-options">([^<]+)<\/script>/)[1];
const script=fs.readFileSync('winter-config.js','utf8');
class Element {
 constructor(tag){Object.assign(this,{tag,children:[],style:{},hidden:false,disabled:false,checked:false,value:''})}
 append(...items){this.children.push(...items)} replaceChildren(...items){this.children=items}
 setAttribute(k,v){this[k]=v} focus(){this.focused=true} scrollIntoView(){this.scrolled=true}
 showModal(){this.open=true} close(){this.open=false;this.onclose?.()} addEventListener(){} remove(){}
 querySelectorAll(tag){return this.children.flatMap(c=>[...(c.tag===tag?[c]:[]),...c.querySelectorAll(tag)])}
}
async function journey(size){
 const nodes={},root=new Element('main'),get=s=>nodes[s]||=new Element('div');root.querySelector=get;
 let requests=[],finish;
 const data=JSON.parse(options),stock={};for(const m of data.models)for(const v of m.variants)stock[m.id+':'+v.colorId]=20;
 stock['full-soft:red-matte']=0;
 const context={document:{querySelector:s=>s==='#winter-options'?{textContent:options}:root,querySelectorAll:()=>[],createElement:t=>new Element(t),head:new Element('head')},
 Intl,URL,URLSearchParams,setTimeout,clearTimeout,crypto:{randomUUID:()=> 'test-request'},location:{search:'?size='+size,protocol:'https:',hostname:'example.test',origin:'https://example.test',href:'https://example.test/',assign(){}},
 fetch:async(url,opts)=>url==='api/status.php'?{ok:true,headers:{get:()=> 'application/json'},json:async()=>({mode:'test',available:true,currency:'PLN',freeCourierFromOrnaments:6,smallOrderCourierGrosz:2049,stock})}:new Promise(resolve=>{requests.push(JSON.parse(opts.body));finish=()=>resolve({ok:false,json:async()=>({message:'Fixture failure'})})})};
 vm.runInNewContext(script,context);await new Promise(r=>setImmediate(r));
 const pick=(area,id)=>{const node=get(area).querySelectorAll('input').find(n=>String(n.value)===String(id));assert(node&&!node.disabled);node.onchange()};
 const btn=get('[data-checkout]');assert(!btn.disabled);assert.equal(btn['data-ready'],'false');
 get('[data-review]').onclick();await btn.onclick();assert.equal(get('[data-stage="2"]').hidden,false);assert.equal(requests.length,0);
 assert.equal(get('[data-issues]').children.length,size);
 for(let i=0;i<size;i++){get('[data-slots]').children[i].onclick();pick('[data-models]','full-soft');if(i!==0)pick('[data-colors]','marble')}
 assert.equal(get('[data-issues]').children.length,1);assert.match(get('[data-issues]').children[0].children[0].textContent,/Bombka 1/);
 get('[data-review]').onclick();get('[data-sticky-action]').onclick();assert.match(get('[data-edit-title]').textContent,/01/);assert.equal(requests.length,0);
 assert(get('[data-colors]').querySelectorAll('input').find(n=>n.value==='red-matte').disabled);
 pick('[data-colors]','marble');assert.equal(btn['data-ready'],'true');assert.equal(get('[data-issues]').children.length,0);
 assert.match(get('[data-compose-count]').textContent,new RegExp(size+' z '+size));
 // Changing model must require a new color; use the exact item edit action.
 get('[data-basket]').children[0].querySelectorAll('button')[0].onclick();pick('[data-models]','knitted-star');assert.equal(btn['data-ready'],'false');
 await btn.onclick();assert.equal(requests.length,0);pick('[data-colors]','white');
 const first=btn.onclick();const second=btn.onclick();assert.equal(requests.length,1);assert.equal(requests[0].selections.length,size);assert(btn.disabled);
 finish();await Promise.all([first,second]);assert.equal(btn.disabled,false);
 assert.match(get('[data-payment-status]').textContent,/Fixture failure/);
}
Promise.all([1,2,4,6,8].map(journey)).then(()=>console.log('PASS: 1/2/4/6/8, missing model/color, exact missing-item navigation, editing, model resets color, repeated variants, unavailable color, immediate progress and one in-flight checkout request.')).catch(e=>{console.error(e);process.exitCode=1});
