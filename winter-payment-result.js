/* Return navigation is not evidence of payment. Only the server's stored status is. */
(()=>{
  const panel=document.querySelector('[data-order-result]');if(!panel)return;
  const heading=panel.querySelector('h1'),copy=panel.querySelector('[data-order-message]');
  const button=panel.querySelector('[data-order-refresh]');let busy=false;
  async function refresh(){
    if(busy)return;busy=true;button.disabled=true;
    try{
      const attempt=JSON.parse(sessionStorage.getItem('pf-w26-checkout-attempt-v1')||'null');
      if(!attempt?.id){heading.textContent='Nie można ustalić statusu zamówienia';copy.textContent='Brakuje zapisanej próby w tej karcie. Skontaktuj się ze sklepem; nie płać ponownie.';return;}
      const res=await fetch('/api/order-status.php',{method:'POST',credentials:'same-origin',cache:'no-store',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({requestId:attempt.id})});
      const json=await res.json();
      const titles={paid:'Zamówienie opłacone',pending:'Płatność jest przetwarzana',released:'Próba zakończona bez płatności',review:'Płatność wymaga sprawdzenia',reserved:'Płatność nie jest potwierdzona',reconcile:'Sprawdzamy wynik płatności'};
      if(!res.ok||!titles[json.state]||typeof json.message!=='string')throw new Error('status unavailable');
      heading.textContent=titles[json.state];copy.textContent=json.message;
      // Keep the original request, including for released. The configurator verifies it itself.
      attempt.blocked=json.state==='paid'?'ORDER_PAID':json.state==='review'?'PAYMENT_REVIEW':null;
      attempt.message=json.message;try{sessionStorage.setItem('pf-w26-checkout-attempt-v1',JSON.stringify(attempt));}catch{}
    }catch{heading.textContent='Nie potwierdzono statusu płatności';copy.textContent='Spróbuj ponownie sprawdzić status. Nie rozpoczynaj kolejnej płatności.';}
    finally{busy=false;button.disabled=false;}
  }
  button.onclick=refresh;window.addEventListener('pageshow',refresh);refresh();
})();
