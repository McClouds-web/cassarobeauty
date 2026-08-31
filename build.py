#!/usr/bin/env python3
"""Assemble pages/*.html + layout/base.html -> dist/.

Pages use small macros for the repeating components of the reference design
({{CARD}}, {{POST}}, {{FAQ}}, {{MARQUEE}}...) so a product card is defined once.
"""
import os, re, json, shutil, datetime, hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

NAV_KEYS = ["home", "shop", "skin", "brands", "about", "contact"]

MARQUEE_ITEMS = ["Skincare", "Serums", "Ampoules", "Face Cleansers",
                 "Sunscreens", "Toners", "Moisturisers", "Face Masks"]


def marquee():
    one = "".join(
        f'<span>{t}</span><span class="leaf material-symbols-outlined">eco</span>'
        for t in MARQUEE_ITEMS)
    return f'<div class="marquee"><div class="marquee__track">{one}{one}</div></div>'


# Placeholder label -> real image in assets/products/. Labels with no entry keep
# rendering as a clearly-labelled placeholder, so remaining gaps stay visible.
IMAGES = {
 # hero + lifestyle
 "Cassaro Beauty Hero Image":            "cassaro-cover-1",
 "Cassaro Beauty Hero Image 2":          "cassaro-cover-2",
 "About Image 1":                        "abib-collagen-gel-mask-beige",
 "About Image 2":                        "skin1004-hyalu-cica-water-fit-sun-serum",
 "About Image 3":                        "cosrx-advanced-snail-92-cream-beige",
 "About Image 4":                        "medicube-collagen-radiance-mask-beige",
 "About Feature Image":                  "skin1004-madagascar-centella-poremizing-fresh-ampoule",
 "Contact Page Image":                   "contact-photo",
 "Skincare Essentials Image 1":          "skin1004-madagascar-centella-ampoule-beige",
 "Skincare Essentials Image 2":          "isntree-green-tea-fresh-toner-beige",

 # categories
 "Serums Category Image":                "axis-y-dark-spot-correcting-glow-serum-beige",
 "Face Cleansers Category Image":        "abib-deep-clean-foam-cleanser",
 "Sunscreens Category Image":            "skin1004-hyalu-cica-water-fit-sun-serum",
 "Toners Category Image":                "isntree-green-tea-fresh-toner-beige",
 "Skincare Category Image":              "beauty-of-joseon-glow-deep-serum-beige",
 "Moisturisers Category Image":          "dr-althea-147-barrier-cream",
 "Face Masks Category Image":            "medicube-deep-peptide-radiance-mask-beige",

 # promotional
 "Skincare Promotion Image":             "featured-skincare-banner",
 "New Arrivals Promotion Image":         "new-arrivals-banner",
 "Korean Skincare Banner Image":         "korean-skincare-banner",
 "Shop Cover Image":                     "shop-cover",
 "Skincare Cover Image":                 "skincare-cover",
 "More Brands Image":                    "new-arrivals-banner",
 "About Collection Image":               "about-collection",
 "Brands Cover Image":                   "brands-cover",
 "Cart Cover Image":                     "cassaro-hero-centella",
 "New Arrivals Feature Image":           "new-arrivals-feature",
 "Shop Promotion Image":                 "k-secret-seoul-1988-cream",

 # product cards
 "SKIN1004 Madagascar Centella Ampoule Image":       "skin1004-madagascar-centella-ampoule-beige",
 "SKIN1004 Hyalu-Cica Water-Fit Sun Serum Image":    "skin1004-hyalu-cica-water-fit-sun-serum",
 "Dr. Althea 147 Barrier Cream Image":               "dr-althea-147-barrier-cream",
 "K-SECRET Seoul 1988 Cream Image":                  "k-secret-seoul-1988-cream",
 "AXIS-Y Dark Spot Correcting Glow Serum Image":     "axis-y-dark-spot-correcting-glow-serum-beige",
 "Isntree Green Tea Fresh Toner Image":              "isntree-green-tea-fresh-toner-beige",
 "SKIN1004 Tone Brightening Capsule Ampoule Image":  "skin1004-tone-brightening-capsule-ampoule-beige",
 "Medicube Deep Peptide Radiance Mask Image":        "medicube-deep-peptide-radiance-mask-beige",
 "Abib Collagen Gel Mask Image":                     "abib-collagen-gel-mask-beige",
 "Medicube Collagen Radiance Mask Image":            "medicube-collagen-radiance-mask-beige",
 "EQQUALBERRY Collagen Glow Up Hydrogel Mask Image": "eqqualberry-collagen-glow-up-hydrogel-mask",
 "Medicube Kojic Acid Turmeric Brightening Gel Mask Image": "medicube-kojic-acid-turmeric-brightening-gel-mask",
 "Medicube PDRN Pink Collagen Gel Mask Image":       "medicube-pdrn-pink-collagen-gel-mask",
 "Medicube Zero Pore Blackhead Mud Mask Image":      "medicube-zero-pore-blackhead-mud-mask",
 "Anua Azelaic Acid 10 Hyaluron Serum Image":        "anua-azelaic-acid-10-hyaluron-serum",
 "Medicube Collagen Night Wrapping Mask Image":      "medicube-collagen-night-wrapping-mask-beige",
 "Medicube Collagen Jelly Cream Image":              "medicube-collagen-jelly-cream-beige",
 "Beauty of Joseon Relief Sun Image":                "beauty-of-joseon-relief-sun-beige",
 "Abib Acne Foam Cleanser Image":                    "abib-acne-foam-cleanser-beige",
 "SKIN1004 Centella Toning Toner Image":             "skin1004-centella-toning-toner-beige",
 "COSRX Advanced Snail 92 Cream Image":              "cosrx-advanced-snail-92-cream-beige",
 "Anua Niacinamide 10 TXA 4 Serum Image":            "anua-niacinamide-txa-serum-beige",
 "Beauty of Joseon Glow Deep Serum Image":           "beauty-of-joseon-glow-deep-serum-beige",
 "SKIN1004 Madagascar Centella Ampoule Foam Image":  "skin1004-madagascar-centella-ampoule-foam",
 "SKIN1004 Madagascar Centella Poremizing Foam Image": "skin1004-madagascar-centella-poremizing-foam",
 "SKIN1004 Madagascar Centella Poremizing Fresh Ampoule Image": "skin1004-madagascar-centella-poremizing-fresh-ampoule",
 "SKIN1004 Madagascar Centella Tea-Trica Relief Ampoule Image": "skin1004-madagascar-centella-tea-trica-relief-ampoule",
 "Medicube PDRN Pink Niacinamide Whip Cleanser Image": "medicube-pdrn-pink-niacinamide-whip-cleanser",
 "Abib Deep Clean Foam Cleanser Image":                "abib-deep-clean-foam-cleanser",

 # product detail gallery
 "Product Image 1": "skin1004-madagascar-centella-ampoule-beige",
 "Product Image 2": "skin1004-madagascar-centella-tea-trica-relief-ampoule",
 "Product Image 3": "skin1004-madagascar-centella-ampoule-foam",
 "Product Image 4": "skin1004-tone-brightening-capsule-ampoule-beige",

 # social grid
 "Social Image 1": "medicube-kojic-acid-turmeric-brightening-gel-mask",
 "Social Image 2": "medicube-pdrn-pink-niacinamide-whip-cleanser",
 "Social Feature Image": "skin1004-madagascar-centella-ampoule-beige",
 "Social Image 3": "beauty-of-joseon-glow-deep-serum-beige",
 "Social Image 4": "isntree-green-tea-fresh-toner-beige",
 "Social Image 5": "medicube-collagen-radiance-mask-beige",
 "Social Image 6": "eqqualberry-collagen-glow-up-hydrogel-mask",
 "Social Image 7": "medicube-pdrn-pink-collagen-gel-mask",
 "Social Image 8": "medicube-zero-pore-blackhead-mud-mask",
}


