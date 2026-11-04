'use strict';
for (const gallery of document.querySelectorAll('.store-gallery')) {
  const frames = [...gallery.querySelectorAll('[data-frame]')];
  const thumbs = [...gallery.querySelectorAll('[data-slide]')];
  const dialog = document.querySelector('.zoom-dialog');
  let opener;
  function select(index) {
    frames.forEach((f, i) => { f.hidden = i !== index; });
    thumbs.forEach((b, i) => b.setAttribute('aria-pressed', String(i === index)));
    gallery.querySelector('[data-gallery-status]').textContent = frames[index].querySelector('figcaption').innerText;
  }
  thumbs.forEach((button, i) => {
    button.addEventListener('click', () => select(i));
    button.addEventListener('keydown', e => {
      const move = {ArrowLeft:-1, ArrowRight:1}[e.key];
      if (!move) return;
      e.preventDefault();
      const next=(i+move+frames.length)%frames.length;
      select(next);thumbs[next].focus();
    });
  });
  select(0);gallery.querySelector('.thumbs').hidden = false;
  if (!dialog || !dialog.showModal) continue;
  gallery.addEventListener('click', event => {
    const link = event.target.closest('[data-zoom]');
    if (!link) return;
    event.preventDefault();
    opener = link;
    const image = dialog.querySelector('img');
    image.src = link.href; image.alt = link.querySelector('img').alt;
    dialog.querySelector('p').textContent = link.nextElementSibling.innerText;
    dialog.showModal();
  });
  dialog.addEventListener('close', () => opener?.focus());
  dialog.addEventListener('click', e => { if(e.target === dialog) dialog.close(); });
}
