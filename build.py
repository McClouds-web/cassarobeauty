#!/usr/bin/env python3
"""Assemble pages/*.html + layout/base.html -> dist/.

Pages use small macros for the repeating components of the reference design
({{CARD}}, {{POST}}, {{FAQ}}, {{MARQUEE}}...) so a product card is defined once.
"""
import os, re, json, shutil, datetime, hashlib, html as _html, urllib.parse

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
 "Medicube Zero Pore Pad Image":                     "medicube-zero-pore-pad",
 "Beauty of Joseon Red Bean Pore Mask Image":        "beauty-of-joseon-red-bean-refreshing-pore-mask",
 "Beauty of Joseon Apricot Peeling Gel Image":       "beauty-of-joseon-apricot-blossom-peeling-gel",
 "Anua Heartleaf Pore Deep Cleansing Foam Image":    "anua-heartleaf-quercetinol-pore-deep-cleansing-foam",
 "Anua Peach 70 Niacin Collagen Mask Image":         "anua-peach-70-niacin-brightening-collagen-mask",
 "MISSHA Airy Fit Sheet Mask Image":                 "missha-airy-fit-sheet-mask",
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
 "SKIN1004 Hyalu-Cica Brightening Toner Image":       "skin1004-madagascar-centella-hyalu-cica-brightening-toner",
 "SKIN1004 Hyalu-Cica First Ampoule Image":           "skin1004-madagascar-centella-hyalu-cica-first-ampoule",
 "SKIN1004 Probio-Cica Enrich Cream Image":           "skin1004-madagascar-centella-probio-cica-enrich-cream",
 "SKIN1004 Tea-Trica Purifying Toner Image":          "skin1004-madagascar-centella-tea-trica-purifying-toner",
 "Anua Zero-Cast Sunscreen Image":                    "anua-zero-cast-moisturizing-finish-sunscreen",
 "d\'Alba First Spray Serum Image":                    "dalba-piedmont-first-spray-serum",
 "mixsoon Centella Cleansing Foam Image":             "mixsoon-centella-cleansing-foam",
 "mixsoon Centella Sun Cream Image":                  "mixsoon-centella-sun-cream",

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


