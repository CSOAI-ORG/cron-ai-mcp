# Cron AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Cron expression parsing, generation, scheduling, and human-readable explanations

## Installation

```bash
pip install cron-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `parse_cron`
Parse a cron expression into its components with validation. Supports @yearly, @monthly, @daily aliases.

**Parameters:**
- `expression` (str): Cron expression (5 fields or alias)

### `generate_cron`
Generate a cron expression from individual fields or common presets.

**Parameters:**
- `minute` (str): Minute field (default '*')
- `hour` (str): Hour field (default '*')
- `day_of_month` (str): Day field (default '*')
- `month` (str): Month field (default '*')
- `day_of_week` (str): Day of week field (default '*')
- `preset` (str): Preset — 'every_5min', 'every_hour', 'daily_midnight', 'weekly_monday', 'monthly_first', 'weekdays_9am', 'quarterly'

### `next_runs`
Calculate next N run times for a cron expression.

**Parameters:**
- `expression` (str): Cron expression
- `count` (int): Number of runs (default 5, max 50)
- `from_date` (str): Starting date

### `explain_cron`
Explain a cron expression in human-readable English with frequency estimates.

**Parameters:**
- `expression` (str): Cron expression

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
