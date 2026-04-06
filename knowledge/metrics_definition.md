# Metrics Definitions & Business Rules

## Core Sales Metrics

### Trade Sales Quantity
- **Definition**: Number of product units sold, expressed in standard units (typically single-gallon equivalents or unit packs).
- **Unit**: Dimensionless count of sellable units.
- **Notes**: 
  - Fractional quantities (e.g., 0.333) occur because some product lines are sold in quart or sample sizes and normalized to gallon equivalents for reporting.
  - Negative values represent returns or credit adjustments.
  - A quantity of 0.00 with non-zero Dollars indicates a fee, service charge, or pricing-only adjustment.

### Trade Sales Gallons
- **Definition**: Volume of paint sold, normalized to gallons regardless of container size.
- **Unit**: US gallons.
- **Conversion logic**:
  - 1 gallon can = 1.0 gallon
  - 1 quart can = 0.25 gallons
  - 5-gallon pail = 5.0 gallons
  - Sample size (small pot) ≈ 0.03–0.05 gallons
- **Use**: Gallons is the primary operational volume metric for manufacturing planning and distribution capacity.

### Trade Sales Dollars (Group)
- **Definition**: Net revenue in USD at the group/distributor level, after dealer discounts but before end-consumer markups.
- **Unit**: US Dollars (USD).
- **Important**: This is **not** retail shelf price. Benjamin Moore sells to independent dealers at wholesale/trade pricing, typically 30–50% below suggested retail. Dealers then mark up to retail.
- **"Group" suffix**: Indicates these figures are aggregated at the product group level, not individual SKU level. Some rounding may occur.

---

## Derived Metrics (Calculated Fields)

These columns do not exist in the raw dataset but are commonly calculated in analysis:

### Price Per Gallon
```
Price Per Gallon = Trade Sales Dollars (Group) / Trade Sales Gallons
```
- Indicates the average realized price per gallon for a product group.
- **Typical ranges by segment**:
  - Super Premium (Aura): $45–$75/gallon (trade price)
  - Premium (Regal Select, Advance): $35–$55/gallon
  - Commercial (Ultra Spec): $20–$35/gallon
  - Commodity (Super Hide): $15–$25/gallon
  - Industrial (INSL-X): $25–$60/gallon depending on product
  - Color Samples: Very low or negative (promotional)
- **Warning**: Prices below $5/gallon or above $100/gallon usually indicate data anomalies (returns, fees, sample products).

### Price Per Unit
```
Price Per Unit = Trade Sales Dollars (Group) / Trade Sales Quantity
```
- Less commonly used than price per gallon, but useful for unit economics analysis.

### Revenue Mix %
```
Revenue Mix % = Segment Dollars / Total Dollars × 100
```
- Used in segment performance reports to show contribution of each product tier.

### Gallon Mix %
```
Gallon Mix % = Segment Gallons / Total Gallons × 100
```
- Volume share. Commodity segments often have higher gallon mix % than dollar mix %, indicating lower pricing.

---

## Business Rules & Data Quirks

### Zero-Dollar Transactions
Rows where Trade Sales Dollars = 0.00 but Quantity > 0 represent:
- **No-charge promotions**: Free goods given to dealers as incentives.
- **Samples**: Color sample programs where product is provided at no charge.
- **Internal transfers**: Goods moved between company facilities.

### COLOR SAMPLES Segment
- Always treat separately from revenue analysis. Color Samples are a marketing cost, not a revenue driver.
- Negative dollars in this segment are expected and intentional — Benjamin Moore subsidizes sample programs.
- Gallon volumes from COLOR SAMPLES are negligible (< 0.05 gallons per unit) and should be excluded from pricing analysis.

### MERCHANDISING Segment
- Contains non-paint items: display racks, painter's tape, brushes, roller covers, branded literature.
- Gallons = 0.00 for all merchandising rows (not applicable).
- Useful for understanding total account spend but not for product performance analysis.

### UNASSIGNED Segment / "Not assigned" Sector
- These represent data quality gaps — accounts or products that haven't been fully classified in the system.
- Should be excluded from segment-level performance analysis but included in total revenue figures.

### PRIVATE LABEL Segment
- ACE Hardware private label products manufactured by Benjamin Moore.
- Reported separately because ACE accounts have different margin structures and contractual pricing.
- ACE-only territories have high Private Label concentration.

### Payment Sequencing & Split Records
- Some territory-product combinations appear multiple times in the data. This is expected — each record represents a unique combination of Year × Territory × Industry Sector × State × Country × Product Segment × Product Group × Product Line.
- There is no single "order" concept in this dataset. It is a **summary-level sales reporting table**, not a transactional order table.

### Negative Trade Sales (Returns)
- Negative dollars represent net returns, credits, or chargebacks in that period.
- A territory showing negative total dollars for a period is unusual but not impossible — it would indicate returns exceeded new sales.

---

## Fiscal Year & Reporting Periods

- Benjamin Moore's fiscal year follows the calendar year (January–December).
- The dataset contains **2024** and **2025** data.
- 2025 data may be partial depending on when the export was generated. Always check the distribution of rows by year before drawing year-over-year conclusions.
- There is no month or quarter field in this dataset — all figures are **annual aggregates per territory/product combination**.

---

## KPIs Used by Sales Management

| KPI | Definition | Target |
|---|---|---|
| Total Trade Sales Dollars | Sum of all net revenue | vs. prior year / budget |
| Super Premium Mix % | Aura + Regal dollars / total dollars | >30% is considered healthy |
| Gallon Growth YoY | (2025 gallons − 2024 gallons) / 2024 gallons | Positive growth target |
| Commercial Penetration | Commercial sector dollars / total dollars | Tracked by territory |
| Private Label Dependency | Private Label dollars / total dollars | <20% preferred for margin health |
| International Revenue % | Non-USA + non-Canada dollars / total | Strategic growth metric |
| Return Rate | Abs(negative dollars) / gross positive dollars | <3% is acceptable |