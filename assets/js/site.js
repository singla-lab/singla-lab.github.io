/* Singla Lab — progressive enhancement only.
   Every page is fully readable with JavaScript disabled. */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

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

    var apply = function (key, value) {
      pubs.forEach(function (p) {
        var show = value === 'all' || p.getAttribute(key) === value;
        p.hidden = !show;
      });
      // hide year blocks that ended up empty
      var shown = 0;
      years.forEach(function (block) {
        var visible = block.querySelectorAll('[data-pub]:not([hidden])').length;
        block.hidden = visible === 0;
        shown += visible;
      });
      if (counter) counter.textContent = shown;
    };

    filterBar.addEventListener('click', function (e) {
      var btn = e.target.closest('.chip');
      if (!btn) return;
      var group = btn.getAttribute('data-group');
      // reset every chip in the bar, then activate this one
      filterBar.querySelectorAll('.chip').forEach(function (c) {
        c.setAttribute('aria-pressed', String(c === btn));
      });
      apply(group === 'type' ? 'data-type' : 'data-topic', btn.getAttribute('data-value'));
    });
  }

  /* ---- footer year ---- */
  var y = document.querySelector('[data-year]');
  if (y) y.textContent = new Date().getFullYear();
})();
