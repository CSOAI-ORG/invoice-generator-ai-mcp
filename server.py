#!/usr/bin/env python3
"""MEOK AI Labs — invoice-generator-ai-mcp MCP Server. Generate professional invoices with line items and totals."""

import json
import uuid
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from mcp.server.fastmcp import FastMCP
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

_store = {}

TEMPLATES = {
    "standard": {"header": "INVOICE", "footer": "Thank you for your business.", "columns": ["Item", "Qty", "Unit Price", "Total"]},
    "professional": {"header": "TAX INVOICE", "footer": "Payment due within 30 days. Thank you.", "columns": ["Description", "Quantity", "Rate", "Amount"]},
    "simple": {"header": "BILL", "footer": "Please pay promptly.", "columns": ["Item", "Amount"]},
    "freelancer": {"header": "INVOICE FOR SERVICES", "footer": "Payment due on receipt. Late fees may apply.", "columns": ["Service", "Hours", "Rate", "Total"]},
}

TAX_RATES = {"US": 0.0, "UK": 0.20, "AU": 0.10, "EU": 0.21, "CA": 0.13, "NZ": 0.15}

mcp = FastMCP("invoice-generator-ai", instructions="Generate, validate, and manage professional invoices with tax calculations.")


@mcp.tool()
def generate_invoice(client: str, items: list[dict], currency: str = "USD", tax_region: str = "US", template: str = "standard", due_days: int = 30, notes: str = "", api_key: str = "") -> str:
    """Generate a professional invoice. Each item needs 'description', 'qty', and 'price' keys."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    now = datetime.now(timezone.utc)
    invoice_id = f"INV-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    tax_rate = TAX_RATES.get(tax_region.upper(), 0.0)
    tmpl = TEMPLATES.get(template, TEMPLATES["standard"])

    line_items = []
    for item in items:
        qty = item.get("qty", 1)
        price = item.get("price", 0)
        line_total = round(qty * price, 2)
        line_items.append({
            "description": item.get("description", "Item"),
            "qty": qty,
            "unit_price": price,
            "line_total": line_total,
        })

    subtotal = round(sum(li["line_total"] for li in line_items), 2)
    tax_amount = round(subtotal * tax_rate, 2)
    total = round(subtotal + tax_amount, 2)

    invoice = {
        "invoice_id": invoice_id,
        "client": client,
        "date": now.isoformat(),
        "due_date": (now + timedelta(days=due_days)).strftime("%Y-%m-%d"),
        "template": template,
        "header": tmpl["header"],
        "items": line_items,
        "subtotal": subtotal,
        "tax_region": tax_region.upper(),
        "tax_rate": f"{tax_rate * 100:.1f}%",
        "tax_amount": tax_amount,
        "total": total,
        "currency": currency.upper(),
        "notes": notes,
        "footer": tmpl["footer"],
        "status": "draft",
    }

    _store[invoice_id] = invoice
    return json.dumps(invoice, indent=2)


@mcp.tool()
def calculate_totals(items: list[dict], tax_region: str = "US", discount_percent: float = 0, api_key: str = "") -> str:
    """Calculate subtotal, tax, discount, and grand total for a list of line items."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    tax_rate = TAX_RATES.get(tax_region.upper(), 0.0)
    line_totals = []
    for item in items:
        qty = item.get("qty", 1)
        price = item.get("price", 0)
        lt = round(qty * price, 2)
        line_totals.append({"description": item.get("description", "Item"), "line_total": lt})

    subtotal = round(sum(lt["line_total"] for lt in line_totals), 2)
    discount = round(subtotal * (discount_percent / 100), 2)
    after_discount = round(subtotal - discount, 2)
    tax = round(after_discount * tax_rate, 2)
    grand_total = round(after_discount + tax, 2)

    return json.dumps({
        "line_totals": line_totals,
        "subtotal": subtotal,
        "discount_percent": discount_percent,
        "discount_amount": discount,
        "after_discount": after_discount,
        "tax_rate": f"{tax_rate * 100:.1f}%",
        "tax_amount": tax,
        "grand_total": grand_total,
    }, indent=2)


@mcp.tool()
def validate_invoice(invoice: dict, api_key: str = "") -> str:
    """Validate an invoice dict for required fields, correct math, and common errors."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    errors = []
    warnings = []

    required = ["client", "items"]
    for field in required:
        if field not in invoice:
            errors.append(f"Missing required field: {field}")

    items = invoice.get("items", [])
    if not items:
        errors.append("Invoice has no line items")

    computed_subtotal = 0
    for i, item in enumerate(items):
        if "price" not in item and "unit_price" not in item:
            errors.append(f"Item {i+1} missing price")
        qty = item.get("qty", 1)
        price = item.get("price", item.get("unit_price", 0))
        if qty <= 0:
            warnings.append(f"Item {i+1} has non-positive quantity")
        if price < 0:
            errors.append(f"Item {i+1} has negative price")
        computed_subtotal += qty * price

    if "subtotal" in invoice:
        if abs(invoice["subtotal"] - computed_subtotal) > 0.01:
            errors.append(f"Subtotal mismatch: stated {invoice['subtotal']}, computed {round(computed_subtotal, 2)}")

    if "client" in invoice and not invoice["client"].strip():
        warnings.append("Client name is empty")

    return json.dumps({
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "computed_subtotal": round(computed_subtotal, 2),
    }, indent=2)


@mcp.tool()
def list_templates(api_key: str = "") -> str:
    """List all available invoice templates with their details."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://meok.ai/pricing"})
    if err := _rl(): return err

    templates = []
    for name, tmpl in TEMPLATES.items():
        templates.append({
            "name": name,
            "header": tmpl["header"],
            "columns": tmpl["columns"],
            "footer": tmpl["footer"],
        })

    return json.dumps({
        "templates": templates,
        "supported_tax_regions": {k: f"{v*100:.1f}%" for k, v in TAX_RATES.items()},
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
