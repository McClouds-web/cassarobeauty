/* Cassaro Beauty — WhatsApp-assisted checkout.
   -------------------------------------------------------------------------
   The website does not process money. It builds the order, gives it a
   reference, and hands the customer to WhatsApp where the team confirms
   stock, delivery cost and banking details. Nothing here marks an order paid.
   ------------------------------------------------------------------------- */
(function () {
  'use strict';

  var C = window.Cassaro;
  if (!C) return;
  var CFG = window.CASSARO_CONFIG || {};
  var K = C.keys;

  var STATUS = {
    pending:   'Pending WhatsApp Confirmation',
    awaiting:  'Awaiting Payment',
    submitted: 'Payment Submitted',
    confirmed: 'Payment Confirmed',
    processing:'Processing',
    ready:     'Ready for Dispatch',
    shipped:   'Shipped',
    delivered: 'Delivered',
    cancelled: 'Cancelled'
  };

  /* Progress steps on the order status page, in order. */
  var TIMELINE = [STATUS.pending, STATUS.awaiting, STATUS.confirmed,
                  STATUS.shipped, STATUS.delivered];

  /* --------------------------------------------------------- order reference */
  /* A static site has no shared counter, so a plain 1,2,3 sequence would repeat
     across customers. The reference keeps the CAS-###### shape but draws its
     digits from the clock and a random pair, and is checked against the
     references this browser has already issued. */
  function makeRef() {
    var used = C.read(K.orders, []).map(function (o) { return o.ref; });
    var ref;
    do {
      var n = (Date.now() % 10000) * 100 + Math.floor(Math.random() * 100);
      ref = (CFG.orderPrefix || 'CAS-') + String(n).replace(/^(\d{1,6})$/, function (s) {
        while (s.length < 6) s = '0' + s;
        return s;
      });
    } while (used.indexOf(ref) !== -1);
    return ref;
  }

  /* -------------------------------------------------------- customer details */
  var FIELDS = ['firstName', 'lastName', 'company', 'country', 'street', 'city',
                'province', 'postal', 'phone', 'email', 'notes', 'deliverySame'];

  function details() {
    var d = C.read(K.details, {}) || {};
    FIELDS.forEach(function (f) { if (d[f] === undefined) d[f] = ''; });
    return d;
  }
  function fullName(d) {
    return [d.firstName, d.lastName].filter(Boolean).join(' ').trim();
  }
  function detailsComplete(d) {
    return !!(fullName(d) && d.phone && d.email && d.province && d.city && d.street);
  }

  /* ------------------------------------------------------------ order record */
  function orders() { return C.read(K.orders, []); }
  function saveOrders(list) { C.write(K.orders, list); }
  function findOrder(ref) {
    var hit = null;
    orders().forEach(function (o) {
      if (o.ref.toLowerCase() === String(ref || '').trim().toLowerCase()) hit = o;
    });
    return hit;
  }
  function setStatus(ref, status) {
    saveOrders(orders().map(function (o) {
      if (o.ref === ref) { o.status = status; o.updated = new Date().toISOString(); }
      return o;
    }));
  }

  function createOrder() {
    var d = details();
    var items = C.cart.all();
    var order = {
      ref: makeRef(),
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      status: STATUS.pending,
      paymentMethod: 'Bank Transfer / EFT',
      items: items,
      subtotal: C.cart.subtotal(),      /* null while prices are unavailable */
      discount: null,
      deliveryFee: null,                /* quoted by the team on WhatsApp */
      total: null,
      customer: {
        name: fullName(d), phone: d.phone, email: d.email,
        province: d.province, city: d.city, address: d.street,
        postal: d.postal, notes: d.notes
      }
    };
    var list = orders();
    list.unshift(order);
    saveOrders(list);
    C.write(K.last, order.ref);
    C.track('order_reference_created', { order_reference: order.ref });
    return order;
  }

  /* --------------------------------------------------------- WhatsApp message */
  function itemLine(item, compact) {
    var label = item.qty + ' x ' + (item.brand ? item.brand + ' ' : '') + item.name +
                (item.variant ? ' (' + item.variant + ')' : '');
    if (compact || item.price === null || item.price === undefined) return label;
    return label + ' — ' + C.money(item.price) + ' each, line total ' +
           C.money(item.price * item.qty);
  }

  function buildMessage(order, compact) {
    var d = order.customer;
    var lines = [];
    lines.push('Hi ' + (CFG.storeName || 'Cassaro Beauty') + ', I would like to place an order.');
    lines.push('');
    lines.push('Order Reference: ' + order.ref);
    lines.push('');
    lines.push('Order:');
    order.items.forEach(function (i) { lines.push(itemLine(i, compact)); });
    lines.push('');
    lines.push('Subtotal: ' + (order.subtotal === null || order.subtotal === undefined
      ? (CFG.tbc || 'To be confirmed') : C.money(order.subtotal)));
    if (order.discount !== null && order.discount !== undefined) {
      lines.push('Discount: ' + C.money(order.discount));
    }
    lines.push('');
    lines.push('Delivery:');
    lines.push(order.deliveryFee === null || order.deliveryFee === undefined
      ? (CFG.tbc || 'To be confirmed') : C.money(order.deliveryFee));
    if (order.total !== null && order.total !== undefined) {
      lines.push('');
      lines.push('Total: ' + C.money(order.total));
    }
    lines.push('');
    lines.push('Customer Details:');
    lines.push('Name: ' + (d.name || '-'));
    lines.push('Phone: ' + (d.phone || '-'));
    lines.push('Email: ' + (d.email || '-'));
    lines.push('Delivery Area: ' + [d.city, d.province].filter(Boolean).join(', '));
    if (d.address) lines.push('Delivery Address: ' + d.address + (d.postal ? ', ' + d.postal : ''));
    if (d.notes) lines.push('Order Notes: ' + d.notes);
    lines.push('');
    lines.push('Please confirm availability, delivery cost and banking details so I can complete payment by bank transfer.');
    return lines.join('\n');
  }

  /* wa.me carries the message in the query string, so a very long cart has to
     stay inside a URL length browsers and WhatsApp both accept. Detail is shed
     before items are, and items are only dropped as a last resort — the note
     that says so is added only when something was actually left out. */
  var URL_BUDGET = 3500;

  function encodedLength(order, compact, keep) {
    return encodeURIComponent(messageFor(order, compact, keep)).length;
  }

  function messageFor(order, compact, keep) {
    if (keep >= order.items.length) return buildMessage(order, compact);
    var trimmed = Object.assign({}, order, { items: order.items.slice(0, keep) });
    return buildMessage(trimmed, compact) +
      '\n\n(' + (order.items.length - keep) + ' further item(s) in this order — ' +
      'please request the full list.)';
  }

  function waUrl(order) {
    var count = order.items.length;
    var compact = false;
    if (encodedLength(order, false, count) > URL_BUDGET) compact = true;
    while (count > 1 && encodedLength(order, compact, count) > URL_BUDGET) count--;
    return 'https://wa.me/' + (CFG.whatsappNumber || '') +
      '?text=' + encodeURIComponent(messageFor(order, compact, count));
  }

  /* ------------------------------------------------------- order submission */
  /* The WhatsApp draft only reaches the team if the customer presses send, so
     the order is also posted to the backend, which records it and alerts the
     owner with the customer's WhatsApp number and email. Failures are logged
     and never block the customer — the draft remains the fallback path. */
  function submitOrder(order) {
    var url = CFG.orderEndpoint;
    if (!url) return;

    var d = order.customer || {};
    var payload = {
      ref: order.ref,
      name: d.name,
      phone: d.phone,
      whatsapp: d.phone,
      email: d.email,
      address: d.address,
      city: d.city,
      province: d.province,
      postal: d.postal,
      country: details().country || 'South Africa',
      notes: d.notes,
      subtotal: order.subtotal,
      items: (order.items || []).map(function (i) {
        return { name: i.name, brand: i.brand, variant: i.variant, qty: i.qty, price: i.price };
      })
    };

    var headers = { 'Content-Type': 'application/json' };
    if (CFG.orderEndpointKey) {
      headers.apikey = CFG.orderEndpointKey;
      headers.Authorization = 'Bearer ' + CFG.orderEndpointKey;
    }

    try {
      /* keepalive lets the request finish after this page navigates away. */
      fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload),
        keepalive: true
      }).then(function (res) {
        if (!res.ok) console.warn('Order submission failed with status', res.status);
      }).catch(function (err) {
        console.warn('Order submission failed', err);
      });
    } catch (e) {
      console.warn('Order submission failed', e);
    }
  }

  /* Opening in a new tab keeps the store — and the cart — where the customer
     left it. If the browser blocks that, this tab goes to WhatsApp instead. */
  function openWhatsApp(url) {
    var win = null;
    try { win = window.open(url, '_blank', 'noopener'); } catch (e) {}
    if (!win) { location.href = url; return false; }
    return true;
  }

  /* --------------------------------------------------- checkout: details step */
  (function () {
    var form = document.querySelector('[data-checkout-form]');
    if (!form) return;

    var d = details();
    FIELDS.forEach(function (f) {
      var els = form.querySelectorAll('[name="' + f + '"]');
      if (!els.length || !d[f]) return;
      if (els[0].type === 'radio') {
        els.forEach(function (r) { r.checked = r.value === d[f]; });
      } else {
        els[0].value = d[f];
      }
    });

    function persist() {
      var next = details();
      FIELDS.forEach(function (f) {
        var els = form.querySelectorAll('[name="' + f + '"]');
        if (!els.length) return;
        if (els[0].type === 'radio') {
          var on = form.querySelector('[name="' + f + '"]:checked');
          next[f] = on ? on.value : '';
        } else {
          next[f] = els[0].value;
        }
      });
      C.write(K.details, next);
    }
    form.addEventListener('input', persist);
    form.addEventListener('change', persist);

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      persist();
      location.href = 'checkout-payment.html';
    });

    var next = document.querySelector('[data-checkout-continue]');
    if (next) next.addEventListener('click', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      persist();
      location.href = 'checkout-payment.html';
    });
  })();

  /* --------------------------------------------------- checkout: review step */
  (function () {
    var btn = document.querySelector('[data-whatsapp-checkout]');
    if (!btn) return;

    /* Echo what the customer entered, so the last screen before WhatsApp
       shows the details the message will carry. */
    var d = details();
    var map = {
      name: fullName(d), phone: d.phone, email: d.email,
      area: [d.city, d.province].filter(Boolean).join(', '),
      address: d.street + (d.postal ? ', ' + d.postal : ''),
      notes: d.notes
    };
    Object.keys(map).forEach(function (k) {
      document.querySelectorAll('[data-review="' + k + '"]').forEach(function (el) {
        el.textContent = map[k] || '—';
      });
    });

    /* The items exactly as they will appear in the WhatsApp message. */
    var reviewRows = document.querySelector('[data-review-rows]');
    if (reviewRows) {
      var items = C.cart.all();
      reviewRows.innerHTML = items.length ? items.map(function (i) {
        var lineTotal = i.price === null || i.price === undefined ? null : i.price * i.qty;
        return '<tr><td class="linetable__prod">' +
          (i.img ? '<img class="ph-img" src="' + i.img + '" alt="' + i.name + '" loading="lazy" decoding="async"/>' : '') +
          '<div><strong>' + i.name + '</strong><small>' + i.brand +
          (i.variant ? ' · ' + i.variant : '') + ' · Qty ' + i.qty + '</small></div></td>' +
          '<td style="text-align:right">' + C.money(lineTotal) + '</td></tr>';
      }).join('') : '<tr><td>Your cart is empty.</td><td></td></tr>';
    }

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (!C.cart.all().length) { C.toast('Your cart is empty.'); return; }
      if (!detailsComplete(details())) {
        C.toast('Please complete your delivery details first.');
        location.href = 'checkout-billing.html';
        return;
      }
      var order = createOrder();
      var url = waUrl(order);
      C.track('whatsapp_checkout_click', {
        order_reference: order.ref, items: order.items.length
      });
      /* Posted before the tab may navigate, so the owner is alerted even if
         the customer abandons the WhatsApp draft. */
      submitOrder(order);
      /* The cart is deliberately left intact — it is cleared only when the
         customer confirms on the next page that the message was sent. */
      if (openWhatsApp(url)) location.href = 'order-completed.html';
    });
  })();

  /* ------------------------------------------------------ order completed page */
  (function () {
    var root = document.querySelector('[data-order-complete]');
    if (!root) return;

    var order = findOrder(C.read(K.last, ''));
    var rows = root.querySelector('[data-order-rows]');

    function paint() {
      if (!order) {
        root.querySelectorAll('[data-order="ref"]').forEach(function (el) {
          el.textContent = '—';
        });
        if (rows) rows.innerHTML = '<tr><td>No recent order found on this device.</td><td></td></tr>';
        return;
      }
      var fields = {
        ref: order.ref,
        status: order.status,
        payment: order.paymentMethod,
        total: order.subtotal === null || order.subtotal === undefined
          ? (CFG.tbc || 'To be confirmed') : C.money(order.subtotal),
        delivery: CFG.tbc || 'To be confirmed'
      };
      Object.keys(fields).forEach(function (k) {
        root.querySelectorAll('[data-order="' + k + '"]').forEach(function (el) {
          el.textContent = fields[k];
        });
      });

      if (rows) {
        rows.innerHTML = order.items.map(function (i) {
          var lineTotal = i.price === null || i.price === undefined
            ? null : i.price * i.qty;
          return '<tr><td class="linetable__prod">' +
            (i.img ? '<img class="ph-img" src="' + i.img + '" alt="' + i.name + '" loading="lazy" decoding="async"/>' : '') +
            '<div><strong>' + i.name + '</strong><small>' + i.brand +
            ' · Qty ' + i.qty + '</small></div></td>' +
            '<td style="text-align:right">' + C.money(lineTotal) + '</td></tr>';
        }).join('') +
        '<tr><td>Delivery</td><td style="text-align:right">' + (CFG.tbc || 'To be confirmed') + '</td></tr>' +
        '<tr class="linetable__total"><td>Subtotal</td><td style="text-align:right">' +
          (order.subtotal === null || order.subtotal === undefined
            ? (CFG.tbc || 'To be confirmed') : C.money(order.subtotal)) + '</td></tr>';
      }
    }

    var again = root.querySelector('[data-whatsapp-resend]');
    if (again) again.addEventListener('click', function (e) {
      e.preventDefault();
      if (!order) return;
      openWhatsApp(waUrl(order));
    });

    var done = root.querySelector('[data-order-sent]');
    if (done) done.addEventListener('click', function (e) {
      e.preventDefault();
      if (!order) return;
      setStatus(order.ref, STATUS.awaiting);
      order.status = STATUS.awaiting;
      C.cart.clear();
      paint();
      done.hidden = true;
      var ack = root.querySelector('[data-order-ack]');
      if (ack) ack.hidden = false;
    });

    paint();
  })();

  /* ------------------------------------------------------- order status page */
  (function () {
    var root = document.querySelector('[data-order-status]');
    if (!root) return;

    var ref = new URLSearchParams(location.search).get('ref') || C.read(K.last, '');
    var order = findOrder(ref);

    root.querySelectorAll('[data-order="ref"]').forEach(function (el) {
      el.textContent = order ? order.ref : '—';
    });
    root.querySelectorAll('[data-order="status"]').forEach(function (el) {
      el.textContent = order ? order.status : 'No order found on this device';
    });

    var reached = order ? TIMELINE.indexOf(order.status) : -1;
    /* Statuses that are not milestones still sit after the payment step. */
    if (order && reached === -1) reached = 1;
    root.querySelectorAll('[data-step-index]').forEach(function (li) {
      var i = parseInt(li.getAttribute('data-step-index'), 10);
      li.classList.toggle('is-done', i <= reached);
    });

    var rows = root.querySelector('[data-order-rows]');
    if (rows) {
      rows.innerHTML = order && order.items.length
        ? order.items.map(function (i) {
            return '<tr><td class="linetable__prod">' +
              (i.img ? '<img class="ph-img" src="' + i.img + '" alt="' + i.name + '" loading="lazy" decoding="async"/>' : '') +
              '<div><strong>' + i.name + '</strong><small>' + i.brand + ' · Qty ' + i.qty +
              '</small></div></td></tr>';
          }).join('')
        : '<tr><td>Enter your order reference on the Track Your Order page.</td></tr>';
    }
  })();

  /* -------------------------------------------------------- track order page */
  (function () {
    var form = document.querySelector('[data-track-form]');
    if (!form) return;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ref = form.querySelector('[name="ref"]').value.trim();
      if (!findOrder(ref)) {
        C.toast('No order with that reference was placed on this device. Message us on WhatsApp and we will check it for you.');
        return;
      }
      location.href = 'order-status.html?ref=' + encodeURIComponent(ref);
    });
  })();

  /* ------------------------------------------------------- account: my orders */
  (function () {
    var list = document.querySelector('[data-orders-list]');
    if (!list) return;
    var empty = document.querySelector('[data-orders-empty]');
    var all = orders();
    if (!all.length) { if (empty) empty.hidden = false; list.hidden = true; return; }
    if (empty) empty.hidden = true;
    list.innerHTML = all.map(function (o) {
      var when = new Date(o.created).toLocaleDateString('en-ZA',
        { year: 'numeric', month: 'short', day: 'numeric' });
      return '<tr><td data-label="Order"><strong>' + o.ref + '</strong>' +
        '<small style="display:block;color:var(--muted)">' + when + '</small></td>' +
        '<td data-label="Items">' + o.items.reduce(function (n, i) { return n + i.qty; }, 0) + '</td>' +
        '<td data-label="Status">' + o.status + '</td>' +
        '<td style="text-align:right"><a class="btn btn--white btn--sm" href="order-status.html?ref=' +
          encodeURIComponent(o.ref) + '">View</a></td></tr>';
    }).join('');
  })();

  window.CassaroCheckout = {
    STATUS: STATUS, makeRef: makeRef, buildMessage: buildMessage,
    waUrl: waUrl, orders: orders, findOrder: findOrder, setStatus: setStatus
  };
})();