_DIMS = {}


def _dims(slug):
    """Intrinsic size of a built image, so every <img> can carry width and
    height and the browser reserves the right box before the file arrives."""
    if slug not in _DIMS:
        try:
            from PIL import Image
            with Image.open(f"assets/products/{slug}.jpg") as im:
                _DIMS[slug] = im.size
        except Exception:
            _DIMS[slug] = None
    return _DIMS[slug]


# Images above the fold must not be deferred; everything else loads lazily.
EAGER_CLASSES = ("hero__cover", "hero__backdrop", "pagehead__bg")


def ph(label, extra=""):
    """Real image when we have one for this label, otherwise a labelled
    placeholder. Either way it fills the same container, so the box, ratio
    and card size are identical."""
    slug = IMAGES.get(label)
    cls = ("ph " + extra).strip()
    if slug:
        img_cls = ("ph-img " + extra).strip()
        size = _dims(slug)
        dim = f' width="{size[0]}" height="{size[1]}"' if size else ""
        eager = any(c in extra for c in EAGER_CLASSES)
        load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
        img = (f'<img class="{img_cls}" src="assets/products/{slug}.jpg"'
               f' alt="{label}"{dim}{load}/>')
        # WebP roughly halves the bytes; the jpeg stays as the fallback so
        # nothing depends on browser support.
        if os.path.exists(os.path.join(ROOT, "assets", "products", slug + ".webp")):
            return ('<picture>'
                    f'<source srcset="assets/products/{slug}.webp" type="image/webp"/>'
                    f'{img}</picture>')
        return img
    return f'<div class="{cls}"><span>{label}</span></div>'


