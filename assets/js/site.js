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
    drawer.setAttribute('aria-hidden', on ? 'false' : 'true');
    if (open) {
      open.classList.toggle('is-active', on);   // burger morphs to a cross
      open.setAttribute('aria-expanded', on ? 'true' : 'false');
    }
    /* lock the page behind the drawer without losing scroll position */
    if (on) {
      drawer.__y = window.scrollY;
      document.body.style.position = 'fixed';
      document.body.style.top = -drawer.__y + 'px';
      document.body.style.width = '100%';
    } else {
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.width = '';
      if (typeof drawer.__y === 'number') window.scrollTo(0, drawer.__y);
    }
    if (on) {
      var first = drawer.querySelector('a');
      if (first) setTimeout(function () { first.focus({ preventScroll: true }); }, 260);
    } else if (open) {
      open.focus({ preventScroll: true });
    }
  }
  if (open)  open.addEventListener('click', function () {
    setDrawer(!drawer.classList.contains('is-open'));
  });
  if (close) close.addEventListener('click', function () { setDrawer(false); });
  if (scrim) scrim.addEventListener('click', function () { setDrawer(false); });

  /* Escape closes it; following a link closes it too */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer && drawer.classList.contains('is-open')) setDrawer(false);
  });
  if (drawer) {
    drawer.addEventListener('click', function (e) {
      if (e.target.closest('a[href]')) setDrawer(false);
    });
  }
  /* a resize past the breakpoint should not leave the page locked */
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1024 && drawer && drawer.classList.contains('is-open')) setDrawer(false);
  });

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
  var search  = document.querySelector('[data-product-search]');
  var sorter  = document.querySelector('[data-product-sort]');
  var empty   = null;

  /* The order the page was built in, so "Default Sorting" can return to it. */
  cards.forEach(function (card, i) { card.dataset.order = i; });

  function cardText(card) {
    var brand = card.getAttribute('data-brand') || '';
    var title = card.querySelector('.pcard__name, h3, h4');
    return (brand + ' ' + (title ? title.textContent : '') + ' ' +
            (card.getAttribute('data-cat') || '')).toLowerCase();
  }

  function matchesSearch(card) {
    var q = (search && search.value || '').trim().toLowerCase();
    if (!q) return true;
    /* Every word must appear somewhere, so "anua serum" narrows rather than
       widening the way an OR would. */
    return q.split(/\s+/).every(function (word) {
      return cardText(card).indexOf(word) !== -1;
    });
  }

  function sortCards() {
    if (!sorter) return;
    var mode = sorter.value;
    var titleOf = function (c) {
      var t = c.querySelector('.pcard__name, h3, h4');
      return (t ? t.textContent : '').trim().toLowerCase();
    };
    var brandOf = function (c) { return (c.getAttribute('data-brand') || '').toLowerCase(); };

    var sorted = cards.slice().sort(function (a, b) {
      if (mode === 'name-asc')  return titleOf(a).localeCompare(titleOf(b));
      if (mode === 'name-desc') return titleOf(b).localeCompare(titleOf(a));
      if (mode === 'brand-asc') return brandOf(a).localeCompare(brandOf(b)) ||
                                       titleOf(a).localeCompare(titleOf(b));
      return Number(a.dataset.order) - Number(b.dataset.order);
    });
    sorted.forEach(function (c) { grid.appendChild(c); });
  }

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
      var ok = (!active || matches(card, by)) && matchesSearch(card);
      card.hidden = !ok;
      if (ok) shown++;
    });

    if (counter) {
      counter.textContent = 'Showing ' + shown + ' product' + (shown === 1 ? '' : 's');
    }
    if (clear) clear.hidden = !active && !(search && search.value.trim());

    if (!shown) {
      if (!empty) {
        empty = document.createElement('p');
        empty.className = 'filters__empty';
        empty.textContent = 'Nothing matched. Try a different word or remove a filter.';
        grid.parentNode.insertBefore(empty, grid.nextSibling);
      }
      empty.hidden = false;
    } else if (empty) {
      empty.hidden = true;
    }
  }

  boxes.forEach(function (b) { b.addEventListener('change', apply); });

  if (search) {
    search.addEventListener('input', apply);
    /* Enter in a lone search field would otherwise submit and reload. */
    search.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') e.preventDefault();
    });
  }

  if (sorter) {
    sorter.addEventListener('change', function () { sortCards(); apply(); });
  }

  if (clear) {
    clear.addEventListener('click', function () {
      boxes.forEach(function (b) { b.checked = false; });
      if (search) search.value = '';
      apply();
    });
  }

  /* A search term can arrive from the header, which has no input of its own. */
  if (location.hash === '#search' && search) {
    search.focus();
    search.scrollIntoView({ block: 'center' });
  }

  var params  = new URLSearchParams(location.search);
  var initial = params.get('q');
  if (initial && search) { search.value = initial; }

  /* The Brands page links here as shop.html?brand=Medicube. Without this the
     link lands on the full unfiltered grid, which is what it used to do. Any
     facet works the same way, so ?cat=Toners is available too. */
  var preset = false;
  ['brand', 'cat', 'skin', 'concern'].forEach(function (facet) {
    params.getAll(facet).forEach(function (want) {
      var target = want.trim().toLowerCase();
      boxes.forEach(function (b) {
        if (b.getAttribute('data-facet') === facet &&
            b.value.trim().toLowerCase() === target) {
          b.checked = true;
          preset = true;
        }
      });
    });
  });

  if (preset) {
    apply();
    /* The grid sits below a full-height cover, so a filtered arrival would
       otherwise open on a photograph with the result out of sight. */
    var anchor = document.querySelector('[data-result-count]') || grid;
    if (anchor && 'scrollIntoView' in anchor) {
      anchor.scrollIntoView({ block: 'start' });
    }
  } else if (initial || (search && search.value)) {
    apply();
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

/* -------------------------------------------------------------------------
   Reveal on scroll
   Elements fade and rise once, the first time they enter the viewport. Items
   inside the same row are staggered a little so a grid arrives as a sequence
   rather than a block. Anything already on screen at load is revealed
   immediately, so nothing above the fold waits for a scroll event.
   ------------------------------------------------------------------------- */
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!('IntersectionObserver' in window)) return;

  var SELECTOR = [
    '.section-head', '.pcard', '.brandcard', '.cat', '.vmcard', '.infocard',
    '.post', '.promo', '.videoblock', '.about-strip__gallery > div',
    '.about-strip__copy', '.deals__side', '.deals__mid', '.arrivals__feature',
    '.insta a', '.insta .ph-img', '.newsletter .wrap', '.trust__item'
  ].join(',');

  var items = Array.prototype.slice.call(document.querySelectorAll(SELECTOR));
  if (!items.length) return;

  items.forEach(function (el) {
    el.classList.add('reveal');
    // stagger by position among siblings, capped so long grids do not crawl
    var i = Array.prototype.indexOf.call(el.parentNode.children, el);
    var delay = Math.min(i, 5) * 60;
    if (delay) el.style.transitionDelay = delay + 'ms';
  });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      io.unobserve(entry.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

  items.forEach(function (el) {
    var box = el.getBoundingClientRect();
    if (box.top < window.innerHeight) {
      el.classList.add('is-in');       // already visible at load
    } else {
      io.observe(el);
    }
  });
})();


