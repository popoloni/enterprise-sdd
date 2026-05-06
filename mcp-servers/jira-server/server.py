#!/usr/bin/env python3
"""
Jira MCP Server
Provides access to Jira issues for requirement traceability
"""

import base64
import json
import os
import sys
from urllib.parse import quote

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

JIRA_URL = os.environ.get("JIRA_URL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")
JIRA_USER_EMAIL = os.environ.get("JIRA_USER_EMAIL", "")

server = Server("jira-mcp")


def _auth_header() -> str:
    credentials = f"{JIRA_USER_EMAIL}:{JIRA_API_TOKEN}"
    return "Basic " + base64.b64encode(credentials.encode()).decode()


async def _jira_request(endpoint: str, method: str = "GET", body: dict | None = None) -> dict:
    url = f"{JIRA_URL}/rest/api/3{endpoint}"
    headers = {
        "Authorization": _auth_header(),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        if method == "GET":
            resp = await client.get(url, headers=headers)
        else:
            resp = await client.request(method, url, headers=headers, json=body)
        resp.raise_for_status()
        return resp.json()


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_issue",
            description="Get details of a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issueKey": {
                        "type": "string",
                        "description": "Jira issue key (e.g., PROJ-123)",
                    },
                },
                "required": ["issueKey"],
            },
        ),
        Tool(
            name="search_issues",
            description="Search Jira issues using JQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {"type": "string", "description": "JQL query string"},
                    "maxResults": {
                        "type": "number",
                        "description": "Maximum results (default 20)",
                    },
                },
                "required": ["jql"],
            },
        ),
        Tool(
            name="get_epic_stories",
            description="Get all stories in an epic",
            inputSchema={
                "type": "object",
                "properties": {
                    "epicKey": {
                        "type": "string",
                        "description": "Epic issue key",
                    },
                },
                "required": ["epicKey"],
            },
        ),
        Tool(
            name="get_sprint_issues",
            description="Get issues in a sprint",
            inputSchema={
                "type": "object",
                "properties": {
                    "sprintId": {
                        "type": "string",
                        "description": "Sprint ID",
                    },
                },
                "required": ["sprintId"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_issue":
        return await get_issue(arguments["issueKey"])
    elif name == "search_issues":
        return await search_issues(arguments["jql"], arguments.get("maxResults", 20))
    elif name == "get_epic_stories":
        return await get_epic_stories(arguments["epicKey"])
    elif name == "get_sprint_issues":
        return await get_sprint_issues(arguments["sprintId"])
    else:
        raise ValueError(f"Unknown tool: {name}")


async def get_issue(issue_key: str):
    data = await _jira_request(f"/issue/{issue_key}?expand=renderedFields")

    fields = data.get("fields", {})
    issue = {
        "key": data["key"],
        "summary": fields.get("summary"),
        "description": data.get("renderedFields", {}).get("description")
        or fields.get("description"),
        "status": (fields.get("status") or {}).get("name"),
        "type": (fields.get("issuetype") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "assignee": (fields.get("assignee") or {}).get("displayName"),
        "reporter": (fields.get("reporter") or {}).get("displayName"),
        "labels": fields.get("labels", []),
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "acceptanceCriteria": fields.get("customfield_10001"),
    }

    return [TextContent(type="text", text=json.dumps(issue, indent=2))]


async def search_issues(jql: str, max_results: int = 20):
    data = await _jira_request(
        f"/search?jql={quote(jql)}&maxResults={max_results}"
    )

    issues = [
        {
            "key": issue["key"],
            "summary": issue["fields"].get("summary"),
            "status": (issue["fields"].get("status") or {}).get("name"),
            "type": (issue["fields"].get("issuetype") or {}).get("name"),
            "assignee": (issue["fields"].get("assignee") or {}).get("displayName"),
        }
        for issue in data.get("issues", [])
    ]

    return [TextContent(type="text", text=json.dumps(issues, indent=2))]


async def get_epic_stories(epic_key: str):
    jql = f'"Epic Link" = {epic_key} OR parent = {epic_key}'
    return await search_issues(jql, 100)


async def get_sprint_issues(sprint_id: str):
    jql = f"Sprint = {sprint_id}"
    return await search_issues(jql, 100)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
