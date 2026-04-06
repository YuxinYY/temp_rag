# Product Hierarchy & Catalog

## Product Hierarchy

Benjamin Moore organizes its catalog in a four-level hierarchy:

```
Product Segment
    └── Product Group
            └── Product Line
                    └── Individual SKU (color/sheen variants)
```

In the dataset, the granularity goes down to **Product Line** level. Individual SKU-level data (specific colors, sheens) is not included.

---

## Product Segments

Product Segments are the highest-level classification. They reflect broad strategic categories:

| Segment | Description |
|---|---|
| SUPER PREMIUM | Highest-quality, highest-margin products. Benjamin Moore's flagship tier. |
| PREMIUM | Mid-to-high quality products, strong volume drivers. |
| COMMERCIAL | Formulations optimized for professional and commercial use. |
| COMMODITY | Baseline performance products, price-competitive, high volume. |
| PRIMERS | Surface preparation products across all quality tiers. |
| SPECIALTY | Niche-application products (chalkboard paint, pool paint, traffic marking, etc.). |
| INDUSTRIAL COATINGS | Heavy-duty coatings for industrial/manufacturing applications (INSL-X brand). |
| EXTERIOR STAINS | Wood stains and clear finishes for exterior surfaces (Arborcoat line). |
| FLOORING POLYS | Polyurethane floor finishes (Lenmar, poly clear lines). |
| LACQUERS | Solvent-based lacquers for furniture and cabinetry finishing. |
| COLORANT | Tinting bases and colorant systems used in store mixing machines. |
| COLOR SAMPLES | Small-format sample pots used for customer color trials. Not a revenue segment — often negative margin due to promotional pricing. |
| MERCHANDISING | Point-of-sale materials, display racks, and branded merchandise. |
| PRIVATE LABEL | Products manufactured by Benjamin Moore and sold under a retailer's own brand (primarily ACE Hardware). |
| UNASSIGNED | Transactions pending segment classification. |

---

## Key Product Groups & Lines

### Super Premium Segment
- **AURA INTERIOR / AURA EXTERIOR**: Benjamin Moore's top-tier line. Known for Color Lock technology. Highest price per gallon ($80–$100 retail). Used by premium residential and hospitality clients.
- **AURA GRAND ENTRANCE**: Specialty door and trim paint within the Aura family.
- **REGAL SELECT INTERIOR / EXTERIOR**: Second-tier premium. Strong professional contractor preference.
- **ADVANCE**: Waterborne alkyd line. Premium pricing, favored for cabinetry and furniture due to hard, durable finish.

### Premium Segment
- **BEN INTERIOR / BEN EXTERIOR**: Mid-range workhorse line. Excellent hide, good scrub resistance. Popular with property managers.
- **NATURA**: Zero-VOC interior paint. Targeted at healthcare and education sectors with strict air quality requirements.
- **ECO SPEC / ECO SPEC SILVER**: Low-VOC commercial products. Frequently specified by LEED-certified projects.
- **ELEMENT GUARD**: Exterior line designed for harsh weather resistance.

### Commercial Segment
- **ULTRA SPEC INTERIOR / EXTERIOR**: Core commercial line. Standard specification product for contractors and property managers.
- **ULTRA SPEC 500**: Economy-tier commercial interior. High volume, lower margin.
- **ULTRA SPEC SCUFF-X**: Scuff-resistant formula for high-traffic commercial interiors.
- **SUPERSPEC INTERIOR / EXTERIOR**: Professional-grade commercial line.
- **SUPER KOTE 5000 / 3000**: High-hide commercial coatings. Favored in government and institutional specifications.

### Commodity Segment
- **SUPER HIDE MOOREPRO / SUPER HIDE ZERO**: Entry-level interior products. High volume in hardware channel.
- **MOOREGARD**: Standard exterior commodity product.
- **CONTRACTOR PRO**: Basic contractor-grade interior/exterior line.

### Industrial Coatings (INSL-X Brand)
- **SSHP DTM (Direct-to-Metal)**: Industrial enamel for metal surfaces.
- **SSHP URETHANES / SSHP METAL PRIMERS**: High-performance industrial systems.
- **EPOXY / EPOXY CTECH**: Two-component epoxy coatings for floors and chemical-resistant surfaces.
- **RUST-A-VOID**: Rust-inhibiting primer for steel.
- **TRAFFIC PAINT / ATHLETIC FIELD MARKING**: Specialty marking paints for roads and sports fields.
- **POOL PAINT**: Epoxy and rubber-based coatings for swimming pools.

### Exterior Stains (Arborcoat)
- **ARBORCOAT**: Premium exterior wood stain line. Available in solid, semi-transparent, and transparent formulas.
- **WOODLUXE EXTERIOR STAINS**: Mid-range wood stain alternative.
- **INTERIOR STAINS (BENWOOD)**: Penetrating oil and waterborne stains for interior wood.

### Primers
- **FRESH START PRIMERS**: Multi-purpose interior/exterior primer line. Flagship primer brand.
- **BM INT/EXT MP PRIMER**: Multi-purpose primer at value pricing.
- **BM PRO PRIMER / BM MASONRY**: Specialized substrate primers.
- **SURE SEAL**: Stain-blocking high-hide primer.
- **STEP ONE PRIMER**: Entry-level primer for hardware channel.

### Private Label (ACE Hardware)
- **ACE CONTRACTOR PRO INTERIOR / EXTERIOR**: ACE-branded equivalent to Benjamin Moore commercial lines.
- **ACE CABINET, DOOR & TRIM**: ACE-branded trim paint.
- **ROYAL INTERIOR / EXTERIOR**: Full ACE-branded premium interior/exterior line.
- **C+K INTERIOR / EXTERIOR**: California Products brand sold through ACE.
- **BARN & FENCE LATEX / OIL**: Specialty farm and agricultural coatings.

### Colorant System
- **COLORANT BM PREM / COLORANT CTECH**: Tinting colorants used in-store to mix custom colors. Tracked separately as they flow through the system differently from finished goods.

---

## Sheen Levels
Within each product line, multiple sheen variants exist. Common sheens from flattest to glossiest:
- **FLAT / MATTE** — ceilings, low-traffic walls
- **EGGSHELL** — most popular residential finish
- **SATIN** — kitchens, baths, higher durability
- **SEMI-GLOSS** — trim, doors, cabinets
- **GLOSS / HIGH GLOSS** — maximum durability, furniture, trim

---

## Negative Quantities & Returns
Negative values in Trade Sales Quantity, Gallons, and Dollars represent:
- Product returns from dealers
- Credit memos issued for damaged goods
- Pricing adjustments
- Promotional chargebacks

These are normal in paint distribution and should be expected in any analysis.