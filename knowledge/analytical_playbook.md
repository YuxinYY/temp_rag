# Analytical Playbook & Common Business Questions

## How Sales Teams Use This Data

Benjamin Moore's sales analytics team uses this dataset primarily for:
1. **Territory performance reviews** — quarterly business reviews with each rep
2. **Segment mix analysis** — tracking shift toward/away from premium products
3. **New account development** — identifying geographic areas with low penetration
4. **Product line rationalization** — identifying underperforming SKUs for discontinuation
5. **Competitive displacement tracking** — watching for volume losses in key product groups

---

## Common Analytical Questions & How to Answer Them

### Territory Performance

**Q: Which territories are growing year-over-year?**
- Compare 2024 vs 2025 Trade Sales Dollars by Territory
- Calculate YoY growth % = (2025 − 2024) / 2024 × 100
- Flag territories with >10% growth as high performers, <−10% as at-risk

**Q: Which territories have the best premium mix?**
- Filter to Product Segment IN ('SUPER PREMIUM', 'PREMIUM')
- Divide by total territory dollars
- Territories above 40% premium mix are considered healthy positioning

**Q: Which territories are overly dependent on Private Label?**
- Filter to Product Segment = 'PRIVATE LABEL'
- Divide by total territory dollars
- >25% Private Label concentration is flagged for strategic review

---

### Product Performance

**Q: What is the revenue contribution of each product segment?**
- Group by Product Segment, sum Trade Sales Dollars
- Calculate mix % of total
- Super Premium + Premium combined should ideally exceed 35% of total dollars

**Q: Which product groups are declining?**
- Compare 2024 vs 2025 by Product Group
- Focus on groups with >$50K in 2024 that declined >15%

**Q: What is the average realized price per gallon by product group?**
- Exclude rows where Trade Sales Gallons = 0 (Merchandising, some returns)
- Exclude COLOR SAMPLES segment (distorts pricing)
- Calculate: SUM(Dollars) / SUM(Gallons) per group

---

### Geographic Analysis

**Q: How does Canada compare to USA performance?**
- Filter by Country = 'USA' vs 'CANADA'
- Compare total dollars, gallons, and segment mix
- Canada typically skews more commercial/commodity vs USA's premium mix

**Q: Which states/provinces drive the most volume?**
- Group by State/Province, sum Trade Sales Dollars and Gallons
- Note: Florida, New York, and California are historically top 3 US states

**Q: What is the international business size?**
- Filter Country NOT IN ('USA', 'CANADA')
- Segment by region (Caribbean, Europe, Asia, Latin America)

---

### Sector Analysis

**Q: How much revenue comes from professional vs. retail channels?**
- Professional: Industry Sector IN ('PAINTING CONTRACTOR', 'GENERAL CONTRACTOR', 'FRANCHISE PAINTER', 'PAINT COMMERCIAL')
- Retail: Industry Sector IN ('HARDWARE', 'PAINT & DECORATING', 'SM HOME IMPROVEMENT', 'BUILDING SUPPLY')
- Institutional: Industry Sector IN ('HEALTHCARE', 'HOSPITALITY', 'PROPERTY MANAGEMENT', 'GOVERNMENT', 'EDUCATION')

**Q: Which sectors buy the most premium products?**
- Filter by Product Segment IN ('SUPER PREMIUM', 'PREMIUM')
- Group by Industry Sector
- Hospitality and Property Management typically index highest for premium

---

## Glossary of Internal Terms

| Term | Meaning |
|---|---|
| **GMV** | Gross Merchandise Value — total trade sales dollars before returns |
| **Net Revenue** | GMV minus returns (negative rows) |
| **Mix Shift** | Change in the proportion of premium vs. commodity sales over time |
| **ACE-only territory** | Sales rep whose entire book of business is ACE Hardware dealers |
| **GPO** | Group Purchasing Organization — negotiated contract account |
| **DTM** | Direct-to-Metal — industrial coating applied without a separate primer |
| **VOC** | Volatile Organic Compounds — regulatory measure of paint emissions |
| **LEED** | Leadership in Energy and Environmental Design — green building certification |
| **Trade price** | Price charged by Benjamin Moore to dealers (not retail consumer price) |
| **Coverage rate** | Square footage a gallon of paint covers (typically 350–400 sq ft/gallon) |
| **Hide** | A paint's ability to cover the previous color in fewer coats |
| **Sheen** | The level of glossiness of the dried paint film |
| **Specification** | When an architect or designer formally names a product in project documents |
| **Color pull** | When a dealer generates a customer order from a color chip or fan deck |
| **SKU** | Stock Keeping Unit — individual product variant (color + sheen + size) |
| **Colorant** | Liquid pigment concentrate added to base paint in-store to achieve custom colors |
| **Base paint** | Untinted paint formula that accepts colorant. Deep base accepts more colorant for dark colors; pastel base accepts less |

---

## Known Data Limitations

1. **No SKU-level detail**: Data is at Product Line level. Cannot distinguish between specific colors or individual can sizes.
2. **No time sub-period**: Data is annual. Cannot analyze monthly or quarterly trends within a year.
3. **No cost data**: Only revenue is available. Cannot calculate margins or profitability.
4. **No customer count**: Cannot determine number of unique dealers per territory.
5. **Territory naming inconsistency**: Territory names reflect the rep's name and may change when territories are reassigned. "ACE ONLY" suffix is not standardized — some ACE reps lack this tag.
6. **Partial 2025**: Depending on export date, 2025 may represent only a partial year. Always validate total row counts and sum figures before comparing 2024 vs 2025 directly.
7. **No unit price at SKU level**: Price per gallon is derived, not sourced. Distorted by product mix within a group.
8. **Returns inflate negative rows**: A single large return can make an entire territory or product line appear negative for the period.