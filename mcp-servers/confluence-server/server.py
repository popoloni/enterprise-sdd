#!/usr/bin/env python3
"""
Confluence MCP Server
Provides access to internal wiki documentation
"""

import base64
import json
import os
import re
import sys
from urllib.parse import urlencode

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

CONFLUENCE_URL = os.environ.get("CONFLUENCE_URL", "")
CONFLUENCE_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN", "")
CONFLUENCE_USER_EMAIL = os.environ.get("CONFLUENCE_USER_EMAIL", "")

server = Server("confluence-mcp")


def _auth_header() -> str:
    credentials = f"{CONFLUENCE_USER_EMAIL}:{CONFLUENCE_API_TOKEN}"
    return "Basic " + base64.b64encode(credentials.encode()).decode()


def _sanitize_cql_value(value: str) -> str:
    """Escape special CQL characters to prevent injection."""
    # Remove characters that could break out of CQL string literals
    return value.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")


async def _confluence_request(endpoint: str, params: dict | None = None) -> dict:
    url = f"{CONFLUENCE_URL}/rest/api{endpoint}"
    headers = {"Authorization": _auth_header(), "Accept": "application/json"}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, params=params or {}, headers=headers)
        resp.raise_for_status()
        return resp.json()


def _extract_text(html: str | None) -> str:
    if not html:
        return ""
    text = re.sub(r"<[^>]*>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_confluence",
            description="Search Confluence wiki for relevant documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "space": {
                        "type": "string",
                        "description": "Confluence space key (optional)",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results (default 10)",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_confluence_page",
            description="Get content of a specific Confluence page",
            inputSchema={
                "type": "object",
                "properties": {
                    "pageId": {
                        "type": "string",
                        "description": "Confluence page ID",
                    },
                },
                "required": ["pageId"],
            },
        ),
        Tool(
            name="list_space_pages",
            description="List all pages in a Confluence space",
            inputSchema={
                "type": "object",
                "properties": {
                    "spaceKey": {
                        "type": "string",
                        "description": "Confluence space key",
                    },
                },
                "required": ["spaceKey"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_confluence":
        return await search_confluence(
            arguments["query"], arguments.get("space"), arguments.get("limit", 10)
        )
    elif name == "get_confluence_page":
        return await get_page(arguments["pageId"])
    elif name == "list_space_pages":
        return await list_space_pages(arguments["spaceKey"])
    else:
        raise ValueError(f"Unknown tool: {name}")


async def search_confluence(query: str, space: str | None = None, limit: int = 10):
    safe_query = _sanitize_cql_value(query)
    cql = f'text ~ "{safe_query}"'
    if space:
        safe_space = _sanitize_cql_value(space)
        cql += f' AND space = "{safe_space}"'

    data = await _confluence_request(
        "/content/search", {"cql": cql, "limit": limit, "expand": "body.storage"}
    )

    results = [
        {
            "id": page["id"],
            "title": page["title"],
            "space": page.get("space", {}).get("key"),
            "excerpt": _extract_text(
                page.get("body", {}).get("storage", {}).get("value")
            )[:500],
            "url": f'{CONFLUENCE_URL}{page["_links"]["webui"]}',
        }
        for page in data.get("results", [])
    ]

    return [TextContent(type="text", text=json.dumps(results, indent=2))]


async def get_page(page_id: str):
    data = await _confluence_request(
        f"/content/{page_id}", {"expand": "body.storage,version"}
    )

    content = _extract_text(data.get("body", {}).get("storage", {}).get("value"))
    return [TextContent(type="text", text=f'# {data["title"]}\n\n{content}')]


async def list_space_pages(space_key: str):
    data = await _confluence_request(
        "/content", {"spaceKey": space_key, "type": "page", "limit": 100}
    )

    pages = [
        {
            "id": page["id"],
            "title": page["title"],
            "url": f'{CONFLUENCE_URL}{page["_links"]["webui"]}',
        }
        for page in data.get("results", [])
    ]

    return [TextContent(type="text", text=json.dumps(pages, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