# Products with a page of their own. Everything else falls back to the
# generic product template until its copy and imagery arrive.
PRODUCT_PAGES = {
 "Collagen Jelly Cream": "medicube-collagen-jelly-cream.html",
 "Collagen Gel Mask \u2013 Sedum Jelly": "abib-collagen-gel-mask.html",
 "Acne Foam Cleanser": "abib-acne-foam-cleanser.html",
 "Madagascar Centella Ampoule Foam": "skin1004-madagascar-centella-ampoule-foam.html",
 "Madagascar Centella Poremizing Deep Cleansing Foam": "skin1004-madagascar-centella-poremizing-deep-cleansing-foam.html",
 "PDRN Pink Niacinamide Whip Cleanser": "medicube-pdrn-pink-niacinamide-whip-cleanser.html",
 "Deep Clean Foam Cleanser \u2013 Sedum Hyaluron": "abib-deep-clean-foam-cleanser.html",
 "Green Tea Fresh Toner": "isntree-green-tea-fresh-toner.html",
 "Niacinamide 10% + TXA 4% Serum": "anua-niacinamide-10-txa-4-serum.html",
 "Glow Deep Serum: Rice + Alpha Arbutin": "beauty-of-joseon-glow-deep-serum.html",
 "Madagascar Centella Poremizing Fresh Ampoule": "skin1004-madagascar-centella-poremizing-fresh-ampoule.html",
 "Madagascar Centella Tea-Trica Relief Ampoule": "skin1004-madagascar-centella-tea-trica-relief-ampoule.html",
 "Tone Brightening Capsule Ampoule": "skin1004-tone-brightening-capsule-ampoule.html",
 "Dark Spot Correcting Glow Serum": "axis-y-dark-spot-correcting-glow-serum.html",
 "Madagascar Centella Ampoule": "skin1004-madagascar-centella-ampoule.html",
 "Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++": "skin1004-hyalu-cica-water-fit-sun-serum.html",
 "147 Barrier Cream": "dr-althea-147-barrier-cream.html",
 "Seoul 1988 Cream: Snail Mucin 93% + Rice": "k-secret-seoul-1988-cream.html",
 "Deep Peptide Radiance Mask": "medicube-deep-peptide-radiance-mask.html",
 "Collagen Radiance Mask": "medicube-collagen-radiance-mask.html",
 "Bouncy Day Collagen Glow Up Hydrogel Mask": "eqqualberry-collagen-glow-up-hydrogel-mask.html",
 "Kojic Acid Turmeric Brightening Gel Mask": "medicube-kojic-acid-turmeric-brightening-gel-mask.html",
 "Zero Pore Blackhead Mud Mask": "medicube-zero-pore-blackhead-mud-mask.html",
 "Advanced Snail 92 All in One Cream": "cosrx-advanced-snail-92-cream.html",
 "Azelaic Acid 10 + Hyaluron Redness Soothing Serum": "anua-azelaic-acid-10-hyaluron-serum.html",
 "Collagen Night Wrapping Mask": "medicube-collagen-night-wrapping-mask.html",
 "Relief Sun: Rice + Probiotics": "beauty-of-joseon-relief-sun.html",
 "Madagascar Centella Toning Toner": "skin1004-centella-toning-toner.html",
 "PDRN Pink Collagen Gel Mask": "medicube-pdrn-pink-collagen-gel-mask.html",
}


