#!/usr/bin/env python3
"""MEOK AI Labs — invoice-generator-ai-mcp MCP Server. Generate professional invoices with line items and totals."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)
import mcp.types as types

# In-memory store (replace with DB in production)
_store = {}

server = Server("invoice-generator-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="create_invoice", description="Create an invoice", inputSchema={"type":"object","properties":{"client":{"type":"string"},"items":{"type":"array","items":{"type":"object"}}},"required":["client","items"]}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "create_invoice":
            total = sum(i.get("qty", 1) * i.get("price", 0) for i in args["items"])
            inv = {"client": args["client"], "total": total, "items": args["items"], "date": datetime.now().isoformat()}
            return [TextContent(type="text", text=json.dumps(inv, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="invoice-generator-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
