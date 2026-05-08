<div align="center">

# Cron Ai MCP

**Cron AI MCP Server — Cron expression tools.**

[![PyPI](https://img.shields.io/pypi/v/meok-cron-ai-mcp)](https://pypi.org/project/meok-cron-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Cron AI MCP Server — Cron expression tools.

## Tools

| Tool | Description |
|------|-------------|
| `parse_cron` | Parse a cron expression into its components with validation. |
| `generate_cron` | Generate a cron expression. Use preset for common schedules: every_5min, every_h |
| `next_runs` | Calculate next N run times for a cron expression. |
| `explain_cron` | Explain a cron expression in human-readable English. |

## Installation

```bash
pip install meok-cron-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "cron-ai": {
      "command": "python",
      "args": ["-m", "meok_cron_ai_mcp.server"]
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