def img_direct(slug, alt, extra=""):
    """Render a known image file. ph() maps a human label to a file; galleries
    instead need to name the file, because which variants exist differs per
    product."""
    img_cls = ("ph-img " + extra).strip()
    size = _dims(slug)
    dim = f' width="{size[0]}" height="{size[1]}"' if size else ""
    # The gallery's main photo is the largest thing above the fold, so it must
    # not be deferred; thumbnails and everything else can wait.
    eager = "eager" in extra
    img_cls = img_cls.replace("eager", "").strip()
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    img = (f'<img class="{img_cls}" src="assets/products/{slug}.jpg"'
           f' alt="{alt}"{dim}{load}/>')
    if os.path.exists(os.path.join(ROOT, "assets", "products", slug + ".webp")):
        return ('<picture>'
                f'<source srcset="assets/products/{slug}.webp" type="image/webp"/>'
                f'{img}</picture>')
    return img


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
 "Zero Pore Pad": "medicube-zero-pore-pad.html",
 "Red Bean Refreshing Pore Mask": "beauty-of-joseon-red-bean-refreshing-pore-mask.html",
 "Apricot Blossom Peeling Gel": "beauty-of-joseon-apricot-blossom-peeling-gel.html",
 "Heartleaf Quercetinol Pore Deep Cleansing Foam": "anua-heartleaf-quercetinol-pore-deep-cleansing-foam.html",
 "Peach 70 Niacin Brightening Collagen Mask": "anua-peach-70-niacin-brightening-collagen-mask.html",
 "Airy Fit Sheet Mask": "missha-airy-fit-sheet-mask.html",
 "Advanced Snail 92 All in One Cream": "cosrx-advanced-snail-92-cream.html",
 "Azelaic Acid 10 + Hyaluron Redness Soothing Serum": "anua-azelaic-acid-10-hyaluron-serum.html",
 "Collagen Night Wrapping Mask": "medicube-collagen-night-wrapping-mask.html",
 "Relief Sun: Rice + Probiotics": "beauty-of-joseon-relief-sun.html",
 "Madagascar Centella Toning Toner": "skin1004-centella-toning-toner.html",
 "PDRN Pink Collagen Gel Mask": "medicube-pdrn-pink-collagen-gel-mask.html",
 "Madagascar Centella Hyalu-Cica Brightening Toner": "skin1004-madagascar-centella-hyalu-cica-brightening-toner.html",
 "Madagascar Centella Hyalu-Cica First Ampoule": "skin1004-madagascar-centella-hyalu-cica-first-ampoule.html",
 "Madagascar Centella Probio-Cica Enrich Cream": "skin1004-madagascar-centella-probio-cica-enrich-cream.html",
 "Madagascar Centella Tea-Trica Purifying Toner": "skin1004-madagascar-centella-tea-trica-purifying-toner.html",
 "Zero-Cast Moisturizing Finish Sunscreen SPF50": "anua-zero-cast-moisturizing-finish-sunscreen.html",
 "First Spray Serum": "dalba-piedmont-first-spray-serum.html",
 "Centella Cleansing Foam": "mixsoon-centella-cleansing-foam.html",
 "Centella Sun Cream SPF50+ PA++++": "mixsoon-centella-sun-cream.html",
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
 "Zero Pore Pad":                                      (4.7, 186),
 "Red Bean Refreshing Pore Mask":                      (4.8, 213),
 "Apricot Blossom Peeling Gel":                        (4.8, 241),
 "Heartleaf Quercetinol Pore Deep Cleansing Foam":     (4.8, 268),
 "Peach 70 Niacin Brightening Collagen Mask":           (4.8, 302),
 "Airy Fit Sheet Mask":                                 (4.6, 418),
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
 "Madagascar Centella Hyalu-Cica Brightening Toner":   (4.7, 178),
 "Madagascar Centella Hyalu-Cica First Ampoule":       (4.8, 224),
 "Madagascar Centella Probio-Cica Enrich Cream":       (4.7, 145),
 "Madagascar Centella Tea-Trica Purifying Toner":      (4.7, 192),
 "Zero-Cast Moisturizing Finish Sunscreen SPF50":      (4.8, 276),
 "First Spray Serum":                                  (4.8, 331),
 "Centella Cleansing Foam":                            (4.7, 156),
 "Centella Sun Cream SPF50+ PA++++":                   (4.7, 168),
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
 "Zero Pore Pad":                                      ("Toners",       "combination oily",                 "blemishes brightening"),
 "Red Bean Refreshing Pore Mask":                      ("Face Masks",   "combination oily",                 "blemishes"),
 "Apricot Blossom Peeling Gel":                        ("Face Cleansers", "normal combination oily",        "brightening"),
 "Heartleaf Quercetinol Pore Deep Cleansing Foam":     ("Face Cleansers", "normal combination oily",        "blemishes"),
 "Peach 70 Niacin Brightening Collagen Mask":           ("Face Masks",   "normal combination dry",           "brightening"),
 "Airy Fit Sheet Mask":                                 ("Face Masks",   "normal combination dry oily",      "hydration soothing"),
 "Madagascar Centella Hyalu-Cica Brightening Toner":   ("Toners",       "normal combination dry sensitive", "brightening hydration soothing"),
 "Madagascar Centella Hyalu-Cica First Ampoule":       ("Ampoules",     "normal combination dry sensitive", "hydration soothing"),
 "Madagascar Centella Probio-Cica Enrich Cream":       ("Moisturisers", "normal combination dry sensitive", "hydration soothing"),
 "Madagascar Centella Tea-Trica Purifying Toner":      ("Toners",       "combination oily sensitive",       "blemishes soothing"),
 "Zero-Cast Moisturizing Finish Sunscreen SPF50":      ("Sunscreens",   "normal combination dry oily",      "daily-protection hydration"),
 "First Spray Serum":                                  ("Serums",       "normal combination dry",           "hydration brightening"),
 "Centella Cleansing Foam":                            ("Face Cleansers", "normal combination oily sensitive", "soothing"),
 "Centella Sun Cream SPF50+ PA++++":                   ("Sunscreens",   "normal combination dry sensitive", "daily-protection soothing"),
}

