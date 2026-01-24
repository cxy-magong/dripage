# MCP Server Configuration

This directory contains configuration files for the Dripage MCP server.

## Files

### `mcp_config.yaml`
Main configuration file for the MCP server.

**Configuration options:**

```yaml
browser:
  address: "127.0.0.1:19222"  # Browser connection address

output:
  directory: "output"              # Output directory (relative to project root)
  images_subdir: "images"          # Screenshot subdirectory

vision:
  model: "glm-4v-flash"           # Default vision model
  temperature: 0.7                 # Temperature for vision API
  max_tokens: 1024                 # Max tokens for vision API
```

### `mcporter.json`
Configuration for mcporter using STDIO transport.

### `mcporter-http.json`
Configuration for mcporter using HTTP transport (for testing).

### `models_config.yaml`
Model configuration for vision and AI tools.