/* -------------------------------------------------------------------------
   Product gallery
   The thumbnails and the arrows were markup only — nothing ever listened to
   them. It went unnoticed while three of the four thumbnails were empty
   placeholders; with real photographs in place the stage has to follow.

   Each image is wrapped in <picture> with a WebP <source>, so swapping the
   img src alone changes nothing: the source still matches and the browser
   keeps showing the old file. Both have to move together.
   ------------------------------------------------------------------------- */
(function () {
  var stage = document.querySelector('.pdp__stage');
  if (!stage) return;

  var stageImg = stage.querySelector('img');
  var stageSource = stage.querySelector('source');
  var thumbs = Array.prototype.slice.call(
    document.querySelectorAll('.pdp__thumbs button'));
  if (!stageImg || thumbs.length < 1) return;

  var shots = thumbs.map(function (b) {
    var im = b.querySelector('img');
    var so = b.querySelector('source');
    return {
      src: im ? im.getAttribute('src') : '',
      webp: so ? so.getAttribute('srcset') : '',
      alt: im ? im.getAttribute('alt') : ''
    };
  }).filter(function (s) { return s.src; });

  if (!shots.length) return;
  var index = 0;

  function show(next) {
    index = (next + shots.length) % shots.length;
    var shot = shots[index];
    /* Source first: if the img loaded before the source updated, the browser
       would briefly show the previous photograph. */
    if (stageSource) {
      if (shot.webp) stageSource.setAttribute('srcset', shot.webp);
      else stageSource.removeAttribute('srcset');
    }
    stageImg.setAttribute('src', shot.src);
    stageImg.setAttribute('alt', shot.alt || stageImg.getAttribute('alt') || '');

    thumbs.forEach(function (b, i) {
      b.classList.toggle('is-active', i === index);
      b.setAttribute('aria-current', i === index ? 'true' : 'false');
    });
  }

  thumbs.forEach(function (b, i) {
    b.addEventListener('click', function (e) { e.preventDefault(); show(i); });
  });

  var prev = stage.querySelector('.pdp__arrow--prev');
  var next = stage.querySelector('.pdp__arrow--next');
  if (prev) prev.addEventListener('click', function (e) { e.preventDefault(); show(index - 1); });
  if (next) next.addEventListener('click', function (e) { e.preventDefault(); show(index + 1); });

  /* A single photograph needs no controls at all. */
  if (shots.length < 2) {
    [prev, next].forEach(function (b) { if (b) b.hidden = true; });
    var strip = document.querySelector('.pdp__thumbs');
    if (strip) strip.hidden = true;
  }

  /* Arrow keys move the gallery when it has focus, which is what a keyboard
     user expects of a carousel. */
  stage.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
  });

  show(0);
})();

/* ------------------------------------------------------- copy link to share
   Instagram has no web share endpoint, so the share row offers a copy link
   instead. The Clipboard API needs a secure context and can be refused, so a
   textarea + execCommand stands behind it and the button never fails silently.
   ------------------------------------------------------------------------ */
(function () {
  var buttons = document.querySelectorAll('[data-copy-link]');
  if (!buttons.length) return;

  function say(message) {
    if (window.Cassaro && window.Cassaro.toast) window.Cassaro.toast(message);
  }

  function fallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var url = window.location.href.split('#')[0];
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(function () {
          say('Link copied');
        }, function () {
          say(fallback(url) ? 'Link copied' : 'Press ⌘C to copy the link');
        });
      } else {
        say(fallback(url) ? 'Link copied' : 'Press ⌘C to copy the link');
      }
    });
  });
})();
