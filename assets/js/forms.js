/* Cassaro Beauty — the forms that talk to a person.
   -------------------------------------------------------------------------
   Contact enquiries, newsletter signups and product reviews all post to the
   same endpoint. Before this they cleared themselves and claimed to have sent
   something, which is worse than no form: the customer walks away believing
   they made contact.

   Every form here degrades honestly. If the request fails the customer is
   told so and given the WhatsApp number, rather than being thanked for a
   message nobody received.
   ------------------------------------------------------------------------- */
(function () {
  'use strict';

  var CFG = window.CASSARO_CONFIG || {};
  var ENDPOINT = CFG.messageEndpoint;

  function feedback(form, message, ok) {
    var el = form.querySelector('[data-form-status]');
    if (!el) {
      el = document.createElement('p');
      el.setAttribute('data-form-status', '');
      form.appendChild(el);
    }
    el.className = 'formstatus ' + (ok ? 'is-ok' : 'is-error');
    el.textContent = message;
    el.hidden = false;
    /* Announced by screen readers without stealing focus mid-typing. */
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
  }

  function fallbackNumber() {
    return CFG.whatsappDisplay || CFG.whatsappNumber || '';
  }

  function submit(form, payload, successText) {
    var button = form.querySelector('button[type="submit"], button:not([type])');
    var label = button ? button.textContent : '';
    if (button) { button.disabled = true; button.textContent = 'Sending…'; }

    var headers = { 'Content-Type': 'application/json' };
    if (CFG.orderEndpointKey) {
      headers.apikey = CFG.orderEndpointKey;
      headers.Authorization = 'Bearer ' + CFG.orderEndpointKey;
    }

    return fetch(ENDPOINT, { method: 'POST', headers: headers, body: JSON.stringify(payload) })
      .then(function (res) { return res.json().catch(function () { return {}; }).then(function (b) { return { res: res, body: b }; }); })
      .then(function (r) {
        if (!r.res.ok || !r.body.ok) {
          throw new Error(r.body.error || 'That did not go through.');
        }
        form.reset();
        feedback(form, r.body.already ? 'You are already on the list.' : successText, true);
      })
      .catch(function (err) {
        feedback(form,
          (err.message || 'Something went wrong.') +
          ' You can also reach us on WhatsApp at ' + fallbackNumber() + '.', false);
      })
      .then(function () {
        if (button) { button.disabled = false; button.textContent = label; }
      });
  }

  function value(form, name) {
    var el = form.querySelector('[name="' + name + '"]');
    return el ? el.value.trim() : '';
  }

  /* ------------------------------------------------------------ contact */
  document.querySelectorAll('[data-contact-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      submit(form, {
        kind: 'contact',
        name: [value(form, 'firstName'), value(form, 'lastName')].filter(Boolean).join(' '),
        email: value(form, 'email'),
        phone: value(form, 'phone'),
        subject: value(form, 'subject'),
        message: value(form, 'message'),
        website: value(form, 'website')
      }, 'Thank you. We have your message and will reply shortly.');
    });
  });

  /* --------------------------------------------------------- newsletter */
  document.querySelectorAll('[data-subscribe-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      submit(form, {
        kind: 'subscribe',
        email: value(form, 'email'),
        website: value(form, 'website')
      }, 'Thank you for subscribing.');
    });
  });

  /* ------------------------------------------------------------- review */
  document.querySelectorAll('[data-review-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      submit(form, {
        kind: 'review',
        name: value(form, 'name'),
        email: value(form, 'email'),
        product: form.getAttribute('data-review-form') || document.title,
        subject: value(form, 'subject'),
        rating: Number(value(form, 'rating')) || null,
        message: value(form, 'message'),
        website: value(form, 'website')
      }, 'Thank you for your review. Our team reads every one before it is published.');
    });
  });
})();
