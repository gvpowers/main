(function () {
  'use strict';

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Theme toggle ----------
  (function initTheme() {
    var toggle = document.getElementById('themeToggle');
    if (!toggle) return;
    toggle.addEventListener('click', function () {
      var root = document.documentElement;
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('gvp-theme', next); } catch (e) {}
      var meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.setAttribute('content', next === 'dark' ? '#0a0e14' : '#0b3d91');
    });
  })();

  // ---------- Mobile navigation toggle ----------
  var toggle = document.getElementById('navToggle');
  var menu = document.getElementById('navMenu');
  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      toggle.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    });
    // Close when a link in the mobile menu is tapped
    menu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        menu.classList.remove('open');
        toggle.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });
  }

  // ---------- Solutions dropdown (desktop hover + mobile tap) ----------
  var dd = document.getElementById('solutionsDropdown');
  var ddToggle = document.querySelector('.dd-toggle');
  var isMobile = function () { return window.innerWidth <= 860; };

  if (ddToggle && dd) {
    ddToggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var open = dd.classList.toggle('open');
      ddToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!dd.contains(e.target) && dd.classList.contains('open')) {
        dd.classList.remove('open');
        ddToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Close dropdown/menu on resize to desktop
  window.addEventListener('resize', function () {
    if (!isMobile()) {
      if (dd) dd.classList.remove('open');
      if (ddToggle) ddToggle.setAttribute('aria-expanded', 'false');
      if (menu) { menu.classList.remove('open'); toggle.classList.remove('open'); document.body.style.overflow = ''; }
    }
  });

  // ---------- Animated statistic counters ----------
  function animateCounter(el) {
    if (!el || el.dataset.done) return;
    if (prefersReducedMotion) {
      el.dataset.done = '1';
      return;
    }
    var target = parseFloat(el.getAttribute('data-target'));
    var suffix = el.getAttribute('data-suffix') || '';
    var prefix = el.getAttribute('data-prefix') || '';
    var duration = 1500;
    var start = null;

    function step(timestamp) {
      if (!start) start = timestamp;
      var progress = Math.min((timestamp - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = Math.floor(eased * target);
      el.textContent = prefix + value + suffix;
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = prefix + target + suffix;
        el.dataset.done = '1';
      }
    }
    requestAnimationFrame(step);
  }

  function initCounters() {
    if (!('IntersectionObserver' in window) || prefersReducedMotion) {
      document.querySelectorAll('.counter[data-target]').forEach(animateCounter);
      return;
    }
    var known = new WeakMap();
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          animateCounter(el);
          known.set(el, true);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.35 });
    document.querySelectorAll('.counter[data-target]').forEach(function (el) {
      observer.observe(el);
    });
    window.__counterObserver = observer;
  }

  // ---------- Scroll reveal ----------
  function initReveal() {
    var items = document.querySelectorAll('.reveal, .service-card.reveal');
    if (!items.length || prefersReducedMotion) {
      items.forEach(function (el) { if (el.classList.contains('reveal')) el.classList.add('in-view'); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { observer.observe(el); });
  }

  // ---------- Project filtering ----------
  function initProjectFilter() {
    var buttons = document.querySelectorAll('.project-filter .filter-btn');
    var cards = document.querySelectorAll('#projectGrid .project-card');
    if (!buttons.length) return;

    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        buttons.forEach(function (b) {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');

        var filter = btn.getAttribute('data-filter');
        cards.forEach(function (card) {
          var shows;
          if (filter === 'all') shows = true;
          else if (filter === 'completed') shows = card.dataset.status === 'completed';
          else if (filter === 'ongoing') shows = card.dataset.status === 'ongoing';
          else if (filter === 'solar') shows = card.dataset.solar === '1';
          else shows = true;
          card.classList.toggle('hidden', !shows);
        });
      });
    });
  }

  // ---------- Auto-hide flash messages ----------
  document.querySelectorAll('.flash').forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = 'opacity .4s ease, transform .4s ease';
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-8px)';
      setTimeout(function () { flash.remove(); }, 450);
    }, 5000);
  });

  function init() {
    initCounters();
    initReveal();
    initProjectFilter();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