DEFAULT_FACET = ("Skincare", "normal combination", "hydration")


# Retail price in rand, keyed by product name. A product absent from this table
# still renders "R___" everywhere and is left out of the JSON-LD offer block,
# so the catalogue can be priced one product at a time without the cart, the
# WhatsApp message or Google ever seeing a half-priced product.
PRICES = {
 # Serums and ampoules
 "Madagascar Centella Ampoule": 575.00,
 "Madagascar Centella Hyalu-Cica First Ampoule": 395.00,
 "Madagascar Centella Poremizing Fresh Ampoule": 400.00,
 "Madagascar Centella Tea-Trica Relief Ampoule": 495.00,
 "Azelaic Acid 10 + Hyaluron Redness Soothing Serum": 500.00,
 "First Spray Serum": 350.00,
 "Madagascar Centella Tone Brightening Capsule Ampoule": 95.00,
 "Dark Spot Correcting Glow Serum": 390.00,
 "Glow Deep Serum: Rice + Alpha-Arbutin": 350.00,
 # Cleansers
 "Deep Clean Foam Cleanser &mdash; Sedum Hyaluron Foam": 250.00,
 "Acne Foam Cleanser &ndash; Heartleaf Foam": 250.00,
 "Madagascar Centella Poremizing Deep Cleansing Foam": 310.00,
 "Madagascar Centella Ampoule Foam": 300.00,
 "Heartleaf Quercetinol Pore Deep Cleansing Foam": 280.00,
 "Centella Cleansing Foam": 200.00,
 # Toners and pads
 "Madagascar Centella Hyalu-Cica Brightening Toner": 395.00,
 "Green Tea Fresh Toner": 450.00,
 "Madagascar Centella Tea-Trica Purifying Toner": 400.00,
 "Zero Pore Pad": 580.00,
 # Sunscreens
 "Madagascar Centella Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++": 395.00,
 "Relief Sun: Rice + Probiotics SPF50+ PA++++": 360.00,
 "Zero-Cast Moisturizing Finish Sunscreen SPF50": 350.00,
 "Centella Sun Cream SPF50+ PA++++": 190.00,
 # Masks
 "Collagen Gel Mask &ndash; Sedum Jelly": 150.00,
 "Bouncy Day Collagen Glow Up Hydrogel Mask": 150.00,
 "Collagen Radiance Mask": 90.00,
 "Deep Peptide Radiance Mask": 100.00,
 "PDRN Pink Collagen Gel Mask": 100.00,
 "Airy Fit Sheet Mask": 40.00,
 "Peach 70 Niacin Brightening Collagen Mask": 135.00,
 "Kojic Acid Turmeric Brightening Gel Mask": 135.00,
 "Zero Pore Blackhead Mud Mask": 350.00,
 "Red Bean Refreshing Pore Mask": 480.00,
 "Collagen Night Wrapping Mask": 650.00,
 "Apricot Blossom Peeling Gel": 300.00,
 # Moisturisers
 "Advanced Snail 92 All in One Cream": 460.00,
 "Madagascar Centella Probio-Cica Enrich Cream": 470.00,
 "Seoul 1988 Cream: Snail Mucin 93% + Rice": 500.00,
 "Collagen Jelly Cream": 480.00,
}

CURRENCY = "ZAR"


