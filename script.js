document.documentElement.classList.add('js');

const pageStartedAt = Date.now();
const minimumPreloaderTime = 950;

const menuBtn = document.getElementById('menuBtn');
const nav = document.getElementById('siteNav');
const header = document.querySelector('.site-header');

const showPage = () => {
  if (document.body.classList.contains('is-ready')) {
    return;
  }

  const elapsed = Date.now() - pageStartedAt;
  const delay = Math.max(0, minimumPreloaderTime - elapsed);

  window.setTimeout(() => {
    document.body.classList.add('is-ready');
  }, delay);
};

window.addEventListener('load', showPage);
window.setTimeout(showPage, 3600);

const closeMenu = () => {
  nav?.classList.remove('open');
  document.body.classList.remove('menu-open');
  menuBtn?.setAttribute('aria-expanded', 'false');
  menuBtn?.setAttribute('aria-label', 'Otwórz menu');
};

menuBtn?.addEventListener('click', () => {
  const isOpen = nav.classList.toggle('open');
  document.body.classList.toggle('menu-open', isOpen);
  menuBtn.setAttribute('aria-expanded', String(isOpen));
  menuBtn.setAttribute('aria-label', isOpen ? 'Zamknij menu' : 'Otwórz menu');
});

nav?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', closeMenu);
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeMenu();
  }
});

const updateHeader = () => {
  header?.classList.toggle('scrolled', window.scrollY > 40);
};

updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.12,
  rootMargin: '0px 0px -40px 0px'
});

document.querySelectorAll('.reveal').forEach((element) => {
  observer.observe(element);
});

document.querySelector('.signup-form')?.addEventListener('submit', async (event) => {
  event.preventDefault();

  const form = event.currentTarget;
  const emailInput = form.querySelector('input[type="email"]');
  const consentInput = form.querySelector('input[name="consent"]');
  const button = form.querySelector('button[type="submit"]');

  const email = emailInput?.value.trim();

  form.querySelector('.form-error')?.remove();

  if (!email) {
    emailInput?.focus();
    return;
  }

  if (consentInput && !consentInput.checked) {
    const error = document.createElement('p');
    error.className = 'form-error';
    error.textContent = 'Zaznacz zgodę, aby dołączyć do listy premierowej.';
    form.appendChild(error);
    consentInput.focus();
    return;
  }

  form.classList.add('is-sending');
  button?.setAttribute('disabled', 'true');
  button?.setAttribute('aria-busy', 'true');

  /*
    TODO BREVO:
    W tym miejscu później podłączymy formularz do Brevo.
    Na razie formularz działa jako front-endowy prototyp listy premierowej.
  */

  window.setTimeout(() => {
    form.classList.remove('is-sending');
    form.classList.add('sent');

    form.innerHTML = `
      <p class="form-success">
        Dziękujemy. Jesteś na liście premierowej Pracowni Form.
        Otrzymasz wcześniejszy dostęp do informacji o premierze, kolekcjach i pre-orderze.
      </p>
    `;
  }, 550);
});
document.querySelectorAll('[data-finish-tabs]').forEach((tabs) => {
  const buttons = tabs.querySelectorAll('[data-finish]');
  const panels = tabs.querySelectorAll('[data-finish-panel]');

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const target = button.dataset.finish;

      buttons.forEach((item) => {
        const isActive = item === button;
        item.classList.toggle('active', isActive);
        item.setAttribute('aria-selected', String(isActive));
      });

      panels.forEach((panel) => {
        const isActive = panel.dataset.finishPanel === target;
        panel.classList.toggle('active', isActive);
        panel.hidden = !isActive;
      });
    });
  });
});