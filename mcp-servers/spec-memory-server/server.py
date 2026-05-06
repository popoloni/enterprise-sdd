#!/usr/bin/env python3
"""
Specification Memory MCP Server
Manages persistent context for SDD workflow
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    TextContent,
    Tool,
)

MEMORY_PATH = Path(os.environ.get("SPEC_MEMORY_PATH", "./.specify/memory"))

server = Server("spec-memory")


@server.list_resources()
async def list_resources():
    resources = []

    constitution_path = MEMORY_PATH / "constitution.md"
    if constitution_path.exists():
        resources.append(
            Resource(
                uri="spec://memory/constitution",
                name="Project Constitution",
                description="Project-wide principles and standards",
                mimeType="text/markdown",
            )
        )

    context_path = MEMORY_PATH / "active-context.json"
    if context_path.exists():
        resources.append(
            Resource(
                uri="spec://memory/context",
                name="Active Feature Context",
                description="Current feature being worked on",
                mimeType="application/json",
            )
        )

    decisions_path = MEMORY_PATH / "decisions.md"
    if decisions_path.exists():
        resources.append(
            Resource(
                uri="spec://memory/decisions",
                name="Decisions Log",
                description="Cross-feature architectural decisions",
                mimeType="text/markdown",
            )
        )

    return resources


@server.read_resource()
async def read_resource(uri: str):
    resource_map = {
        "spec://memory/constitution": "constitution.md",
        "spec://memory/context": "active-context.json",
        "spec://memory/decisions": "decisions.md",
    }

    filename = resource_map.get(uri)
    if not filename:
        raise ValueError(f"Unknown resource: {uri}")

    file_path = MEMORY_PATH / filename
    content = file_path.read_text(encoding="utf-8")
    mime = "application/json" if filename.endswith(".json") else "text/markdown"

    return content, mime


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="set_active_feature",
            description="Set the currently active feature for context",
            inputSchema={
                "type": "object",
                "properties": {
                    "featureId": {
                        "type": "string",
                        "description": "Feature ID (e.g., 001-user-auth)",
                    },
                    "phase": {
                        "type": "string",
                        "description": 'Current phase (e.g., "1.2-spec", "2.1-design")',
                    },
                },
                "required": ["featureId"],
            },
        ),
        Tool(
            name="get_active_feature",
            description="Get the currently active feature context",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="add_decision",
            description="Log an architectural decision",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Decision title"},
                    "context": {
                        "type": "string",
                        "description": "Why this decision was needed",
                    },
                    "decision": {
                        "type": "string",
                        "description": "What was decided",
                    },
                    "consequences": {
                        "type": "string",
                        "description": "Impact of this decision",
                    },
                    "featureId": {
                        "type": "string",
                        "description": "Related feature ID (optional)",
                    },
                },
                "required": ["title", "context", "decision"],
            },
        ),
        Tool(
            name="get_feature_artifacts",
            description="List all artifacts for a feature",
            inputSchema={
                "type": "object",
                "properties": {
                    "featureId": {"type": "string", "description": "Feature ID"},
                },
                "required": ["featureId"],
            },
        ),
        Tool(
            name="get_constitution_section",
            description="Get a specific section from the constitution",
            inputSchema={
                "type": "object",
                "properties": {
                    "article": {
                        "type": "string",
                        "description": 'Article number (e.g., "III" for quality standards)',
                    },
                },
                "required": ["article"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "set_active_feature":
        return await set_active_feature(arguments["featureId"], arguments.get("phase"))
    elif name == "get_active_feature":
        return await get_active_feature()
    elif name == "add_decision":
        return await add_decision(arguments)
    elif name == "get_feature_artifacts":
        return await get_feature_artifacts(arguments["featureId"])
    elif name == "get_constitution_section":
        return await get_constitution_section(arguments["article"])
    else:
        raise ValueError(f"Unknown tool: {name}")


async def set_active_feature(feature_id: str, phase: str | None = None):
    now = datetime.now(timezone.utc).isoformat()
    context = {
        "featureId": feature_id,
        "phase": phase or "unknown",
        "startedAt": now,
        "updatedAt": now,
    }

    MEMORY_PATH.mkdir(parents=True, exist_ok=True)
    context_path = MEMORY_PATH / "active-context.json"
    context_path.write_text(json.dumps(context, indent=2), encoding="utf-8")

    return [
        TextContent(
            type="text",
            text=f"Active feature set to {feature_id} (phase: {phase or 'unknown'})",
        )
    ]


async def get_active_feature():
    try:
        context_path = MEMORY_PATH / "active-context.json"
        content = context_path.read_text(encoding="utf-8")
        return [TextContent(type="text", text=content)]
    except FileNotFoundError:
        return [TextContent(type="text", text="No active feature set")]


async def add_decision(decision: dict):
    decisions_path = MEMORY_PATH / "decisions.md"

    try:
        content = decisions_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        content = "# Architectural Decisions Log\n\n"

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    feature_line = (
        f'**Feature:** {decision["featureId"]}\n' if decision.get("featureId") else ""
    )
    entry = f"""
## {decision["title"]}

**Date:** {date}
{feature_line}
### Context
{decision["context"]}

### Decision
{decision["decision"]}

### Consequences
{decision.get("consequences", "To be determined.")}

---
"""

    content += entry
    decisions_path.write_text(content, encoding="utf-8")

    return [TextContent(type="text", text=f'Decision logged: {decision["title"]}')]


async def get_feature_artifacts(feature_id: str):
    specs_dir = Path.cwd() / ".specify" / "specs" / feature_id

    try:
        artifacts = []
        for item in specs_dir.iterdir():
            if item.is_file():
                stat = item.stat()
                artifacts.append(
                    {
                        "name": item.name,
                        "path": str(item),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc
                        ).isoformat(),
                    }
                )
            elif item.is_dir():
                for sub_item in item.iterdir():
                    artifacts.append(
                        {"name": f"{item.name}/{sub_item.name}", "path": str(sub_item)}
                    )

        return [TextContent(type="text", text=json.dumps(artifacts, indent=2))]
    except FileNotFoundError:
        return [TextContent(type="text", text=f"Feature not found: {feature_id}")]


async def get_constitution_section(article: str):
    constitution_path = MEMORY_PATH / "constitution.md"

    try:
        content = constitution_path.read_text(encoding="utf-8")
        pattern = rf"## Article {re.escape(article)}[:\s].*?(?=## Article|$)"
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return [TextContent(type="text", text=match.group(0))]
        else:
            return [
                TextContent(
                    type="text", text=f"Article {article} not found in constitution"
                )
            ]
    except FileNotFoundError:
        return [TextContent(type="text", text="Constitution not found")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