# Product cards shorten some names ("Relief Sun: Rice + Probiotics" for the
# product page's "Relief Sun: Rice + Probiotics SPF50+ PA++++"), and the same
# name is written with an entity in one place and a literal dash in another.
# Prices are keyed by the full product name, so a card looked up by its own
# label would silently fall back to R___ — which is exactly what happened. Both
# forms are normalised before lookup, and a shortened label is listed here.
CARD_ALIASES = {
 "Acne Foam Cleanser":                          "Acne Foam Cleanser &ndash; Heartleaf Foam",
 "Deep Clean Foam Cleanser - Sedum Hyaluron":   "Deep Clean Foam Cleanser &mdash; Sedum Hyaluron Foam",
 "Glow Deep Serum: Rice + Alpha Arbutin":       "Glow Deep Serum: Rice + Alpha-Arbutin",
 "Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++":"Madagascar Centella Hyalu-Cica Water-Fit Sun Serum SPF50+ PA++++",
 "Relief Sun: Rice + Probiotics":               "Relief Sun: Rice + Probiotics SPF50+ PA++++",
 "Tone Brightening Capsule Ampoule":            "Madagascar Centella Tone Brightening Capsule Ampoule",
}


def norm_name(name):
    """Entity-free, dash-agnostic, case-folded form of a product name."""
    text = _html.unescape(name)
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _price_index():
    index = {}
    for key, amount in PRICES.items():
        index[norm_name(key)] = amount
    for label, target in CARD_ALIASES.items():
        if target in PRICES:
            index[norm_name(label)] = PRICES[target]
    return index


PRICE_INDEX = _price_index()


def price_of(name):
    """Formatted price for a product name or card label, or the R___ placeholder."""
    amount = PRICES.get(name)
    if amount is None:
        amount = PRICE_INDEX.get(norm_name(name))
    return f"R{amount:,.2f}" if amount is not None else "R___"


CARD_LABELS_SEEN = set()


def card(imglabel, brand, name, price=None):
    """Product card. Brand sits above the product name; the rating comes from
    RATINGS so each product carries its own score."""
    CARD_LABELS_SEEN.add(name)
    price = price or price_of(name)
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
    html = re.sub(r"\{\{IMG\|([^}]*)\}\}",
                  lambda m: img_direct(*(m.group(1).split("|") + ["", ""])[:3]), html)
    html = result_count(html)
    return html


def result_count(html):
    """The shop and skincare grids print a product count above the grid. The
    filter script only rewrites it once a filter is touched, so the number in
    the markup has to be right on first paint. Count the cards the grid was
    actually built with rather than trusting a hand-typed figure."""
    m = re.search(r'<div class="grid[^"]*" data-product-grid>(.*?)\n      </div>',
                  html, re.S)
    if not m:
        return html
    n = m.group(1).count('<a class="pcard"')
    return re.sub(r'(<span data-result-count>)Showing \d+ products?(</span>)',
                  r'\g<1>Showing %d product%s\g<2>' % (n, "" if n == 1 else "s"),
                  html)


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