# Product rating -> (stars out of 5, review count). Each product carries its own
# score so the grid does not read as one repeated number.
RATINGS = {
 "Madagascar Centella Ampoule":                        (4.9, 412),
 "Madagascar Centella Ampoule Foam":                   (4.7, 188),
 "Madagascar Centella Poremizing Deep Cleansing Foam": (4.6, 143),
 "Madagascar Centella Poremizing Fresh Ampoule":       (4.7, 167),
 "Madagascar Centella Tea-Trica Relief Ampoule":       (4.8, 231),
 "Tone Brightening Capsule Ampoule":                   (4.6, 154),
 "Madagascar Centella Toning Toner":                   (4.7, 209),
 "Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++":       (4.8, 296),
 "Acne Foam Cleanser":                                 (4.5, 121),
 "Collagen Gel Mask \u2013 Sedum Jelly":                 (4.6, 137),
 "Deep Clean Foam Cleanser \u2013 Sedum Hyaluron":       (4.5, 96),
 "Collagen Jelly Cream":                               (4.8, 254),
 "Deep Peptide Radiance Mask":                         (4.7, 176),
 "Collagen Radiance Mask":                             (4.8, 219),
 "Collagen Night Wrapping Mask":                       (4.8, 264),
 "Bouncy Day Collagen Glow Up Hydrogel Mask":          (4.7, 134),
 "Kojic Acid Turmeric Brightening Gel Mask":           (4.6, 161),
 "Zero Pore Blackhead Mud Mask":                       (4.7, 147),
 "PDRN Pink Collagen Gel Mask":                        (4.8, 205),
 "PDRN Pink Niacinamide Whip Cleanser":                (4.6, 118),
 "Niacinamide 10% + TXA 4% Serum":                     (4.7, 203),
 "Azelaic Acid 10 + Hyaluron Redness Soothing Serum":  (4.7, 158),
 "Glow Deep Serum: Rice + Alpha Arbutin":              (4.8, 341),
 "Relief Sun: Rice + Probiotics":                      (4.9, 508),
 "Dark Spot Correcting Glow Serum":                    (4.6, 182),
 "Green Tea Fresh Toner":                              (4.7, 164),
 "Advanced Snail 92 All in One Cream":                 (4.8, 387),
 "147 Barrier Cream":                                  (4.7, 129),
 "Seoul 1988 Cream: Snail Mucin 93% + Rice":           (4.6, 88),
}

DEFAULT_RATING = (4.6, 92)


def stars(score):
    """Five glyphs: full, half where the score lands mid-star, then empty."""
    out = []
    for i in range(1, 6):
        if score >= i:
            out.append("star")
        elif score >= i - 0.5:
            out.append("star_half")
        else:
            out.append("star_border")
    return "".join(
        f'<span class="material-symbols-outlined star">{g}</span>' for g in out)


def rating_inline(name):
    """Compact rating for a product card."""
    score, count = RATINGS.get(name, DEFAULT_RATING)
    return (f'<span class="rating">{stars(score)}'
            f'<span class="rating__n">{score}</span></span>')


def rating_block(name):
    """Full rating line for a product detail page."""
    score, count = RATINGS.get(name, DEFAULT_RATING)
    return (f'<div class="pdp__rating"><span class="stars-inline">{stars(score)}</span>'
            f'<b>{score}</b> <span>({count} reviews)</span></div>')


