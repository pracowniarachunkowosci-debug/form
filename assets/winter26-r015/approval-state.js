const approved={"id": "full-soft-czerwono-czarny-main", "modelId": "full-soft", "colorId": "dual", "role": "main", "sourceSha256": "12cfc47cc2d188b6a19142bc114422a680a6c681e0d66a5005d214e6c656e859"};
export const ownerApprovalFor = item => Object.entries(approved).every(([k,v])=>item[k]===v)?approved:null;
