// Runs the unchanged production script in a network-free DOM stub.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'winter-26.html'), 'utf8');
const initializer = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].find(m=>m[1].includes('PF_GA_MEASUREMENT_ID'))[1];
const code = fs.readFileSync(path.join(root, 'script.js'), 'utf8');
function run(saved) {
  const handlers = {}, injected = [], storage = new Map(saved ? [['pf_cookie_consent', saved]] : []);
  const classes = {add(){},remove(){},contains(){return false},toggle(){return false}};
  const banner = {hidden:true};
  const selectors = {'[data-cookie-banner]':banner};
  for (const name of ['accept','reject']) selectors[`[data-cookie-${name}]`] = {addEventListener(event,fn){handlers[name]=fn}};
  const context = {Date, IntersectionObserver:class {observe(){} unobserve(){}},
    document:{documentElement:{classList:classes},body:{classList:classes},
      getElementById(){return null},querySelector(s){return selectors[s] || null},querySelectorAll(){return []},
      addEventListener(){},createElement(){return {}},head:{appendChild(s){injected.push(s)}}},
    setTimeout(){},addEventListener(){},scrollY:0,
    localStorage:{getItem(k){return storage.get(k)||null},setItem(k,v){storage.set(k,v)}}};
  context.window=context;
  vm.createContext(context); vm.runInContext(initializer,context); vm.runInContext(code,context);
  assert.equal(context.dataLayer[0][2].analytics_storage,'denied');
  return {context,banner,handlers,injected,storage};
}
let s = run(); assert.equal(s.banner.hidden,false); assert.equal(s.injected.length,0);
s.handlers.reject(); assert.equal(s.banner.hidden,true); assert.equal(s.storage.get('pf_cookie_consent'),'rejected'); assert.equal(s.injected.length,0);
s = run('rejected'); assert.equal(s.banner.hidden,true); assert.equal(s.injected.length,0);
s = run(); s.handlers.accept(); s.handlers.accept();
assert.equal(s.storage.get('pf_cookie_consent'),'accepted'); assert.equal(s.banner.hidden,true); assert.equal(s.injected.length,1);
assert.equal(s.injected[0].src,'https://www.googletagmanager.com/gtag/js?id=G-58YFJ2RHNZ');
assert(s.context.dataLayer.some(args=>args[0]==='config' && args[1]==='G-58YFJ2RHNZ'));
s = run('accepted'); assert.equal(s.banner.hidden,true); assert.equal(s.injected.length,1);
console.log('PASS: default denied, reject, stored reject, accept, duplicate accept and stored accept; zero network requests.');
