#!/usr/bin/env node

/**
 * Jira MCP Server
 * Provides access to Jira issues for requirement traceability
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const JIRA_URL = process.env.JIRA_URL;
const JIRA_API_TOKEN = process.env.JIRA_API_TOKEN;
const JIRA_USER_EMAIL = process.env.JIRA_USER_EMAIL;

class JiraMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'jira-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'get_issue',
          description: 'Get details of a Jira issue',
          inputSchema: {
            type: 'object',
            properties: {
              issueKey: {
                type: 'string',
                description: 'Jira issue key (e.g., PROJ-123)',
              },
            },
            required: ['issueKey'],
          },
        },
        {
          name: 'search_issues',
          description: 'Search Jira issues using JQL',
          inputSchema: {
            type: 'object',
            properties: {
              jql: {
                type: 'string',
                description: 'JQL query string',
              },
              maxResults: {
                type: 'number',
                description: 'Maximum results (default 20)',
              },
            },
            required: ['jql'],
          },
        },
        {
          name: 'get_epic_stories',
          description: 'Get all stories in an epic',
          inputSchema: {
            type: 'object',
            properties: {
              epicKey: {
                type: 'string',
                description: 'Epic issue key',
              },
            },
            required: ['epicKey'],
          },
        },
        {
          name: 'get_sprint_issues',
          description: 'Get issues in a sprint',
          inputSchema: {
            type: 'object',
            properties: {
              sprintId: {
                type: 'string',
                description: 'Sprint ID',
              },
            },
            required: ['sprintId'],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'get_issue':
          return this.getIssue(args.issueKey);
        case 'search_issues':
          return this.searchIssues(args.jql, args.maxResults);
        case 'get_epic_stories':
          return this.getEpicStories(args.epicKey);
        case 'get_sprint_issues':
          return this.getSprintIssues(args.sprintId);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async jiraRequest(endpoint, method = 'GET', body = null) {
    const url = `${JIRA_URL}/rest/api/3${endpoint}`;
    const auth = Buffer.from(
      `${JIRA_USER_EMAIL}:${JIRA_API_TOKEN}`
    ).toString('base64');

    const options = {
      method,
      headers: {
        Authorization: `Basic ${auth}`,
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`Jira API error: ${response.status}`);
    }

    return response.json();
  }

  async getIssue(issueKey) {
    const data = await this.jiraRequest(
      `/issue/${issueKey}?expand=renderedFields`
    );

    const issue = {
      key: data.key,
      summary: data.fields.summary,
      description: data.renderedFields?.description || data.fields.description,
      status: data.fields.status?.name,
      type: data.fields.issuetype?.name,
      priority: data.fields.priority?.name,
      assignee: data.fields.assignee?.displayName,
      reporter: data.fields.reporter?.displayName,
      labels: data.fields.labels,
      created: data.fields.created,
      updated: data.fields.updated,
      acceptanceCriteria: data.fields.customfield_10001, // Adjust field ID
    };

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(issue, null, 2),
        },
      ],
    };
  }

  async searchIssues(jql, maxResults = 20) {
    const data = await this.jiraRequest(
      `/search?jql=${encodeURIComponent(jql)}&maxResults=${maxResults}`
    );

    const issues = data.issues.map((issue) => ({
      key: issue.key,
      summary: issue.fields.summary,
      status: issue.fields.status?.name,
      type: issue.fields.issuetype?.name,
      assignee: issue.fields.assignee?.displayName,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(issues, null, 2),
        },
      ],
    };
  }

  async getEpicStories(epicKey) {
    const jql = `"Epic Link" = ${epicKey} OR parent = ${epicKey}`;
    return this.searchIssues(jql, 100);
  }

  async getSprintIssues(sprintId) {
    const jql = `Sprint = ${sprintId}`;
    return this.searchIssues(jql, 100);
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Jira MCP server running');
  }
}

const server = new JiraMCPServer();
server.run().catch(console.error);
