/* Singla Lab — progressive enhancement only.
   Every page is fully readable with JavaScript disabled. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- theme ----
     The attribute is already stamped by the inline script in <head>; this only
     handles the button and, while no explicit choice is stored, keeps
     following the system if it changes under us. */
  var root = document.documentElement;
  var themeBtn = document.querySelector('[data-theme-toggle]');
  var meta = document.querySelector('meta[name="theme-color"]');
  var sysDark = window.matchMedia('(prefers-color-scheme: dark)');

  var paint = function (theme) {
    root.dataset.theme = theme;
    if (meta) {
      meta.setAttribute('content', theme === 'dark' ? '#17120E' : '#F9EBDE');
    }
    if (themeBtn) {
      var next = theme === 'dark' ? 'light' : 'dark';
      var label = 'Switch to ' + next + ' theme';
      themeBtn.setAttribute('aria-label', label);
      themeBtn.setAttribute('title', label);
    }
  };

  paint(root.dataset.theme === 'dark' ? 'dark' : 'light');

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
      paint(next);
    });
  }

  var onSystem = function (e) {
    var stored;
    try { stored = localStorage.getItem('theme'); } catch (err) { stored = null; }
    if (stored !== 'light' && stored !== 'dark') paint(e.matches ? 'dark' : 'light');
  };
  if (sysDark.addEventListener) sysDark.addEventListener('change', onSystem);
  else if (sysDark.addListener) sysDark.addListener(onSystem);

  /* ---- colourway ----
     Indigo is what the stylesheet already is, so choosing it clears the
     attribute rather than setting one. The boot script in <head> has stamped
     any stored choice already; this only wires the menu. */
  var picker = document.querySelector('[data-accent-picker]');
  if (picker) {
    var accentBtn = picker.querySelector('button');
    var accentMenu = picker.querySelector('.accent-menu');
    var swatches = Array.prototype.slice.call(picker.querySelectorAll('.accent-sw'));

    var openMenu = function (open) {
      accentMenu.hidden = !open;
      accentBtn.setAttribute('aria-expanded', String(open));
    };

    var mark = function (name) {
      swatches.forEach(function (sw) {
        sw.setAttribute('aria-checked', String(sw.getAttribute('data-accent') === name));
      });
    };

    mark(root.dataset.accent || 'indigo');

    accentBtn.addEventListener('click', function () {
      openMenu(accentMenu.hidden);
    });

    swatches.forEach(function (sw) {
      sw.addEventListener('click', function () {
        var name = sw.getAttribute('data-accent');
        if (name === 'indigo') delete root.dataset.accent;
        else root.dataset.accent = name;
        try { localStorage.setItem('accent', name); } catch (e) { /* private mode */ }
        mark(name);
        openMenu(false);
        accentBtn.focus();
      });
    });

    document.addEventListener('click', function (e) {
      if (!accentMenu.hidden && !picker.contains(e.target)) openMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !accentMenu.hidden) { openMenu(false); accentBtn.focus(); }
    });
  }

  /* ---- Devanagari / Roman ----
     Both scripts are in the page; this only decides which one is shown, so a
     reader with no JavaScript still gets the verse as written. */
  var scriptBtn = document.querySelector('[data-script-toggle]');
  if (scriptBtn) {
    var setScript = function (mode) {
      if (mode === 'iast') root.dataset.script = 'iast';
      else delete root.dataset.script;
      var label = mode === 'iast'
        ? 'Show the Sanskrit in Devanagari'
        : 'Show the Sanskrit in Roman letters';
      scriptBtn.setAttribute('aria-label', label);
      scriptBtn.setAttribute('title', label);
    };
    setScript(root.dataset.script === 'iast' ? 'iast' : 'devanagari');
    scriptBtn.addEventListener('click', function () {
      var next = root.dataset.script === 'iast' ? 'devanagari' : 'iast';
      try { localStorage.setItem('script', next); } catch (e) { /* private mode */ }
      setScript(next);
    });
  }

  /* ---- copy a citation ----
     The text is on the button, put there at build time, so the citation can
     never disagree with the entry it sits under. */
  var copyText = function (text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:0;left:-9999px;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(ta);
      ok ? resolve() : reject();
    });
  };

  var citeState = function (btn, cls, word, label) {
    btn.classList.remove('is-copied', 'is-failed');
    if (cls) btn.classList.add(cls);
    var span = btn.querySelector('span');
    if (span) span.textContent = word;
    btn.setAttribute('aria-label', label);
  };

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.cite') : null;
    if (!btn) return;
    var text = btn.getAttribute('data-cite');
    if (!text) return;
    var settle = function () {
      if (btn._t) clearTimeout(btn._t);
      btn._t = setTimeout(function () {
        citeState(btn, null, 'Cite', 'Copy citation');
      }, 1800);
    };
    copyText(text).then(function () {
      citeState(btn, 'is-copied', 'Copied', 'Citation copied');
      settle();
    }, function () {
      /* say so rather than look like it worked */
      citeState(btn, 'is-failed', 'Failed', 'Could not copy the citation');
      settle();
    });
  });

  /* ---- sticky header shadow ---- */
  var hdr = document.querySelector('.hdr');
  if (hdr) {
    var onScroll = function () {
      hdr.classList.toggle('is-stuck', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---- mobile nav ---- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });
    nav.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        toggle.setAttribute('aria-expanded', 'false');
        nav.classList.remove('is-open');
        toggle.focus();
      }
    });
  }

  /* ---- reveal on scroll ---- */
  var revealables = document.querySelectorAll('.rv');
  if (!revealables.length) { /* nothing to do */ }
  else if (reduced || !('IntersectionObserver' in window)) {
    for (var i = 0; i < revealables.length; i++) revealables[i].classList.add('in');
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---- publication filters ---- */
  var filterBar = document.querySelector('[data-filters]');
  if (filterBar) {
    var pubs = Array.prototype.slice.call(document.querySelectorAll('[data-pub]'));
    var years = Array.prototype.slice.call(document.querySelectorAll('[data-year-block]'));
    var counter = document.querySelector('[data-pub-count]');

    var apply = function (match) {
      pubs.forEach(function (p) { p.hidden = !match(p); });
      // hide year blocks that ended up empty
      var shown = 0;
      years.forEach(function (block) {
        var visible = block.querySelectorAll('[data-pub]:not([hidden])').length;
        block.hidden = visible === 0;
        shown += visible;
      });
      if (counter) counter.textContent = shown;
    };

    var matcher = function (group, value) {
      if (value === 'all') return function () { return true; };
      if (group === 'year') {
        // "last n years" is n whole calendar years, this one included. The cut-off
        // is read off the clock here so it never goes stale between rebuilds.
        var floor = new Date().getFullYear() - (parseInt(value, 10) - 1);
        return function (p) {
          return parseInt(p.getAttribute('data-pub-year'), 10) >= floor;
        };
      }
      var key = group === 'type' ? 'data-type' : 'data-topic';
      return function (p) { return p.getAttribute(key) === value; };
    };

    filterBar.addEventListener('click', function (e) {
      var btn = e.target.closest('.chip');
      if (!btn) return;
      // reset every chip in the bar, then activate this one
      filterBar.querySelectorAll('.chip').forEach(function (c) {
        c.setAttribute('aria-pressed', String(c === btn));
      });
      apply(matcher(btn.getAttribute('data-group'), btn.getAttribute('data-value')));
    });
  }

  /* ---- footer year ---- */
  var y = document.querySelector('[data-year]');
  if (y) y.textContent = new Date().getFullYear();
})();
