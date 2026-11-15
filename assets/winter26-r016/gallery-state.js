// A selected finish never falls back to a different finish or model.
const excluded=new Set(['REJECTED_QUALITY','ARCHIVED_BY_OWNER']);
export function eligible(item,{allowProposals=false}={}){
  return item.galleryIncluded===true&&item.activeVariant!==false&&!item.reviewOnly&&!excluded.has(item.ownerStatus)
    &&(item.colorConfirmed===true||(allowProposals&&item.ownerStatus==='PROPOSAL'));
}
export function selectGallery(media,modelId,colorId=null,options={}){
  const model=media.filter(m=>m.modelId===modelId&&eligible(m,options));
  if(!colorId)return {exact:false,scope:'inspiration',product:[],lifestyle:model.filter(m=>m.role==='lifestyle')};
  const selected=model.filter(m=>m.colorId===colorId);
  return {exact:selected.length>0,scope:selected.length?'variant':'missing',
    product:selected.filter(m=>m.role!=='lifestyle'),lifestyle:selected.filter(m=>m.role==='lifestyle')};
}
export function selectCardPhoto(media,modelId,colorId,options={}){
  // Never promote gallery/detail/lifestyle frames to the main role.
  return media.filter(m=>m.modelId===modelId&&m.colorId===colorId&&m.role==='main'&&eligible(m,options))
    .sort((a,b)=>Number(b.ownerStatus==='OWNER APPROVED')-Number(a.ownerStatus==='OWNER APPROVED')||Number(b.colorConfirmed)-Number(a.colorConfirmed))[0]||null;
}
export const nextFrame=(index,delta,length)=>length?(index+delta+length)%length:0;
export const protectedPreview=()=>['pf26.uber.space','127.0.0.1','localhost'].includes(location.hostname);
