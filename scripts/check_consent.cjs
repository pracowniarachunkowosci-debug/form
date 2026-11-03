// Executes the real consent controller in a network-free DOM stub.
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm'), assert = require('node:assert/strict');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'winter-26.html'), 'utf8');
const initializer = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].find(m => m[1].includes('PF_GA_MEASUREMENT_ID'))[1];
const source = fs.readFileSync(path.join(root, 'script.js'), 'utf8');
const code = source.slice(source.indexOf('// Cookie consent + GA4'), source.indexOf('// Interaktywne badanie'));
const key = 'pf_cookie_consent', disable = 'ga-disable-G-58YFJ2RHNZ';
function run(saved, {blocked = false, analytics = true} = {}) {
  const injected = [], storage = new Map(saved ? [[key, saved]] : []), events = {}, deletions = [];
  const jar = new Map([['_ga','old'],['_ga_58YFJ2RHNZ','old'],['_gid','old'],['sib_cuid','keep'],['other','keep']]);
  const el = () => ({hidden:true, textContent:'', attrs:{}, handlers:{}, focused:false,
    addEventListener(name,fn){this.handlers[name]=fn}, setAttribute(k,v){this.attrs[k]=v}, focus(){this.focused=true}});
  const banner=el(), status=el(), accept=el(), reject=el(), close=el(), settings=el();
  const selectors = {'[data-cookie-banner]':banner,'[data-cookie-status]':status,'[data-cookie-accept]':accept,'[data-cookie-reject]':reject,'[data-cookie-close]':close};
  const document = {querySelector(s){return selectors[s]},querySelectorAll(){return [settings]},
    createElement(){return {}},head:{appendChild(s){injected.push(s)}}};
  Object.defineProperty(document,'cookie',{get(){return [...jar].map(([k,v])=>`${k}=${v}`).join('; ')},set(v){deletions.push(v);jar.delete(v.split('=')[0])}});
  const context={document,Date,location:{hostname:'www.pracowniaform.com',pathname:'/winter-26.html'},
    addEventListener(k,fn){events[k]=fn},
    localStorage:{getItem(k){if(blocked)throw Error('blocked');return storage.get(k)||null},setItem(k,v){if(blocked)throw Error('blocked');storage.set(k,v)}}};
  context.window=context; vm.createContext(context);
  if(analytics) vm.runInContext(initializer,context);
  vm.runInContext(code,context);
  return {context,injected,storage,events,jar,deletions,banner,status,accept,reject,close,settings};
}
let s=run(); assert.equal(s.banner.hidden,false); assert.equal(s.injected.length,0); assert.equal(s.context[disable],true);
s.close.handlers.click(); assert.equal(s.banner.hidden,true); assert.equal(s.storage.size,0);
s.settings.handlers.click(); assert.equal(s.banner.hidden,false); assert(s.reject.focused);
s.banner.handlers.keydown({key:'Escape',preventDefault(){}}); assert(s.banner.hidden); assert(s.settings.focused); assert.equal(s.storage.size,0);
s=run(); s.reject.handlers.click(); assert.equal(s.storage.get(key),'rejected'); assert.equal(s.injected.length,0);
s=run('rejected'); assert(s.banner.hidden); assert.equal(s.injected.length,0);
s.settings.handlers.click(); s.accept.handlers.click(); s.accept.handlers.click(); assert.equal(s.injected.length,1); assert.equal(s.context[disable],false);
assert.equal(s.injected[0].src,'https://www.googletagmanager.com/gtag/js?id=G-58YFJ2RHNZ');
assert.equal(s.context.dataLayer.filter(a=>a[0]==='config').length,1);
s=run('accepted'); assert.equal(s.injected.length,1);
s.settings.handlers.click(); s.reject.handlers.click(); assert.equal(s.context[disable],true); assert.equal(s.storage.get(key),'rejected');
assert.equal(s.context.dataLayer.at(-1)[2].analytics_storage,'denied');
assert(!s.jar.has('_ga')); assert(!s.jar.has('_ga_58YFJ2RHNZ')); assert(s.jar.has('sib_cuid')); assert(s.jar.has('other'));
assert(s.deletions.some(v=>v.includes('domain=.pracowniaform.com')));
let refreshed=run(s.storage.get(key)); assert.equal(refreshed.injected.length,0); assert.equal(refreshed.context[disable],true);
s.settings.handlers.click(); s.accept.handlers.click(); assert.equal(s.context[disable],false); assert.equal(s.injected.length,1);
s.storage.set(key,'rejected'); s.events.storage({key}); assert.equal(s.context[disable],true);
s=run('accepted'); s.storage.clear(); s.events.storage({key:null}); assert.equal(s.context[disable],true);
s=run(undefined,{blocked:true}); s.accept.handlers.click(); assert.equal(s.injected.length,0); assert.equal(s.context[disable],true); assert(!s.banner.hidden); assert(s.status.textContent.includes('Nie udało'));
s=run('accepted',{analytics:false}); assert.equal(s.injected.length,0); s.settings.handlers.click(); s.reject.handlers.click(); assert.equal(s.storage.get(key),'rejected'); assert.equal(s.context[disable],true);
console.log('PASS: absent/accept/reject/withdraw/reload/reaccept, cross-tab revocation, Escape/focus, GA-only cookie cleanup, storage failure, privacy/contact pages; no network.');