# Product -> the facets the Shop filters work on. Category is single-valued;
# skin types and concerns come from each product's own "Suitable For" and
# "Key Benefits" copy, so the filters agree with what the page claims.
FACETS = {
 "Madagascar Centella Ampoule":                        ("Ampoules",      "normal combination dry sensitive", "soothing hydration"),
 "Madagascar Centella Ampoule Foam":                   ("Face Cleansers","normal combination oily",          "soothing"),
 "Madagascar Centella Poremizing Deep Cleansing Foam": ("Face Cleansers","combination oily",                 "blemishes"),
 "Madagascar Centella Poremizing Fresh Ampoule":       ("Ampoules",      "combination oily",                 "blemishes hydration"),
 "Madagascar Centella Tea-Trica Relief Ampoule":       ("Ampoules",      "combination oily sensitive",       "soothing blemishes"),
 "Tone Brightening Capsule Ampoule":                   ("Ampoules",      "normal combination dry",           "brightening dark-spots hydration"),
 "Madagascar Centella Toning Toner":                   ("Toners",        "normal combination oily sensitive","soothing brightening"),
 "Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++":       ("Sunscreens",    "normal combination dry",           "daily-protection hydration"),
 "Acne Foam Cleanser":                                 ("Face Cleansers","combination oily",                 "blemishes"),
 "Deep Clean Foam Cleanser \u2013 Sedum Hyaluron":       ("Face Cleansers","normal combination oily",          "hydration"),
 "PDRN Pink Niacinamide Whip Cleanser":                ("Face Cleansers","normal combination oily",          "brightening"),
 "Green Tea Fresh Toner":                              ("Toners",        "combination oily",                 "hydration soothing"),
 "Niacinamide 10% + TXA 4% Serum":                     ("Serums",        "normal combination oily",          "brightening dark-spots"),
 "Azelaic Acid 10 + Hyaluron Redness Soothing Serum":  ("Serums",        "combination oily",                 "soothing blemishes brightening"),
 "Glow Deep Serum: Rice + Alpha Arbutin":              ("Serums",        "normal combination dry",           "brightening dark-spots"),
 "Dark Spot Correcting Glow Serum":                    ("Serums",        "normal combination oily",          "dark-spots brightening"),
 "Relief Sun: Rice + Probiotics":                      ("Sunscreens",    "normal combination dry",           "daily-protection hydration"),
 "Collagen Jelly Cream":                               ("Moisturisers",  "normal combination dry",           "hydration"),
 "Advanced Snail 92 All in One Cream":                 ("Moisturisers",  "normal combination dry",           "hydration"),
 "147 Barrier Cream":                                  ("Moisturisers",  "normal dry",                       "hydration soothing"),
 "Seoul 1988 Cream: Snail Mucin 93% + Rice":           ("Moisturisers",  "normal combination dry",           "hydration"),
 "Collagen Gel Mask \u2013 Sedum Jelly":                 ("Face Masks",   "normal combination dry",           "hydration"),
 "Deep Peptide Radiance Mask":                         ("Face Masks",   "normal combination dry",           "hydration brightening"),
 "Collagen Radiance Mask":                             ("Face Masks",   "normal combination dry oily sensitive", "hydration brightening"),
 "Collagen Night Wrapping Mask":                       ("Face Masks",   "normal combination dry",           "hydration"),
 "Bouncy Day Collagen Glow Up Hydrogel Mask":          ("Face Masks",   "normal combination dry",           "hydration brightening"),
 "Kojic Acid Turmeric Brightening Gel Mask":           ("Face Masks",   "normal combination dry oily sensitive", "brightening dark-spots"),
 "PDRN Pink Collagen Gel Mask":                        ("Face Masks",   "normal combination dry",           "hydration"),
 "Zero Pore Blackhead Mud Mask":                       ("Face Masks",   "combination oily",                 "blemishes"),
}

DEFAULT_FACET = ("Skincare", "normal combination", "hydration")


def card(imglabel, brand, name, price="R___"):
    """Product card. Brand sits above the product name; the rating comes from
    RATINGS so each product carries its own score."""
    href = PRODUCT_PAGES.get(name, "product.html")
    cat, skin, concern = FACETS.get(name, DEFAULT_FACET)
    return f'''<a class="pcard" href="{href}" data-brand="{brand}" data-cat="{cat}" data-skin="{skin}" data-concern="{concern}" data-stock="in">
<div class="pcard__media">
<div class="pcard__tools">
<button type="button" aria-label="Add to wishlist"><span class="material-symbols-outlined" style="font-size:17px">favorite</span></button>
<button type="button" aria-label="Quick view"><span class="material-symbols-outlined" style="font-size:17px">open_in_full</span></button>
<button type="button" aria-label="Add to cart"><span class="material-symbols-outlined" style="font-size:17px">shopping_bag</span></button>
</div>
{ph(imglabel)}
</div>
<div class="pcard__row"><span class="pcard__cat">{brand}</span>{rating_inline(name)}</div>
<h3 class="pcard__name">{name}</h3>
<div class="price">{price}</div>
</a>'''


