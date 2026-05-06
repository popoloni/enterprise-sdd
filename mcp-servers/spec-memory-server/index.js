#!/usr/bin/env node

/**
 * Specification Memory MCP Server
 * Manages persistent context for SDD workflow
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs/promises';
import path from 'path';

const MEMORY_PATH = process.env.SPEC_MEMORY_PATH || './.specify/memory';

class SpecMemoryServer {
  constructor() {
    this.server = new Server(
      {
        name: 'spec-memory',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
        },
      }
    );

    this.setupHandlers();
  }

  setupHandlers() {
    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      const resources = [];

      // Constitution
      const constitutionPath = path.join(MEMORY_PATH, 'constitution.md');
      try {
        await fs.access(constitutionPath);
        resources.push({
          uri: 'spec://memory/constitution',
          name: 'Project Constitution',
          description: 'Project-wide principles and standards',
          mimeType: 'text/markdown',
        });
      } catch {}

      // Active feature context
      const contextPath = path.join(MEMORY_PATH, 'active-context.json');
      try {
        await fs.access(contextPath);
        resources.push({
          uri: 'spec://memory/context',
          name: 'Active Feature Context',
          description: 'Current feature being worked on',
          mimeType: 'application/json',
        });
      } catch {}

      // Decisions log
      const decisionsPath = path.join(MEMORY_PATH, 'decisions.md');
      try {
        await fs.access(decisionsPath);
        resources.push({
          uri: 'spec://memory/decisions',
          name: 'Decisions Log',
          description: 'Cross-feature architectural decisions',
          mimeType: 'text/markdown',
        });
      } catch {}

      return { resources };
    });

    // Read resource content
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;

      const resourceMap = {
        'spec://memory/constitution': 'constitution.md',
        'spec://memory/context': 'active-context.json',
        'spec://memory/decisions': 'decisions.md',
      };

      const filename = resourceMap[uri];
      if (!filename) {
        throw new Error(`Unknown resource: ${uri}`);
      }

      const filePath = path.join(MEMORY_PATH, filename);
      const content = await fs.readFile(filePath, 'utf-8');

      return {
        contents: [
          {
            uri,
            mimeType: filename.endsWith('.json')
              ? 'application/json'
              : 'text/markdown',
            text: content,
          },
        ],
      };
    });

    // List tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'set_active_feature',
          description: 'Set the currently active feature for context',
          inputSchema: {
            type: 'object',
            properties: {
              featureId: {
                type: 'string',
                description: 'Feature ID (e.g., 001-user-auth)',
              },
              phase: {
                type: 'string',
                description: 'Current phase (e.g., "1.2-spec", "2.1-design")',
              },
            },
            required: ['featureId'],
          },
        },
        {
          name: 'get_active_feature',
          description: 'Get the currently active feature context',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'add_decision',
          description: 'Log an architectural decision',
          inputSchema: {
            type: 'object',
            properties: {
              title: {
                type: 'string',
                description: 'Decision title',
              },
              context: {
                type: 'string',
                description: 'Why this decision was needed',
              },
              decision: {
                type: 'string',
                description: 'What was decided',
              },
              consequences: {
                type: 'string',
                description: 'Impact of this decision',
              },
              featureId: {
                type: 'string',
                description: 'Related feature ID (optional)',
              },
            },
            required: ['title', 'context', 'decision'],
          },
        },
        {
          name: 'get_feature_artifacts',
          description: 'List all artifacts for a feature',
          inputSchema: {
            type: 'object',
            properties: {
              featureId: {
                type: 'string',
                description: 'Feature ID',
              },
            },
            required: ['featureId'],
          },
        },
        {
          name: 'get_constitution_section',
          description: 'Get a specific section from the constitution',
          inputSchema: {
            type: 'object',
            properties: {
              article: {
                type: 'string',
                description: 'Article number (e.g., "III" for quality standards)',
              },
            },
            required: ['article'],
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'set_active_feature':
          return this.setActiveFeature(args.featureId, args.phase);
        case 'get_active_feature':
          return this.getActiveFeature();
        case 'add_decision':
          return this.addDecision(args);
        case 'get_feature_artifacts':
          return this.getFeatureArtifacts(args.featureId);
        case 'get_constitution_section':
          return this.getConstitutionSection(args.article);
        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    });
  }

  async setActiveFeature(featureId, phase) {
    const context = {
      featureId,
      phase: phase || 'unknown',
      startedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    await fs.mkdir(MEMORY_PATH, { recursive: true });
    const contextPath = path.join(MEMORY_PATH, 'active-context.json');
    await fs.writeFile(contextPath, JSON.stringify(context, null, 2));

    return {
      content: [
        {
          type: 'text',
          text: `Active feature set to ${featureId} (phase: ${phase || 'unknown'})`,
        },
      ],
    };
  }

  async getActiveFeature() {
    try {
      const contextPath = path.join(MEMORY_PATH, 'active-context.json');
      const content = await fs.readFile(contextPath, 'utf-8');
      return {
        content: [
          {
            type: 'text',
            text: content,
          },
        ],
      };
    } catch {
      return {
        content: [
          {
            type: 'text',
            text: 'No active feature set',
          },
        ],
      };
    }
  }

  async addDecision(decision) {
    const decisionsPath = path.join(MEMORY_PATH, 'decisions.md');
    
    let content = '';
    try {
      content = await fs.readFile(decisionsPath, 'utf-8');
    } catch {
      content = '# Architectural Decisions Log\n\n';
    }

    const date = new Date().toISOString().split('T')[0];
    const entry = `
## ${decision.title}

**Date:** ${date}
${decision.featureId ? `**Feature:** ${decision.featureId}` : ''}

### Context
${decision.context}

### Decision
${decision.decision}

### Consequences
${decision.consequences || 'To be determined.'}

---
`;

    content += entry;
    await fs.writeFile(decisionsPath, content);

    return {
      content: [
        {
          type: 'text',
          text: `Decision logged: ${decision.title}`,
        },
      ],
    };
  }

  async getFeatureArtifacts(featureId) {
    const specsDir = path.join(process.cwd(), '.specify', 'specs', featureId);
    
    try {
      const files = await fs.readdir(specsDir);
      const artifacts = [];

      for (const file of files) {
        const filePath = path.join(specsDir, file);
        const stat = await fs.stat(filePath);
        
        if (stat.isFile()) {
          artifacts.push({
            name: file,
            path: filePath,
            size: stat.size,
            modified: stat.mtime,
          });
        } else if (stat.isDirectory()) {
          const subFiles = await fs.readdir(filePath);
          for (const subFile of subFiles) {
            artifacts.push({
              name: `${file}/${subFile}`,
              path: path.join(filePath, subFile),
            });
          }
        }
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(artifacts, null, 2),
          },
        ],
      };
    } catch {
      return {
        content: [
          {
            type: 'text',
            text: `Feature not found: ${featureId}`,
          },
        ],
      };
    }
  }

  async getConstitutionSection(article) {
    const constitutionPath = path.join(MEMORY_PATH, 'constitution.md');
    
    try {
      const content = await fs.readFile(constitutionPath, 'utf-8');
      
      // Extract the requested article
      const articleRegex = new RegExp(
        `## Article ${article}[:\\s].*?(?=## Article|$)`,
        's'
      );
      const match = content.match(articleRegex);

      if (match) {
        return {
          content: [
            {
              type: 'text',
              text: match[0],
            },
          ],
        };
      } else {
        return {
          content: [
            {
              type: 'text',
              text: `Article ${article} not found in constitution`,
            },
          ],
        };
      }
    } catch {
      return {
        content: [
          {
            type: 'text',
            text: 'Constitution not found',
          },
        ],
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Spec Memory MCP server running');
  }
}

const server = new SpecMemoryServer();
server.run().catch(console.error);