# Brand marks for the share row. The site already draws Instagram, TikTok and
# WhatsApp as inline SVG in the layout; these follow that, rather than the
# generic material glyphs the share row used to borrow (a globe for Facebook,
# a close icon for X), which read as UI icons rather than as networks.
SHARE_ICONS = {
 "whatsapp": '<path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37s-1.04 1.02-1.04 2.48 1.07 2.88 1.22 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.19 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.42-.07-.13-.27-.2-.57-.35ZM12.04 21.5h-.01a9.4 9.4 0 0 1-4.79-1.31l-.34-.2-3.56.93.95-3.47-.22-.36a9.38 9.38 0 0 1-1.44-5.01c0-5.18 4.22-9.4 9.42-9.4a9.35 9.35 0 0 1 6.65 2.76 9.32 9.32 0 0 1 2.75 6.65c0 5.18-4.22 9.4-9.41 9.4Zm8-17.4A11.31 11.31 0 0 0 12.04.79C5.75.79.63 5.91.63 12.2c0 2.01.53 3.98 1.53 5.71L.53 23.75l5.98-1.57a11.36 11.36 0 0 0 5.53 1.41h.01c6.29 0 11.41-5.12 11.41-11.41 0-3.05-1.19-5.91-3.35-8.07Z"/>',
 "facebook": '<path d="M22 12.06C22 6.5 17.52 2 12 2S2 6.5 2 12.06c0 5.02 3.66 9.18 8.44 9.94v-7.03H7.9v-2.91h2.54V9.85c0-2.52 1.49-3.91 3.77-3.91 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.78-1.63 1.57v1.89h2.78l-.45 2.91h-2.33V22c4.78-.76 8.44-4.92 8.44-9.94Z"/>',
 "x":        '<path d="M17.53 3h3.02l-6.6 7.55L21.75 21h-5.9l-4.62-6.04L5.94 21H2.92l7.06-8.07L2.4 3h6.05l4.18 5.52L17.53 3Zm-1.06 16.2h1.67L7.6 4.71H5.81L16.47 19.2Z"/>',
 "pinterest":'<path d="M12 2a10 10 0 0 0-3.65 19.31c-.09-.78-.17-1.98.03-2.83.19-.79 1.2-5.06 1.2-5.06s-.31-.61-.31-1.52c0-1.42.83-2.48 1.85-2.48.88 0 1.3.66 1.3 1.45 0 .88-.56 2.2-.85 3.42-.24 1.02.51 1.86 1.52 1.86 1.83 0 3.23-1.93 3.23-4.71 0-2.46-1.77-4.18-4.3-4.18-2.93 0-4.65 2.2-4.65 4.47 0 .89.34 1.84.77 2.36.08.1.1.19.07.29-.08.32-.25.99-.28 1.13-.05.19-.15.23-.35.14-1.3-.61-2.11-2.5-2.11-4.03 0-3.28 2.38-6.29 6.87-6.29 3.6 0 6.4 2.57 6.4 6 0 3.58-2.25 6.46-5.39 6.46-1.05 0-2.04-.55-2.38-1.2l-.65 2.47c-.23.9-.86 2.03-1.28 2.72A10 10 0 1 0 12 2Z"/>',
}


def share_row(page):
    """Share links for a product page. Every target is a real endpoint that
    takes this page's own URL.

    Instagram is deliberately absent: it has no web share endpoint, so the icon
    that used to sit here could never have worked. Copy link takes its place,
    which is what someone pasting into a story or a DM actually needs.
    """
    url = "%s/%s.html" % (SITE_URL, page["file"])
    name = _html.unescape(page["product"]["name"])
    text = "%s — %s" % (name, config_value("storeName", "Cassaro Beauty"))
    q = lambda s: urllib.parse.quote(s, safe="")
    links = [
        ("WhatsApp",  "https://wa.me/?text=%s%%20%s" % (q(text), q(url)), "whatsapp"),
        ("Facebook",  "https://www.facebook.com/sharer/sharer.php?u=%s" % q(url), "facebook"),
        ("X",         "https://twitter.com/intent/tweet?url=%s&text=%s" % (q(url), q(text)), "x"),
        ("Pinterest", "https://pinterest.com/pin/create/button/?url=%s&media=%s&description=%s"
                      % (q(url), q("%s/%s" % (SITE_URL, page["product"]["image"])), q(text)), "pinterest"),
    ]
    out = []
    for label, href, icon in links:
        out.append('<a href="%s" target="_blank" rel="noopener" aria-label="Share on %s">'
                   '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">%s</svg></a>'
                   % (html_escape(href), label, SHARE_ICONS[icon]))
    out.append('<button type="button" class="share-copy" data-copy-link aria-label="Copy link">'
               '<span class="material-symbols-outlined">link</span></button>')
    return "\n          ".join(out)


def html_escape(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


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
        product = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": page["product"]["name"],
            "brand": {"@type": "Brand", "name": page["product"]["brand"]},
            "description": page["desc"],
            "image": SITE_URL + "/" + page["product"]["image"],
            "url": SITE_URL + "/" + page["file"] + ".html",
        }
        amount = PRICES.get(page["product"]["name"])
        if amount is not None:
            product["offers"] = {
                "@type": "Offer",
                "price": f"{amount:.2f}",
                "priceCurrency": CURRENCY,
                "availability": "https://schema.org/InStock",
                "url": SITE_URL + "/" + page["file"] + ".html",
            }
        blocks.append(product)
    if not blocks:
        return ""
    body = json.dumps(blocks[0] if len(blocks) == 1 else blocks, indent=1)
    return '<script type="application/ld+json">%s</script>' % body


