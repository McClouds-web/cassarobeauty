/* Cassaro Beauty — single place for the values the ordering flow depends on.
   Nothing else in the site should hard-code a WhatsApp number or a currency. */
window.CASSARO_CONFIG = {
  /* WhatsApp number in international format, digits only, no + and no spaces.
     This is the number already published in the header, footer and Contact
     page. Change it HERE and the whole ordering flow follows. */
  whatsappNumber: '27765222387',

  storeName: 'Cassaro Beauty',

  /* Order references look like CAS-483920. */
  orderPrefix: 'CAS-',

  currencySymbol: 'R',

  /* Shown wherever a real price is not available yet. The site's own
     placeholder is R___, so the two agree on screen. */
  pricePlaceholder: 'R___',

  /* Wording used when an amount has not been established. */
  tbc: 'To be confirmed'
};
