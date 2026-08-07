/* Cassaro Beauty — shared behaviour */
(function () {
  'use strict';

  /* Mobile drawer */
  var drawer = document.getElementById('drawer');
  var scrim  = document.getElementById('scrim');
  var open   = document.getElementById('burger');
  var close  = document.getElementById('drawer-close');
  function setDrawer(on) {
    if (!drawer || !scrim) return;
    drawer.classList.toggle('is-open', on);
    scrim.classList.toggle('is-open', on);
    document.body.style.overflow = on ? 'hidden' : '';
  }
  if (open)  open.addEventListener('click', function () { setDrawer(true); });
  if (close) close.addEventListener('click', function () { setDrawer(false); });
  if (scrim) scrim.addEventListener('click', function () { setDrawer(false); });

  /* Accordions — one open at a time */
  document.querySelectorAll('.acc__head').forEach(function (head) {
    head.addEventListener('click', function () {
      var acc = head.parentElement;
      var wasOpen = acc.classList.contains('is-open');
      acc.parentElement.querySelectorAll('.acc.is-open').forEach(function (o) {
        o.classList.remove('is-open');
        var s = o.querySelector('.acc__sign'); if (s) s.textContent = '+';
      });
      if (!wasOpen) {
        acc.classList.add('is-open');
        var sign = acc.querySelector('.acc__sign'); if (sign) sign.textContent = '−';
      }
    });
  });

  /* Filter chips / tabs */
  document.querySelectorAll('.chips').forEach(function (group) {
    group.addEventListener('click', function (e) {
      var chip = e.target.closest('.chip');
      if (!chip) return;
      group.querySelectorAll('.chip').forEach(function (c) { c.classList.remove('is-active'); });
      chip.classList.add('is-active');
    });
  });

  /* Quantity steppers: [-] <input> [+] */
  document.querySelectorAll('[data-qty]').forEach(function (box) {
    var input = box.querySelector('input');
    var btns  = box.querySelectorAll('button');
    if (!input || btns.length < 2) return;
    btns[0].addEventListener('click', function () {
      input.value = Math.max(1, (parseInt(input.value, 10) || 1) - 1);
    });
    btns[1].addEventListener('click', function () {
      input.value = (parseInt(input.value, 10) || 1) + 1;
    });
  });

  /* Hero cover slideshow: crossfade, dots, auto-advance.
     Pauses while the tab is hidden, and never auto-advances for visitors who
     have asked for reduced motion. */
  var hero = document.querySelector('[data-hero-slider]');
  if (hero) {
    var slides = hero.querySelectorAll('.hero__slide');
    var dots = hero.querySelectorAll('.hero__dots button');
    var idx = 0, timer = null;
    var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function show(n) {
      idx = (n + slides.length) % slides.length;
      slides.forEach(function (el, k) { el.classList.toggle('is-active', k === idx); });
      dots.forEach(function (el, k) {
        el.classList.toggle('is-active', k === idx);
        el.setAttribute('aria-selected', k === idx ? 'true' : 'false');
      });
    }
    function start() {
      if (!still && !timer && slides.length > 1) {
        timer = setInterval(function () { show(idx + 1); }, 5000);
      }
    }
    function stop() { clearInterval(timer); timer = null; }

    dots.forEach(function (el, k) {
      el.addEventListener('click', function () { show(k); stop(); start(); });
    });
    /* No pause on hover: the hero sits behind the announcement bar, so a
       cursor resting near the top of the page would hold the loop still. */
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { stop(); } else { start(); }
    });
    start();
  }

  /* Filter sidebar collapses to a disclosure below 1024 */
  var filters = document.querySelector('.filters');
  var ftitle = document.querySelector('.filters__title');
  if (filters && ftitle) {
    ftitle.addEventListener('click', function () {
      if (window.matchMedia('(max-width: 1024px)').matches) {
        filters.classList.toggle('is-open');
      }
    });
  }

  /* Tabs (product details, account) */
  document.querySelectorAll('[data-tabs]').forEach(function (nav) {
    nav.addEventListener('click', function (e) {
      var tab = e.target.closest('[data-tab]');
      if (!tab) return;
      e.preventDefault();
      var name = tab.getAttribute('data-tab');
      nav.querySelectorAll('[data-tab]').forEach(function (t) { t.classList.remove('is-active'); });
      tab.classList.add('is-active');
      document.querySelectorAll('[data-panel]').forEach(function (p) {
        p.hidden = p.getAttribute('data-panel') !== name;
      });
    });
  });
})();

/* -------------------------------------------------------------------------
   Shop filters
   Each product card carries data-brand / data-cat / data-skin / data-concern.
   Checking boxes within a group is an OR; across groups it is an AND, which is
   how shoppers expect facets to behave: "Serums or Toners, from SKIN1004".
   ------------------------------------------------------------------------- */
(function () {
  var grid = document.querySelector('[data-product-grid]');
  if (!grid) return;

  var boxes = Array.prototype.slice.call(
    document.querySelectorAll('.filters input[type="checkbox"][data-facet]'));
  if (!boxes.length) return;

  var cards   = Array.prototype.slice.call(grid.querySelectorAll('.pcard'));
  var counter = document.querySelector('[data-result-count]');
  var clear   = document.querySelector('[data-filter-clear]');
  var empty   = null;

  function selected() {
    var by = {};
    boxes.forEach(function (b) {
      if (!b.checked) return;
      (by[b.getAttribute('data-facet')] = by[b.getAttribute('data-facet')] || []).push(b.value);
    });
    return by;
  }

  function matches(card, by) {
    return Object.keys(by).every(function (facet) {
      var have = (card.getAttribute('data-' + facet) || '').split(' ').filter(Boolean);
      var whole = card.getAttribute('data-' + facet) || '';
      return by[facet].some(function (want) {
        // brand and category are whole values that may contain spaces
        return facet === 'brand' || facet === 'cat'
          ? whole === want
          : have.indexOf(want) !== -1;
      });
    });
  }

  function apply() {
    var by = selected();
    var active = Object.keys(by).length > 0;
    var shown = 0;

    cards.forEach(function (card) {
      var ok = !active || matches(card, by);
      card.hidden = !ok;
      if (ok) shown++;
    });

    if (counter) {
      counter.textContent = 'Showing ' + shown + ' product' + (shown === 1 ? '' : 's');
    }
    if (clear) clear.hidden = !active;

    if (!shown) {
      if (!empty) {
        empty = document.createElement('p');
        empty.className = 'filters__empty';
        empty.textContent = 'No products match those filters. Try removing one.';
        grid.parentNode.insertBefore(empty, grid.nextSibling);
      }
      empty.hidden = false;
    } else if (empty) {
      empty.hidden = true;
    }
  }

  boxes.forEach(function (b) { b.addEventListener('change', apply); });
  if (clear) {
    clear.addEventListener('click', function () {
      boxes.forEach(function (b) { b.checked = false; });
      apply();
    });
  }
})();

/* Shop filters collapse behind a toggle on small screens, where the sidebar
   would otherwise push every product below a 30-checkbox list. */
(function () {
  var btn = document.querySelector('[data-filters-toggle]');
  var panel = document.getElementById('shop-filters');
  if (!btn || !panel) return;
  btn.addEventListener('click', function () {
    var open = panel.classList.toggle('is-open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
})();
