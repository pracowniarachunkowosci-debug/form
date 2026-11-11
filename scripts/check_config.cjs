// Isolated inventory snapshot: never copied to the storefront.
const {strict:assert}=require('node:assert');
const {summary,eligible,variantFor}=require('../winter-config.js');
const make=(colorId,sku,stock)=>({colorId,sku,stock,label:colorId,available:true});
const a=make('fixture-a','fixture-sku-1',2),b=make('fixture-b','fixture-sku-2',6);
const data={models:[{id:'test',name:'Test',variants:[a,b]}]};
const slot=(v)=>({model:'test',color:v.colorId});
for(const n of [4,6,8]){
 const slots=Array.from({length:n},(_,i)=>slot(i<2?a:b));
 assert.equal(summary(data,slots).done,n);
 assert.equal(summary(data,slots).groups[0].count,2);
 assert(!eligible(a,slots,n-1,data)); // other two units are already allocated
 assert(eligible(a,slots,0,data)); // editing own unit does not consume another
 slots[0].color=null;
 assert(eligible(a,slots,n-1,data)); assert.equal(summary(data,slots).done,n-1);
 slots[0].color='unknown'; assert(!variantFor(data,slots[0]));
 slots[0].model='unknown'; assert.equal(summary(data,slots).done,n-1);
}
for(const v of [{...a,stock:0},{...a,stock:null},{...a,sku:null},{...a,available:false}])
 assert(!eligible(v,[],0,data));
const over=[slot(a),slot(a),slot(a),slot(b)];
assert.notEqual(summary(data,over).done,4);
assert.equal(summary(data,[slot(a)]).done,1);
assert.equal(summary(data,[slot(a),slot(a)]).done,2);
const previewOnly={models:[{id:'test',name:'Test',variants:[{...a,stock:null,available:false}]}]};
assert.equal(summary(previewOnly,[slot(a)],true).done,1);
assert.equal(summary(previewOnly,[slot(a)],false).done,0);
console.log('PASS: 4/6/8 complete, repeated SKUs aggregate; unknown, excess and unavailable cannot complete a set.');
