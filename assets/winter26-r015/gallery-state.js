// R01.4 only: explicitly authorized visual proposals, never the sales catalog.
export function selectGallery(media,modelId,colorId=null){
  const model=media.filter(m=>m.modelId===modelId&&m.galleryIncluded===true&&m.activeVariant!==false);
  // Existing arrangements illustrate the model, not the selected finish.
  const lifestyle=model.filter(m=>m.role==='lifestyle');
  if(!colorId)return {exact:false,scope:'model',product:[],lifestyle};
  const selected=model.filter(m=>m.colorId===colorId);
  return {exact:selected.length>0,scope:selected.length?'proposal':'missing',
    product:selected.filter(m=>m.role!=='lifestyle'&&m.colorConfirmed),lifestyle};
}
export function nextFrame(index,delta,length){return length?(index+delta+length)%length:0}
