<div align="center">

# Invoice Generator Ai MCP

**MCP server for invoice generator ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-invoice-generator-ai-mcp)](https://pypi.org/project/meok-invoice-generator-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Invoice Generator Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `generate_invoice` | Generate a professional invoice. Each item needs 'description', 'qty', and 'pric |
| `calculate_totals` | Calculate subtotal, tax, discount, and grand total for a list of line items. |
| `validate_invoice` | Validate an invoice dict for required fields, correct math, and common errors. |
| `list_templates` | List all available invoice templates with their details. |

## Installation

```bash
pip install meok-invoice-generator-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "invoice-generator-ai": {
      "command": "python",
      "args": ["-m", "meok_invoice_generator_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
