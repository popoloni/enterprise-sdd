#!/usr/bin/env node

/**
 * Confluence MCP Server
 * Provides access to internal wiki documentation
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const CONFLUENCE_URL = process.env.CONFLUENCE_URL;
const CONFLUENCE_API_TOKEN = process.env.CONFLUENCE_API_TOKEN;
const CONFLUENCE_USER_EMAIL = process.env.CONFLUENCE_USER_EMAIL;

class ConfluenceMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'confluence-mcp',
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
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'search_confluence',
          description: 'Search Confluence wiki for relevant documentation',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Search query',
              },
              space: {
                type: 'string',
                description: 'Confluence space key (optional)',
              },
              limit: {
                type: 'number',
                description: 'Maximum results (default 10)',
              },
            },
            required: ['query'],
          },
        },
        {
          name: 'get_confluence_page',
          description: 'Get content of a specific Confluence page',
          inputSchema: {
            type: 'object',
            properties: {
              pageId: {
                type: 'string',
                description: 'Confluence page ID',
              },
            },
            required: ['pageId'],
          },
        },
        {
          name: 'list_space_pages',
          description: 'List all pages in a Confluence space',
          inputSchema: {
            type: 'object',
            properties: {
              spaceKey: {
                type: 'string',
                description: 'Confluence space key',
              },
            },
            required: ['spaceKey'],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'search_confluence':
          return this.searchConfluence(args.query, args.space, args.limit);
        case 'get_confluence_page':
          return this.getPage(args.pageId);
        case 'list_space_pages':
          return this.listSpacePages(args.spaceKey);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async confluenceRequest(endpoint, params = {}) {
    const url = new URL(`${CONFLUENCE_URL}/rest/api${endpoint}`);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, value);
      }
    });

    const auth = Buffer.from(
      `${CONFLUENCE_USER_EMAIL}:${CONFLUENCE_API_TOKEN}`
    ).toString('base64');

    const response = await fetch(url.toString(), {
      headers: {
        Authorization: `Basic ${auth}`,
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Confluence API error: ${response.status}`);
    }

    return response.json();
  }

  async searchConfluence(query, space, limit = 10) {
    let cql = `text ~ "${query}"`;
    if (space) {
      cql += ` AND space = "${space}"`;
    }

    const data = await this.confluenceRequest('/content/search', {
      cql,
      limit,
      expand: 'body.storage',
    });

    const results = data.results.map((page) => ({
      id: page.id,
      title: page.title,
      space: page.space?.key,
      excerpt: this.extractText(page.body?.storage?.value).slice(0, 500),
      url: `${CONFLUENCE_URL}${page._links.webui}`,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(results, null, 2),
        },
      ],
    };
  }

  async getPage(pageId) {
    const data = await this.confluenceRequest(`/content/${pageId}`, {
      expand: 'body.storage,version',
    });

    const content = this.extractText(data.body?.storage?.value);

    return {
      content: [
        {
          type: 'text',
          text: `# ${data.title}\n\n${content}`,
        },
      ],
    };
  }

  async listSpacePages(spaceKey) {
    const data = await this.confluenceRequest('/content', {
      spaceKey,
      type: 'page',
      limit: 100,
    });

    const pages = data.results.map((page) => ({
      id: page.id,
      title: page.title,
      url: `${CONFLUENCE_URL}${page._links.webui}`,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(pages, null, 2),
        },
      ],
    };
  }

  extractText(html) {
    if (!html) return '';
    return html
      .replace(/<[^>]*>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Confluence MCP server running');
  }
}

const server = new ConfluenceMCPServer();
server.run().catch(console.error);
