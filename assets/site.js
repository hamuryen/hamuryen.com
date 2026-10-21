(() => {
  const root = document.documentElement;
  const content = document.querySelector('.content');
  const sections = [...content.querySelectorAll('section[id]')];
  const links = [...document.querySelectorAll('.navigation a')];
  let activeId;
  function navigate() {
    const id = location.hash.slice(1);
    const requested = sections.find(section => section.id === id);
    const active = requested || (id === 'main' && sections.find(section => section.id === activeId)) || sections[0];
    if (id && id !== 'main' && !requested) history.replaceState(null, '', '#' + active.id);
    const changing = Boolean(activeId);
    if (active.id === activeId) return false;
    activeId = active.id;
    sections.forEach(section => { section.hidden = section !== active; });
    links.forEach(link => {
      if (link.hash === '#' + active.id) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
    content.scrollTop = 0;
    if (changing && !matchMedia('(min-width: 1050px)').matches) {
      content.scrollIntoView({ block: 'start', behavior: 'instant' });
    }
    return true;
  }
  root.classList.add('js');
  navigate();
  window.addEventListener('popstate', navigate);
  window.addEventListener('hashchange', navigate);
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    if (!sections.some(section => link.hash === '#' + section.id)) return;
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      // Prevent native fragment scrolling, including repeat clicks on the active panel.
      event.preventDefault();
      if (link.hash.slice(1) === activeId) return;
      history.pushState(null, '', link.hash);
      navigate();
      content.focus({ preventScroll: true });
    });
  });
  document.querySelector('.skip-link').addEventListener('click', event => {
    event.preventDefault();
    content.focus({ preventScroll: true });
    content.scrollIntoView({ block: 'start', behavior: 'instant' });
  });
  const system = matchMedia('(prefers-color-scheme: light)');
  let mode = 'system';
  try { mode = localStorage.getItem('theme') || 'system'; } catch {}
  if (!['light', 'dark', 'system'].includes(mode)) mode = 'system';
  function applyTheme() {
    root.dataset.theme = mode === 'system' ? (system.matches ? 'light' : 'dark') : mode;
    ['light', 'dark', 'system'].forEach(value => {
      const button = document.getElementById('theme-' + value);
      button.classList.toggle('active', mode === value);
      button.setAttribute('aria-pressed', String(mode === value));
    });
  }
  ['light', 'dark', 'system'].forEach(value => {
    document.getElementById('theme-' + value).addEventListener('click', () => {
      mode = value;
      try { localStorage.setItem('theme', mode); } catch {}
      applyTheme();
    });
  });
  system.addEventListener('change', applyTheme);
  applyTheme();
  const showSnake = Math.random() < 0.5;
  document.querySelector('.snake-panel').hidden = !showSnake;
  document.querySelector('.life-panel').hidden = showSnake;
})();
