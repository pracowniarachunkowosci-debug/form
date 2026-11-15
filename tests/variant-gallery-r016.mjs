import assert from 'node:assert/strict';
import {variantMedia as media} from '../assets/winter26-r016/variant-media.js';
import {selectGallery,selectCardPhoto,nextFrame} from '../assets/winter26-r016/gallery-state.js';
import {ownerApprovalFor} from '../assets/winter26-r015/approval-state.js';
const models=['full-soft','knitted-star','knitted-medallion'],colors=['dual','red-matte','white','marble'];
for(const model of models)for(const color of colors){
  for(const allowProposals of [false,true]){
    const found=selectGallery(media,model,color,{allowProposals});
    for(const frame of [...found.product,...found.lifestyle]){
      assert.equal(frame.modelId,model);assert.equal(frame.colorId,color);
      assert(!frame.reviewOnly);assert(frame.colorConfirmed||allowProposals&&frame.ownerStatus==='PROPOSAL');
    }
    assert(found.lifestyle.every(m=>m.role==='lifestyle'));
    assert(found.product.every(m=>m.role!=='lifestyle'));
    const card=selectCardPhoto(media,model,color,{allowProposals});
    if(card){assert.equal(card.modelId,model);assert.equal(card.colorId,color);assert.equal(card.role,'main')}
  }
}
assert.equal(media.length,43);
assert.deepEqual(media.filter(m=>ownerApprovalFor(m)).map(m=>m.id),['full-soft-czerwono-czarny-main']);
assert(!media.some(m=>['WEB018','WEB016'].includes(m.id)||m.colorId==='cappuccino'));
assert.equal(selectCardPhoto(media,'full-soft','white',{allowProposals:true}),null,'White gallery frame must not be promoted to main; uncertain-geometry candidate is review-only');
assert.equal(selectCardPhoto(media,'knitted-star','white',{allowProposals:true}),null,'Existing gallery role remains gallery');
assert.equal(selectGallery(media,'knitted-star','marble',{allowProposals:true}).lifestyle.length,0,'White arrangements never substitute for Marble');
assert.equal(selectGallery(media,'full-soft','red-matte').product.length,0,'Production-safe default excludes proposals');
assert.equal(selectGallery(media,'full-soft','red-matte',{allowProposals:true}).product.length,3,'Protected preview exposes existing candidates');
for(const [model,color] of [['knitted-star','dual'],['knitted-medallion','dual'],['knitted-medallion','red-matte']]){
 const found=selectGallery(media,model,color,{allowProposals:true});assert.equal(found.product.length+found.lifestyle.length,0);
}
const poisoned={...media[0],ownerStatus:'REJECTED_QUALITY',colorConfirmed:true};
assert.equal(selectGallery([poisoned],'full-soft','dual',{allowProposals:true}).product.length,0);
assert.equal(ownerApprovalFor({...media[0],sourceSha256:'different'}),null);
assert.equal(nextFrame(0,-1,3),2);
console.log('R01.6: 12 combinations, strict/proposal modes, no cross-color fallback, no role promotion, exclusions and exact approval PASS');