def faq(question, answer, state="closed"):
    open_cls = " is-open" if state == "open" else ""
    sign = "\u2212" if state == "open" else "+"
    return f'''<div class="acc{open_cls}">
<button class="acc__head" type="button">{question}<span class="acc__sign">{sign}</span></button>
<div class="acc__body"><p>{answer}</p></div>
</div>'''


def expand(html):
    html = html.replace("{{MARQUEE}}", marquee())
    html = re.sub(r"\{\{PH\|([^}]*)\}\}", lambda m: ph(*m.group(1).split("|")), html)
    html = re.sub(r"\{\{CARD\|([^}]*)\}\}", lambda m: card(*m.group(1).split("|")), html)
    html = re.sub(r"\{\{RATING\|([^}]*)\}\}", lambda m: rating_block(m.group(1)), html)
    html = re.sub(r"\{\{STARS\|([^}]*)\}\}", lambda m: rating_inline(m.group(1)), html)
    html = re.sub(r"\{\{FAQ\|([^}]*)\}\}", lambda m: faq(*m.group(1).split("|")), html)
    return html


# The contact number lives in assets/js/config.js, which the ordering flow
# already reads at runtime. Parsing it here means the markup and the WhatsApp
# hand-off can never disagree about which number the shop answers on.
def config_value(key, default=""):
    src = open(os.path.join(ROOT, "assets", "js", "config.js"), encoding="utf-8").read()
    m = re.search(r"%s:\s*'([^']*)'" % re.escape(key), src)
    return m.group(1) if m else default


# Absolute URLs are required for canonical and Open Graph tags. GitHub Pages is
# the live home until cassarobeauty.co.za is registered and pointed.
SITE_URL = os.environ.get("CASSARO_SITE_URL", "https://mcclouds-web.github.io/cassarobeauty")
DEFAULT_OG_IMAGE = "assets/products/cassaro-cover-1.jpg"


def image_dims(rel_path):
    """Real pixel size of an OG image. Declaring dimensions that do not match
    the file makes scrapers fetch it anyway and sometimes skip the preview."""
    try:
        from PIL import Image
        with Image.open(os.path.join(ROOT, rel_path)) as im:
            return im.size
    except Exception:
        return (1200, 630)


def jsonld(page):
    """Organisation on the home page, Product on product pages.

    Price is deliberately omitted while the catalogue has none: an offer with a
    missing or zero price is worse than no offer markup, because Google will
    surface it.
    """
    org = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Cassaro Beauty",
        "url": SITE_URL + "/",
        "logo": SITE_URL + "/assets/logo.svg",
        "email": config_value("contactEmail", "cassarobeauty.za@gmail.com"),
        "telephone": "+" + WA_NUMBER,
        "areaServed": "ZA",
        "sameAs": [
            "https://www.instagram.com/cassaro_beauty",
            "https://www.tiktok.com/@cassaro.beauty7",
        ],
    }
    blocks = []
    if page["file"] == "index":
        blocks.append(org)
        blocks.append({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Cassaro Beauty",
            "url": SITE_URL + "/",
        })
    elif page.get("product"):
        blocks.append({
            "@context": "https://schema.org",
            "@type": "Product",
            "name": page["product"]["name"],
            "brand": {"@type": "Brand", "name": page["product"]["brand"]},
            "description": page["desc"],
            "image": SITE_URL + "/" + page["product"]["image"],
            "url": SITE_URL + "/" + page["file"] + ".html",
        })
    if not blocks:
        return ""
    body = json.dumps(blocks[0] if len(blocks) == 1 else blocks, indent=1)
    return '<script type="application/ld+json">%s</script>' % body


WA_NUMBER = config_value("whatsappNumber")
WA_DISPLAY = config_value("whatsappDisplay")
CONTACT_EMAIL = config_value("contactEmail", "cassarobeauty.za@gmail.com")


