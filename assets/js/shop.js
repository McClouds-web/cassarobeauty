/* Cassaro Beauty — cart, wishlist and the shared shop store.
   -------------------------------------------------------------------------
   The site is static, so the cart lives in localStorage. Product facts are
   read off the page that already displays them (card markup, product detail
   markup) rather than duplicated into a second catalogue that could drift.

   Prices: the catalogue does not carry real prices yet — every product still
   renders the R___ placeholder. Anything that cannot be priced is reported as
   "To be confirmed" rather than guessed. Once prices land in the markup this
   file starts totalling them with no further change.
   ------------------------------------------------------------------------- */
(function () {
  'use strict';

  var CFG = window.CASSARO_CONFIG || {};
  var K = {
    cart:    'cassaro.cart.v1',
    wish:    'cassaro.wishlist.v1',
    details: 'cassaro.checkout.v1',
    orders:  'cassaro.orders.v1',
    last:    'cassaro.lastorder.v1'
  };

  /* ---------------------------------------------------------------- storage */
  function read(key, fallback) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch (e) { return fallback; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  }

  /* ------------------------------------------------------------------ money */
  function parsePrice(text) {
    if (!text) return null;
    var m = String(text).replace(/\s/g, '').match(/R?([0-9]+(?:[.,][0-9]{1,2})?)/);
    if (!m) return null;
    var n = parseFloat(m[1].replace(',', '.'));
    return isNaN(n) ? null : n;
  }
  function money(n) {
    if (n === null || n === undefined) return CFG.pricePlaceholder || 'R___';
    return (CFG.currencySymbol || 'R') +
      n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }

  /* -------------------------------------------------- reading a product off the page */
  function slugFromHref(href) {
    if (!href) return '';
    return href.split('/').pop().replace(/\.html.*$/, '');
  }

  /* A product card anywhere in the site (home, shop, skincare, brands...). */
  function fromCard(card) {
    var name = card.querySelector('.pcard__name');
    var img  = card.querySelector('img');
    var price = card.querySelector('.price');
    return {
      slug:  slugFromHref(card.getAttribute('href')),
      name:  name ? name.textContent.trim() : '',
      brand: card.getAttribute('data-brand') || '',
      img:   img ? img.getAttribute('src') : '',
      price: parsePrice(price ? price.textContent : ''),
      variant: ''
    };
  }

  /* The product detail page. */
  function fromPdp() {
    var title = document.querySelector('.pdp__title');
    if (!title) return null;
    var clone = title.cloneNode(true);
    clone.querySelectorAll('span').forEach(function (s) { s.remove(); });

    var brand = '';
    document.querySelectorAll('.pdp__meta div').forEach(function (row) {
      var dt = row.querySelector('dt');
      if (dt && /brand/i.test(dt.textContent)) {
        var dd = row.querySelector('dd');
        if (dd) brand = dd.textContent.trim();
      }
    });
    if (!brand) {
      var cat = document.querySelector('.pdp__buy .pcard__cat');
      if (cat) brand = cat.textContent.split('·')[0].trim();
    }

    var stage = document.querySelector('.pdp__stage img');
    var size  = document.querySelector('.pdp__sizes .chip.is-active');
    var price = document.querySelector('.pdp__price');

    return {
      slug:  slugFromHref(location.pathname) || 'product',
      name:  clone.textContent.trim(),
      brand: brand,
      img:   stage ? stage.getAttribute('src') : '',
      price: parsePrice(price ? price.textContent : ''),
      variant: size ? size.textContent.trim() : ''
    };
  }

  /* A wishlist / cart row rendered by this file. */
  function fromRow(row) {
    return {
      slug:  row.getAttribute('data-slug'),
      variant: row.getAttribute('data-variant') || ''
    };
  }

  /* ------------------------------------------------------------------- cart */
  function key(item) { return item.slug + '|' + (item.variant || ''); }

  var cart = {
    all: function () { return read(K.cart, []); },
    save: function (items) { write(K.cart, items); publish(); },
    add: function (product, qty) {
      var items = cart.all();
      var found = null;
      items.forEach(function (i) { if (key(i) === key(product)) found = i; });
      if (found) {
        found.qty += (qty || 1);
        /* keep the stored facts fresh if the page has better ones now */
        found.price = product.price;
        found.img = product.img || found.img;
      } else {
        items.push({
          slug: product.slug, name: product.name, brand: product.brand,
          img: product.img, price: product.price,
          variant: product.variant || '', qty: qty || 1
        });
      }
      cart.save(items);
      track('add_to_cart', { item_name: product.name, quantity: qty || 1 });
    },
    setQty: function (ref, qty) {
      var items = cart.all().map(function (i) {
        if (key(i) === key(ref)) i.qty = Math.max(1, qty);
        return i;
      });
      cart.save(items);
    },
    remove: function (ref) {
      cart.save(cart.all().filter(function (i) { return key(i) !== key(ref); }));
    },
    clear: function () { cart.save([]); },
    count: function () {
      return cart.all().reduce(function (n, i) { return n + i.qty; }, 0);
    },
    /* null when any line has no price yet — a partial total would mislead */
    subtotal: function () {
      var items = cart.all();
      if (!items.length) return 0;
      var total = 0;
      for (var i = 0; i < items.length; i++) {
        if (items[i].price === null || items[i].price === undefined) return null;
        total += items[i].price * items[i].qty;
      }
      return total;
    }
  };

  /* --------------------------------------------------------------- wishlist */
  var wishlist = {
    all: function () { return read(K.wish, []); },
    save: function (items) { write(K.wish, items); publish(); },
    has: function (slug) {
      return wishlist.all().some(function (i) { return i.slug === slug; });
    },
    toggle: function (product) {
      var items = wishlist.all();
      var next = items.filter(function (i) { return i.slug !== product.slug; });
      var added = next.length === items.length;
      if (added) next.push(product);
      wishlist.save(next);
      return added;
    },
    remove: function (slug) {
      wishlist.save(wishlist.all().filter(function (i) { return i.slug !== slug; }));
    },
    clear: function () { wishlist.save([]); }
  };

  /* ------------------------------------------------------------- analytics */
  /* No analytics package is installed on the site today. These calls are
     deliberately defensive so that adding GA4 or GTM later starts collecting
     them without another edit. A WhatsApp hand-off is never a purchase. */
  function track(event, data) {
    try {
      if (typeof window.gtag === 'function') window.gtag('event', event, data || {});
      if (Array.isArray(window.dataLayer)) {
        window.dataLayer.push(Object.assign({ event: event }, data || {}));
      }
    } catch (e) {}
  }

  /* ------------------------------------------------------------------ toast */
  var toastEl = null, toastTimer = null;
  function toast(message) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = message;
    toastEl.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, 2600);
  }

  /* ------------------------------------------------------- header cart count */
  function publish() {
    var n = cart.count();
    document.querySelectorAll('[data-cart-count]').forEach(function (el) {
      el.textContent = n;
      el.hidden = n === 0;
    });
    var w = wishlist.all().length;
    document.querySelectorAll('[data-wish-count]').forEach(function (el) {
      el.textContent = w;
      el.hidden = w === 0;
    });
    document.dispatchEvent(new CustomEvent('cassaro:cart'));
  }

  /* ---------------------------------------------------------- card wiring */
  /* The whole card is a link to the product page, so the tool buttons must
     stop the click from following it. */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.pcard__tools button');
    if (!btn) return;
    var card = btn.closest('.pcard');
    if (!card) return;
    e.preventDefault();
    e.stopPropagation();
    var label = (btn.getAttribute('aria-label') || '').toLowerCase();
    var product = fromCard(card);

    if (label.indexOf('cart') !== -1) {
      cart.add(product, 1);
      toast(product.name + ' added to your cart.');
    } else if (label.indexOf('wishlist') !== -1) {
      var added = wishlist.toggle(product);
      toast(added ? product.name + ' saved to your wishlist.'
                  : product.name + ' removed from your wishlist.');
    } else {
      location.href = card.getAttribute('href');
    }
  });

  /* ------------------------------------------------------ product page wiring */
  (function () {
    var actions = document.querySelector('.pdp__actions');
    if (!actions) return;
    var qtyInput = actions.querySelector('.qty input');

    function qty() { return Math.max(1, parseInt(qtyInput && qtyInput.value, 10) || 1); }

    actions.querySelectorAll('a.btn').forEach(function (a) {
      var text = a.textContent.trim().toLowerCase();
      if (text.indexOf('add to cart') !== -1) {
        a.addEventListener('click', function (e) {
          e.preventDefault();
          var p = fromPdp(); if (!p) return;
          cart.add(p, qty());
          toast(p.name + ' added to your cart.');
        });
      } else if (text.indexOf('buy now') !== -1) {
        a.addEventListener('click', function (e) {
          e.preventDefault();
          var p = fromPdp(); if (!p) return;
          cart.add(p, qty());
          location.href = 'cart.html';
        });
      }
    });

    var heart = actions.querySelector('.iconbtn[aria-label*="ishlist"]');
    if (heart) {
      heart.addEventListener('click', function () {
        var p = fromPdp(); if (!p) return;
        var added = wishlist.toggle(p);
        heart.classList.toggle('is-on', added);
        toast(added ? p.name + ' saved to your wishlist.'
                    : p.name + ' removed from your wishlist.');
      });
      var p0 = fromPdp();
      if (p0 && wishlist.has(p0.slug)) heart.classList.add('is-on');
    }
  })();

  /* -------------------------------------------------------------- cart page */
  (function () {
    var body = document.querySelector('[data-cart-rows]');
    if (!body) return;

    var empty = document.querySelector('[data-cart-empty]');
    var table = document.querySelector('[data-cart-table]');
    var tools = document.querySelector('[data-cart-tools]');

    function line(item) {
      var lineTotal = item.price === null || item.price === undefined
        ? null : item.price * item.qty;
      return '<tr data-slug="' + item.slug + '" data-variant="' + (item.variant || '') + '">' +
        '<td class="linetable__prod">' +
          '<button class="rm" type="button" aria-label="Remove" data-remove>&times;</button>' +
          (item.img ? '<img class="ph-img" src="' + item.img + '" alt="' + item.name + '" loading="lazy" decoding="async"/>' : '') +
          '<div><strong>' + item.name + '</strong><small>' + item.brand +
            (item.variant ? ' · ' + item.variant : '') + '</small></div>' +
        '</td>' +
        '<td data-label="Price">' + money(item.price) + '</td>' +
        '<td data-label="Quantity"><div class="qty">' +
          '<button type="button" data-step="-1">&minus;</button>' +
          '<input type="text" inputmode="numeric" value="' + item.qty + '" data-qty-input/>' +
          '<button type="button" data-step="1">+</button></div></td>' +
        '<td class="strong" data-label="Subtotal">' + money(lineTotal) + '</td>' +
      '</tr>';
    }

    function render() {
      var items = cart.all();
      body.innerHTML = items.map(line).join('');
      var none = items.length === 0;
      if (empty) empty.hidden = !none;
      if (table) table.hidden = none;
      if (tools) tools.hidden = none;
      summary();
    }

    body.addEventListener('click', function (e) {
      var row = e.target.closest('tr');
      if (!row) return;
      if (e.target.closest('[data-remove]')) { cart.remove(fromRow(row)); render(); return; }
      var step = e.target.closest('[data-step]');
      if (step) {
        var input = row.querySelector('[data-qty-input]');
        var next = (parseInt(input.value, 10) || 1) + parseInt(step.getAttribute('data-step'), 10);
        cart.setQty(fromRow(row), next);
        render();
      }
    });

    body.addEventListener('change', function (e) {
      var input = e.target.closest('[data-qty-input]');
      if (!input) return;
      cart.setQty(fromRow(input.closest('tr')), parseInt(input.value, 10) || 1);
      render();
    });

    var clear = document.querySelector('[data-cart-clear]');
    if (clear) clear.addEventListener('click', function (e) {
      e.preventDefault(); cart.clear(); render();
    });

    var coupon = document.querySelector('[data-coupon-apply]');
    if (coupon) coupon.addEventListener('click', function (e) {
      e.preventDefault();
      toast('Coupon codes are applied by our team when your order is confirmed on WhatsApp.');
    });

    var checkout = document.querySelector('[data-checkout-start]');
    if (checkout) checkout.addEventListener('click', function (e) {
      if (!cart.all().length) { e.preventDefault(); toast('Your cart is empty.'); return; }
      track('begin_checkout', { items: cart.count() });
    });

    render();
  })();

  /* ---------------------------------------------------------- wishlist page */
  (function () {
    var body = document.querySelector('[data-wish-rows]');
    if (!body) return;
    var empty = document.querySelector('[data-wish-empty]');
    var table = document.querySelector('[data-wish-table]');
    var tools = document.querySelector('[data-wish-tools]');

    function render() {
      var items = wishlist.all();
      body.innerHTML = items.map(function (item) {
        return '<tr data-slug="' + item.slug + '">' +
          '<td class="linetable__prod">' +
            '<button class="rm" type="button" aria-label="Remove" data-remove>&times;</button>' +
            (item.img ? '<img class="ph-img" src="' + item.img + '" alt="' + item.name + '" loading="lazy" decoding="async"/>' : '') +
            '<div><strong>' + item.name + '</strong><small>' + item.brand + '</small></div>' +
          '</td>' +
          '<td data-label="Price">' + money(item.price) + '</td>' +
          '<td data-label="Stock Status">In Stock</td>' +
          '<td style="text-align:right"><button class="btn btn--primary btn--sm" type="button" data-wish-add>Add to Cart</button></td>' +
        '</tr>';
      }).join('');
      var none = items.length === 0;
      if (empty) empty.hidden = !none;
      if (table) table.hidden = none;
      if (tools) tools.hidden = none;
    }

    body.addEventListener('click', function (e) {
      var row = e.target.closest('tr');
      if (!row) return;
      var slug = row.getAttribute('data-slug');
      if (e.target.closest('[data-remove]')) { wishlist.remove(slug); render(); return; }
      if (e.target.closest('[data-wish-add]')) {
        wishlist.all().forEach(function (i) {
          if (i.slug === slug) { cart.add(i, 1); toast(i.name + ' added to your cart.'); }
        });
      }
    });

    var clear = document.querySelector('[data-wish-clear]');
    if (clear) clear.addEventListener('click', function (e) {
      e.preventDefault(); wishlist.clear(); render();
    });

    var addAll = document.querySelector('[data-wish-add-all]');
    if (addAll) addAll.addEventListener('click', function (e) {
      e.preventDefault();
      var items = wishlist.all();
      if (!items.length) { toast('Your wishlist is empty.'); return; }
      items.forEach(function (i) { cart.add(i, 1); });
      toast(items.length + ' item' + (items.length === 1 ? '' : 's') + ' added to your cart.');
    });

    render();
  })();

  /* ------------------------------------------------- order summary aside */
  /* Shared by the cart and both checkout steps. */
  function summary() {
    var items = cart.all();
    var sub = cart.subtotal();
    document.querySelectorAll('[data-sum-items]').forEach(function (el) {
      el.textContent = cart.count();
    });
    document.querySelectorAll('[data-sum-subtotal], [data-sum-total]').forEach(function (el) {
      el.textContent = items.length ? money(sub) : money(0);
    });
  }
  document.addEventListener('cassaro:cart', summary);

  /* ------------------------------------------------------------------ export */
  window.Cassaro = {
    keys: K, read: read, write: write,
    cart: cart, wishlist: wishlist,
    money: money, parsePrice: parsePrice,
    track: track, toast: toast, summary: summary
  };

  publish();
  summary();
})();
