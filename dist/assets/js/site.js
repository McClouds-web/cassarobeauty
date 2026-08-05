/* Beauty Shop — shared behaviour */
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
