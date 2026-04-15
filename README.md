# Invoice Generator AI

> By [MEOK AI Labs](https://meok.ai) — Generate professional invoices with line items and totals

## Installation

```bash
pip install invoice-generator-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `generate_invoice`
Generate a professional invoice. Each item needs 'description', 'qty', and 'price' keys.

**Parameters:**
- `client` (str): Client name
- `items` (list[dict]): Line items with description, qty, and price
- `currency` (str): Currency code (default: "USD")
- `tax_region` (str): Tax region: US, UK, AU, EU, CA, NZ (default: "US")
- `template` (str): Template: standard, professional, simple, freelancer (default: "standard")
- `due_days` (int): Payment due in days (default: 30)
- `notes` (str): Additional notes

### `calculate_totals`
Calculate subtotal, tax, discount, and grand total for a list of line items.

**Parameters:**
- `items` (list[dict]): Line items with description, qty, and price
- `tax_region` (str): Tax region (default: "US")
- `discount_percent` (float): Discount percentage (default: 0)

### `validate_invoice`
Validate an invoice dict for required fields, correct math, and common errors.

**Parameters:**
- `invoice` (dict): Invoice data to validate

### `list_templates`
List all available invoice templates with their details.

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
