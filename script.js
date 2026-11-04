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
// Cookie consent + GA4. Basic mode: no Google script before explicit consent.
(() => {
  const banner = document.querySelector('[data-cookie-banner]');
  const acceptButton = document.querySelector('[data-cookie-accept]');
  const rejectButton = document.querySelector('[data-cookie-reject]');
  const closeButton = document.querySelector('[data-cookie-close]');
  const status = document.querySelector('[data-cookie-status]');
  const settingsButtons = document.querySelectorAll('[data-cookie-settings]');
  if (!banner || !acceptButton || !rejectButton || !closeButton || !status) return;
  const storageKey = 'pf_cookie_consent';
  // Privacy/contact pages manage the same choice without adding analytics there.
  const measurementId = window.PF_GA_MEASUREMENT_ID || 'G-58YFJ2RHNZ';
  const canMeasure = Boolean(window.PF_GA_MEASUREMENT_ID) && typeof gtag === 'function';
  let returnFocus = null;
  let analyticsScript = null;
  const readChoice = () => {
    try { return window.localStorage.getItem(storageKey); } catch { return null; }
  };
  let choice = readChoice();
  const updateStatus = () => {
    status.textContent = choice === 'accepted' ? 'Analityka: zgoda udzielona.' :
      choice === 'rejected' ? 'Analityka: wyłączona.' : 'Analityka: wyłączona — nie udzielono zgody.';
  };
  const consent = (value) => {
    if (typeof gtag !== 'function') return;
    gtag('consent', 'update', {
      analytics_storage: value, ad_storage: 'denied', ad_user_data: 'denied',
      ad_personalization: 'denied', functionality_storage: 'granted', security_storage: 'granted'
    });
  };
  const clearAnalyticsCookies = () => {
    const host = window.location.hostname;
    const parts = host.split('.');
    const domains = ['', host];
    for (let i = 0; i < parts.length - 1; i++) domains.push('.' + parts.slice(i).join('.'));
    const paths = ['/'];
    const segments = window.location.pathname.split('/').filter(Boolean);
    for (let i = 1; i < segments.length; i++) paths.push('/' + segments.slice(0, i).join('/'), '/' + segments.slice(0, i).join('/') + '/');
    document.cookie.split(';').map(item => item.trim().split('=')[0])
      .filter(name => /^(_ga(?:_|$)|_gid$|_gat(?:_|$))/.test(name))
      .forEach(name => domains.forEach(domain => paths.forEach(path => {
        document.cookie = `${name}=; Max-Age=0; path=${path}${domain ? '; domain=' + domain : ''}; SameSite=Lax`;
      })));
  };
  const denyAnalytics = () => {
    // Disable first: removing the script alone does not unload its in-memory code.
    window['ga-disable-' + measurementId] = true;
    consent('denied');
    clearAnalyticsCookies();
  };
  const loadAnalytics = () => {
    if (!canMeasure) return;
    window['ga-disable-' + measurementId] = false;
    consent('granted');
    if (window.PF_GA_LOADED) return;
    window.PF_GA_LOADED = true;
    analyticsScript = document.createElement('script');
    analyticsScript.async = true;
    analyticsScript.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(analyticsScript);
    gtag('js', new Date());
    gtag('config', measurementId, { allow_google_signals: false, allow_ad_personalization_signals: false });
  };
  const setExpanded = (open) => settingsButtons.forEach(button => button.setAttribute('aria-expanded', String(open)));
  const close = () => {
    banner.hidden = true;
    setExpanded(false);
    returnFocus?.focus();
    returnFocus = null;
  };
  settingsButtons.forEach(button => button.addEventListener('click', () => {
    returnFocus = button;
    updateStatus();
    banner.hidden = false;
    setExpanded(true);
    rejectButton.focus();
  }));
  closeButton.addEventListener('click', close);
  banner.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); close(); }
  });
  const choose = (next) => {
    let saved = false;
    try {
      window.localStorage.setItem(storageKey, next);
      saved = readChoice() === next;
    } catch { /* Fail closed: accepting requires a persistent, readable choice. */ }
    choice = next;
    if (next === 'rejected' || !saved) denyAnalytics();
    else loadAnalytics();
    updateStatus();
    if (!saved) {
      status.textContent = 'Analityka jest wyłączona w tej karcie. Nie udało się zapisać wyboru. Usuń zapisane dane tej witryny w przeglądarce, aby usunąć również wcześniejszą zgodę.';
      banner.hidden = false;
      return;
    }
    close();
  };
  acceptButton.addEventListener('click', () => choose('accepted'));
  rejectButton.addEventListener('click', () => choose('rejected'));
  // Revocation in another tab must also stop an already running tag here.
  window.addEventListener('storage', event => {
    if (event.key !== storageKey && event.key !== null) return;
    choice = readChoice();
    if (choice !== 'accepted') denyAnalytics();
    updateStatus();
  });
  updateStatus();
  if (choice === 'accepted') loadAnalytics();
  else {
    denyAnalytics();
    banner.hidden = choice === 'rejected';
    setExpanded(!banner.hidden);
  }
})();
// Interaktywne badanie zainteresowania przed premierą

document.querySelectorAll('[data-interest-picker]').forEach((picker) => {
  const buttons = picker.querySelectorAll('[data-interest]');
  const input = document.getElementById('INTERESUJE');
  const note = picker.querySelector('[data-interest-note]');

  if (!input || !buttons.length) {
    return;
  }

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const value = button.dataset.interest || '';

      input.value = value;

      buttons.forEach((item) => {
        const isActive = item === button;

        item.classList.toggle('active', isActive);
        item.setAttribute('aria-pressed', String(isActive));
      });

      if (note) {
        note.textContent = `Wybrano: ${value}. Dziękujemy — pomoże nam to lepiej przygotować premierę.`;
      }
    });
  });
});