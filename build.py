#!/usr/bin/env python3
"""Assemble pages/*.html + layout/base.html -> dist/.

Pages use small macros for the repeating components of the reference design
({{CARD}}, {{POST}}, {{FAQ}}, {{MARQUEE}}...) so a product card is defined once.
"""
import os, re, json, shutil

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
 "Contact Page Image":                   "dr-althea-147-barrier-cream",
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


def ph(label, extra=""):
    """Real image when we have one for this label, otherwise a labelled
    placeholder. Either way it fills the same container, so the box, ratio
    and card size are identical."""
    slug = IMAGES.get(label)
    cls = ("ph " + extra).strip()
    if slug:
        img_cls = ("ph-img " + extra).strip()
        return f'<img class="{img_cls}" src="assets/products/{slug}.jpg" alt="{label}"/>'
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


def card(imglabel, brand, name, price="R___"):
    """Product card. Brand sits above the product name; the rating comes from
    RATINGS so each product carries its own score."""
    href = PRODUCT_PAGES.get(name, "product.html")
    return f'''<a class="pcard" href="{href}">
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
    for k in NAV_KEYS:
        doc = doc.replace("{{N_%s}}" % k.upper(), "is-active" if p.get("nav") == k else "")
    doc = expand(doc)
    open(os.path.join(DIST, p["file"] + ".html"), "w", encoding="utf-8").write(doc)

built = sum(1 for p in pages if os.path.exists(os.path.join(ROOT, "pages", p["file"] + ".html")))
print(f"built {built}/{len(pages)} pages -> dist/")
