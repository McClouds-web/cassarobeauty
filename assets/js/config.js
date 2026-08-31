/* Cassaro Beauty — single place for the values the ordering flow depends on.
   Nothing else in the site should hard-code a WhatsApp number or a currency. */
window.CASSARO_CONFIG = {
  /* WhatsApp number in international format, digits only, no + and no spaces.
     This is the number already published in the header, footer and Contact
     page. Change it HERE and the whole ordering flow follows. */
  whatsappNumber: '27690634793',

  /* The same number as it is written on screen. build.py reads both values
     from this file, so the header, drawer, footer and contact page cannot
     drift out of step with the number the ordering flow actually uses. */
  whatsappDisplay: '+27 69 063 4793',

  storeName: 'Cassaro Beauty',

  /* Order references look like CAS-483920. */
  orderPrefix: 'CAS-',

  currencySymbol: 'R',

  /* Shown wherever a real price is not available yet. The site's own
     placeholder is R___, so the two agree on screen. */
  pricePlaceholder: 'R___',

  /* Wording used when an amount has not been established. */
  tbc: 'To be confirmed',

  /* Where the order is recorded and the owner alert is raised. The endpoint
     is a Supabase edge function; the key below is the project's publishable
     key, which is safe in a static page — the orders table is unreadable
     without the service role. Leave orderEndpoint empty to disable the
     backend and fall back to the WhatsApp draft alone. */
  orderEndpoint: 'https://cijeetlvkellnsqhsuxo.supabase.co/functions/v1/cassaro_order',

  /* Contact enquiries, newsletter signups and product reviews. Same project,
     same publishable key; the endpoint decides what to do with each kind. */
  messageEndpoint: 'https://cijeetlvkellnsqhsuxo.supabase.co/functions/v1/cassaro_message',
  orderEndpointKey: 'sb_publishable_5NYstW3JOY7b270BbZM-Kg_A6QNcM9V'
};
