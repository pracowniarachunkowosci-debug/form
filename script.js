'use strict';
document.documentElement.classList.add('js');
document.body.classList.add('is-ready');
// Review build: no analytics, external submissions, cookies or browser storage.
const menuBtn = document.getElementById('menuBtn');
const nav = document.getElementById('siteNav');
const closeMenu = (returnFocus = false) => {
  const wasOpen = nav?.classList.contains('open');
  nav?.classList.remove('open');
  menuBtn?.setAttribute('aria-expanded', 'false');
  menuBtn?.setAttribute('aria-label', 'Otwórz menu');
  if (returnFocus && wasOpen) menuBtn?.focus();
};
menuBtn?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menuBtn.setAttribute('aria-expanded', String(open));
  menuBtn.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
});
nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(true); });
document.addEventListener('click', event => { if (!event.target.closest('.site-header')) closeMenu(); });
document.querySelector('.site-header')?.addEventListener('focusout', event => {
  if (!event.currentTarget.contains(event.relatedTarget)) closeMenu();
});
window.matchMedia('(min-width: 901px)').addEventListener('change', () => closeMenu());
document.querySelectorAll('[data-finish-tabs]').forEach(tabs => {
  const buttons = [...tabs.querySelectorAll('[data-finish]')];
  const activate = button => {
    buttons.forEach(item => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
      item.tabIndex = active ? 0 : -1;
    });
    tabs.querySelectorAll('[data-finish-panel]').forEach(panel => {
      const active = panel.dataset.finishPanel === button.dataset.finish;
      panel.classList.toggle('active', active);
      panel.hidden = !active;
    });
  };
  buttons.forEach((button, index) => {
    button.addEventListener('click', () => activate(button));
    button.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % buttons.length;
      if (event.key === 'ArrowLeft') next = (index - 1 + buttons.length) % buttons.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = buttons.length - 1;
      if (next !== undefined) { event.preventDefault(); activate(buttons[next]); buttons[next].focus(); }
    });
  });
  if (buttons.length) activate(buttons.find(button => button.classList.contains('active')) || buttons[0]);
});
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
const demo = document.querySelector('[data-withdrawal-demo]');
if (demo) {
  demo.hidden = false;
  const start = demo.querySelector('[data-withdrawal-start]');
  const fields = ['name', 'order', 'email'].map(key => document.getElementById(`withdrawal-${key}`));
  const error = demo.querySelector('[data-withdrawal-error]');
  const summary = demo.querySelector('[data-withdrawal-summary]');
  const show = step => {
    start.hidden = !!step;
    demo.querySelectorAll('[data-withdrawal-step]').forEach(panel => { panel.hidden = panel.dataset.withdrawalStep !== step; });
    if (step) demo.querySelector(`[data-withdrawal-step="${step}"] h3`).focus();
    else start.focus();
  };
  start.addEventListener('click', () => show('details'));
  demo.querySelector('[data-withdrawal-review]').addEventListener('click', () => {
    error.textContent = '';
    fields.forEach(field => field.removeAttribute('aria-invalid'));
    const invalid = fields.find(field => !field.value.trim() || !field.checkValidity());
    if (invalid) {
      error.textContent = 'Uzupełnij dane testowe, opis umowy i poprawny adres e-mail.';
      invalid.setAttribute('aria-invalid', 'true');
      invalid.setAttribute('aria-describedby', 'withdrawal-error');
      error.id = 'withdrawal-error';
      invalid.focus();
      return;
    }
    summary.replaceChildren();
    ['Imię i nazwisko', 'Umowa', 'E-mail'].forEach((label, index) => {
      const dt = document.createElement('dt'); const dd = document.createElement('dd');
      dt.textContent = label; dd.textContent = fields[index].value.trim(); summary.append(dt, dd);
    });
    show('confirm');
  });
  demo.querySelector('[data-withdrawal-back]').addEventListener('click', () => show('details'));
  demo.querySelector('[data-withdrawal-confirm]').addEventListener('click', () => show('done'));
  demo.querySelector('[data-withdrawal-reset]').addEventListener('click', () => {
    fields.forEach(field => { field.value = ''; field.removeAttribute('aria-invalid'); field.removeAttribute('aria-describedby'); });
    summary.replaceChildren(); error.textContent = ''; show(null);
  });
}