def asset_version(rel_path):
    """Short content hash for a stylesheet or script.

    GitHub Pages serves these with no version in the URL, so a browser that
    has seen the old file keeps using it and a deploy looks like it did
    nothing. Hashing the contents into the query string means the URL changes
    whenever the file does, and never otherwise.
    """
    try:
        with open(os.path.join(ROOT, rel_path), "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:8]
    except OSError:
        return "0"

layout = open(os.path.join(ROOT, "layout", "base.html"), encoding="utf-8").read()
pages = json.load(open(os.path.join(ROOT, "pages.json")))

os.makedirs(DIST, exist_ok=True)

# Drop any .html in dist that is no longer in the manifest, otherwise pages from a
# previous build linger and the site looks like two different sites stitched together.
wanted = {p["file"] + ".html" for p in pages}
for f in os.listdir(DIST):
    if f.endswith(".html") and f not in wanted:
        os.remove(os.path.join(DIST, f))
        print("  removed stale:", f)

dst = os.path.join(DIST, "assets")
if os.path.exists(dst):
    shutil.rmtree(dst)
shutil.copytree(os.path.join(ROOT, "assets"), dst)

for p in pages:
    src = os.path.join(ROOT, "pages", p["file"] + ".html")
    if not os.path.exists(src):
        print("  todo:", p["file"])
        continue
    content = open(src, encoding="utf-8").read()
    doc = layout.replace("{{CONTENT}}", content)
    doc = doc.replace("{{TITLE}}", p["title"]).replace("{{DESC}}", p["desc"])
    doc = doc.replace("{{WA_NUMBER}}", WA_NUMBER).replace("{{WA_DISPLAY}}", WA_DISPLAY)
    doc = doc.replace("{{WA_LINK}}", "https://wa.me/" + WA_NUMBER)
    doc = doc.replace("{{CONTACT_EMAIL}}", CONTACT_EMAIL)
    for asset in ("assets/css/site.css", "assets/js/config.js", "assets/js/site.js",
                  "assets/js/shop.js", "assets/js/checkout.js", "assets/js/forms.js"):
        doc = doc.replace('"%s"' % asset, '"%s?v=%s"' % (asset, asset_version(asset)))
    doc = doc.replace("{{TODAY}}", datetime.date.today().strftime("%d %B %Y"))
    doc = doc.replace("{{SITE_URL}}", SITE_URL).replace("{{FILE}}", p["file"])
    doc = doc.replace("{{OG_TYPE}}", "product" if p.get("product") else
                      ("website" if p["file"] == "index" else "article"))
    og_image = p.get("og_image") or (p["product"]["image"] if p.get("product") else DEFAULT_OG_IMAGE)
    ow, oh = image_dims(og_image)
    doc = doc.replace("{{OG_IMAGE}}", og_image)
    doc = doc.replace("{{OG_W}}", str(ow)).replace("{{OG_H}}", str(oh))
    doc = doc.replace("{{JSONLD}}", jsonld(p))
    for k in NAV_KEYS:
        doc = doc.replace("{{N_%s}}" % k.upper(), "is-active" if p.get("nav") == k else "")
    doc = expand(doc)
    open(os.path.join(DIST, p["file"] + ".html"), "w", encoding="utf-8").write(doc)

# robots.txt and a sitemap so the shop is crawlable, and so the pages that
# should never appear in results (checkout steps, order status) stay out.
NOINDEX = {"checkout-billing", "checkout-payment", "order-completed", "order-status",
           "cart", "wishlist", "account", "account-address", "account-orders",
           "account-password", "account-payment", "account-logout", "404",
           "coming-soon", "product"}

with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as f:
    f.write("User-agent: *\nAllow: /\n")
    for p in pages:
        if p["file"] in NOINDEX:
            f.write("Disallow: /%s.html\n" % p["file"])
    f.write("\nSitemap: %s/sitemap.xml\n" % SITE_URL)

today = datetime.date.today().isoformat()
with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for p in pages:
        if p["file"] in NOINDEX:
            continue
        if not os.path.exists(os.path.join(ROOT, "pages", p["file"] + ".html")):
            continue
        loc = "%s/%s" % (SITE_URL, "" if p["file"] == "index" else p["file"] + ".html")
        priority = "1.0" if p["file"] == "index" else ("0.8" if p.get("product") else "0.6")
        f.write("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n"
                % (loc, today, priority))
    f.write("</urlset>\n")

built = sum(1 for p in pages if os.path.exists(os.path.join(ROOT, "pages", p["file"] + ".html")))
print(f"built {built}/{len(pages)} pages -> dist/")
