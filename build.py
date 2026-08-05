#!/usr/bin/env python3
"""Assemble pages/*.html + layout/base.html -> dist/.

Pages use small macros for the repeating components of the reference design
({{CARD}}, {{POST}}, {{FAQ}}, {{MARQUEE}}...) so a product card is defined once.
"""
import os, re, json, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

NAV_KEYS = ["home", "shop", "skin", "makeup", "fragrance", "brands", "about", "journal", "contact"]

MARQUEE_ITEMS = ["Skincare", "Serums", "Face Cleansers", "Sunscreens", "Toners",
                 "Moisturisers", "Face Masks", "Makeup", "Fragrance", "Body Care",
                 "Accessories", "Gift Sets"]


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
 "About Image 1":                        "abib-heartleaf-cleanser-lifestyle",
 "About Image 2":                        "skin1004-madagascar-centella-ampoule-lifestyle",
 "About Image 3":                        "medicube-jar-lifestyle",
 "About Image 4":                        "abib-mask-sachets",
 "About Feature Image":                  "skin1004-centella-toning-toner",
 "Contact Page Image":                   "medicube-jar-lifestyle",
 "Skincare Essentials Image 1":          "skin1004-madagascar-centella-ampoule",
 "Skincare Essentials Image 2":          "isntree-green-tea-fresh-toner",

 # categories
 "Serums Category Image":                "axis-y-dark-spot-correcting-glow-serum",
 "Face Cleansers Category Image":        "abib-acne-foam-cleanser",
 "Sunscreens Category Image":            "beauty-of-joseon-relief-sun",
 "Toners Category Image":                "isntree-green-tea-fresh-toner",
 "Skincare Category Image":              "beauty-of-joseon-glow-deep-serum",
 "Moisturisers Category Image":          "medicube-collagen-jelly-cream",
 "Face Masks Category Image":            "medicube-deep-peptide-radiance-mask",

 # promotional
 "Skincare Promotion Image":             "skin1004-centella-toning-toner",
 "New Arrivals Promotion Image":         "beauty-of-joseon-glow-deep-serum",
 "Korean Skincare Banner Image":         "skin1004-madagascar-centella-ampoule",
 "New Arrivals Feature Image":           "anua-niacinamide-txa-serum",
 "Shop Promotion Image":                 "medicube-collagen-jelly-cream",
 "Journal Promotion Image":              "beauty-of-joseon-relief-sun",

 # product cards
 "Medicube Collagen Jelly Cream Image":              "medicube-collagen-jelly-cream",
 "Beauty of Joseon Relief Sun Image":                "beauty-of-joseon-relief-sun",
 "SKIN1004 Madagascar Centella Ampoule Image":       "skin1004-madagascar-centella-ampoule",
 "Abib Acne Foam Cleanser Image":                    "abib-acne-foam-cleanser",
 "AXIS-Y Dark Spot Correcting Glow Serum Image":     "axis-y-dark-spot-correcting-glow-serum",
 "Isntree Green Tea Fresh Toner Image":              "isntree-green-tea-fresh-toner",
 "SKIN1004 Tone Brightening Capsule Ampoule Image":  "skin1004-tone-brightening-capsule-ampoule",
 "Medicube Deep Peptide Radiance Mask Image":        "medicube-deep-peptide-radiance-mask",
 "Abib Collagen Gel Mask Image":                     "abib-collagen-gel-mask",
 "COSRX Advanced Snail 92 Cream Image":              "cosrx-advanced-snail-92-cream",
 "Anua Niacinamide 10 TXA 4 Serum Image":            "anua-niacinamide-txa-serum",
 "Beauty of Joseon Glow Deep Serum Image":           "beauty-of-joseon-glow-deep-serum",
 "SKIN1004 Centella Toning Toner Image":             "skin1004-centella-toning-toner",

 # product detail gallery
 "Product Image 1": "skin1004-madagascar-centella-ampoule",
 "Product Image 2": "skin1004-madagascar-centella-ampoule-lifestyle",
 "Product Image 3": "skin1004-centella-ampoule-foam",
 "Product Image 4": "skin1004-tone-brightening-capsule-ampoule",

 # social grid
 "Social Image 1": "medicube-collagen-jelly-cream",
 "Social Image 2": "abib-heartleaf-cleanser-lifestyle",
 "Social Feature Image": "skin1004-madagascar-centella-ampoule",
 "Social Image 3": "beauty-of-joseon-glow-deep-serum",
 "Social Image 4": "isntree-green-tea-fresh-toner",
 "Social Image 5": "medicube-collagen-radiance-mask",
 "Social Image 6": "abib-mask-sachets",
 "Social Image 7": "skin1004-centella-toning-toner",
 "Social Image 8": "medicube-jar-lifestyle",
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
}


def card(imglabel, brand, name, price="R___"):
    """Product card. Brand sits above the product name; no invented rating,
    discount badge or stock level until the real catalogue is loaded."""
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
<div class="pcard__row"><span class="pcard__cat">{brand}</span><span class="rating">Rating coming soon</span></div>
<h3 class="pcard__name">{name}</h3>
<div class="price">{price}</div>
</a>'''


def post(imglabel, cat, title):
    return f'''<a class="post" href="blog-details.html">
<div class="post__media"><span class="badge">{cat}</span>{ph(imglabel)}</div>
<div class="post__meta">Cassaro Beauty Editorial</div>
<h3 class="post__title">{title}</h3>
<span class="link-underline">Read More</span>
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
    html = re.sub(r"\{\{POST\|([^}]*)\}\}", lambda m: post(*m.group(1).split("|")), html)
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