WA_NUMBER = config_value("whatsappNumber")
WA_DISPLAY = config_value("whatsappDisplay")
CONTACT_EMAIL = config_value("contactEmail", "cassarobeauty.za@gmail.com")
TAGLINE = config_value("tagline", "Where self-care becomes art")
BANK = {
    "NAME":    config_value("bankName"),
    "ACCOUNT": config_value("bankAccountName"),
    "NUMBER":  config_value("bankAccountNumber"),
    "BRANCH":  config_value("bankBranchCode"),
}


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
    # The home page leads with the brand and its tagline; every other page is
    # "<page> — Cassaro Beauty".
    page_title = ("Cassaro Beauty — " + TAGLINE if p["file"] == "index"
                  else p["title"] + " — Cassaro Beauty")
    doc = doc.replace("{{PAGE_TITLE}}", page_title)
    doc = doc.replace("{{TITLE}}", p["title"]).replace("{{DESC}}", p["desc"])
    doc = doc.replace("{{WA_NUMBER}}", WA_NUMBER).replace("{{WA_DISPLAY}}", WA_DISPLAY)
    doc = doc.replace("{{WA_LINK}}", "https://wa.me/" + WA_NUMBER)
    doc = doc.replace("{{CONTACT_EMAIL}}", CONTACT_EMAIL)
    doc = doc.replace("{{TAGLINE}}", TAGLINE)
    # Banking details are substituted only into order-completed.html. Any other
    # page that used a {{BANK_*}} placeholder would publish the account number
    # on a crawlable page, so the placeholders are left unresolved and the
    # build fails loudly below instead.
    if p["file"] == "order-completed":
        for k, v in BANK.items():
            doc = doc.replace("{{BANK_%s}}" % k, v)
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
    doc = doc.replace("{{SHARE}}", share_row(p) if p.get("product") else "")
    if p.get("product"):
        # The buy column's price is written from PRICES, not from the page
        # markup, so the visible price, the cart, the WhatsApp message and the
        # JSON-LD offer can never disagree. Pages keep "R___" as their source
        # text; an unpriced product still renders the placeholder.
        doc = re.sub(r'(<div class="pdp__price"[^>]*>)[^<]*(</div>)',
                     lambda m: m.group(1) + price_of(p["product"]["name"]) + m.group(2),
                     doc)
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

# A card label that matches no product page prices nothing and links nowhere
# useful. That drift is invisible in the output — the card just renders R___ —
# so name it here rather than letting it reach the shop.
product_names = {norm_name(p["product"]["name"]) for p in pages if p.get("product")}
product_names |= {norm_name(k) for k in CARD_ALIASES}
orphans = sorted({n for n in CARD_LABELS_SEEN if norm_name(n) not in product_names})
if orphans:
    print("  WARNING: card labels with no matching product page:")
    for n in orphans:
        print("    -", n)
leaked = []
for p in pages:
    src_path = os.path.join(ROOT, "pages", p["file"] + ".html")
    if p["file"] == "order-completed" or not os.path.exists(src_path):
        continue
    if "{{BANK_" in open(src_path, encoding="utf-8").read():
        leaked.append(p["file"])
if leaked:
    raise SystemExit("banking details may only appear on order-completed.html; "
                     "found a {{BANK_*}} placeholder in: " + ", ".join(leaked))

unpriced = sorted({p["product"]["name"] for p in pages
                   if p.get("product") and price_of(p["product"]["name"]) == "R___"})
if unpriced:
    print(f"  {len(unpriced)} products still unpriced (rendering R___):")
    for n in unpriced:
        print("    -", n)
