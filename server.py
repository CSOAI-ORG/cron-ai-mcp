"""Cron AI MCP Server — Cron expression tools."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import time
from datetime import datetime, timedelta
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cron-ai-mcp")
_calls: dict[str, list[float]] = {}
DAILY_LIMIT = 50

def _rate_check(tool: str) -> bool:
    now = time.time()
    _calls.setdefault(tool, [])
    _calls[tool] = [t for t in _calls[tool] if t > now - 86400]
    if len(_calls[tool]) >= DAILY_LIMIT:
        return False
    _calls[tool].append(now)
    return True

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
MONTH_NAMES = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
               7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
DOW_NAMES = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

def _expand_field(field: str, min_val: int, max_val: int) -> list[int]:
    """Expand a cron field to list of valid values."""
    if field == "*":
        return list(range(min_val, max_val + 1))
    values = set()
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            if base == "*":
                start = min_val
            elif "-" in base:
                start = int(base.split("-")[0])
            else:
                start = int(base)
            for v in range(start, max_val + 1, step):
                values.add(v)
        elif "-" in part:
            lo, hi = part.split("-", 1)
            for v in range(int(lo), int(hi) + 1):
                values.add(v)
        else:
            values.add(int(part))
    return sorted(v for v in values if min_val <= v <= max_val)

@mcp.tool()
def parse_cron(expression: str, api_key: str = "") -> dict[str, Any]:
    """Parse a cron expression into its components with validation."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("parse_cron"):
        return {"error": "Rate limit exceeded (50/day)"}
    # Handle common aliases
    aliases = {"@yearly": "0 0 1 1 *", "@annually": "0 0 1 1 *", "@monthly": "0 0 1 * *",
               "@weekly": "0 0 * * 0", "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
               "@hourly": "0 * * * *"}
    expr = aliases.get(expression.lower(), expression)
    parts = expr.split()
    if len(parts) != 5:
        return {"error": f"Expected 5 fields, got {len(parts)}. Format: minute hour day_of_month month day_of_week"}
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
    fields = {}
    for i, (name, (lo, hi)) in enumerate(zip(FIELD_NAMES, ranges)):
        try:
            expanded = _expand_field(parts[i], lo, hi)
            fields[name] = {"raw": parts[i], "values": expanded, "count": len(expanded)}
        except (ValueError, IndexError) as e:
            return {"error": f"Invalid {name} field '{parts[i]}': {e}"}
    return {"expression": expression, "normalized": expr, "fields": fields, "is_valid": True}

@mcp.tool()
def generate_cron(minute: str = "*", hour: str = "*", day_of_month: str = "*", month: str = "*", day_of_week: str = "*", preset: str = "", api_key: str = "") -> dict[str, Any]:
    """Generate a cron expression. Use preset for common schedules: every_5min, every_hour, daily_midnight, weekly_monday, monthly_first, weekdays_9am."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("generate_cron"):
        return {"error": "Rate limit exceeded (50/day)"}
    presets = {
        "every_5min": ("*/5", "*", "*", "*", "*", "Every 5 minutes"),
        "every_15min": ("*/15", "*", "*", "*", "*", "Every 15 minutes"),
        "every_hour": ("0", "*", "*", "*", "*", "Every hour at :00"),
        "daily_midnight": ("0", "0", "*", "*", "*", "Daily at midnight"),
        "daily_noon": ("0", "12", "*", "*", "*", "Daily at noon"),
        "weekly_monday": ("0", "0", "*", "*", "1", "Every Monday at midnight"),
        "monthly_first": ("0", "0", "1", "*", "*", "First day of every month"),
        "weekdays_9am": ("0", "9", "*", "*", "1-5", "Weekdays at 9am"),
        "quarterly": ("0", "0", "1", "1,4,7,10", "*", "First day of each quarter"),
    }
    if preset:
        if preset not in presets:
            return {"error": f"Unknown preset. Available: {', '.join(presets)}"}
        m, h, dom, mon, dow, desc = presets[preset]
        expr = f"{m} {h} {dom} {mon} {dow}"
        return {"expression": expr, "preset": preset, "description": desc}
    expr = f"{minute} {hour} {day_of_month} {month} {day_of_week}"
    return {"expression": expr, "fields": {"minute": minute, "hour": hour, "day_of_month": day_of_month, "month": month, "day_of_week": day_of_week}}

@mcp.tool()
def next_runs(expression: str, count: int = 5, from_date: str = "", api_key: str = "") -> dict[str, Any]:
    """Calculate next N run times for a cron expression."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("next_runs"):
        return {"error": "Rate limit exceeded (50/day)"}
    if count < 1 or count > 50:
        return {"error": "Count must be 1-50"}
    aliases = {"@yearly": "0 0 1 1 *", "@annually": "0 0 1 1 *", "@monthly": "0 0 1 * *",
               "@weekly": "0 0 * * 0", "@daily": "0 0 * * *", "@hourly": "0 * * * *"}
    expr = aliases.get(expression.lower(), expression)
    parts = expr.split()
    if len(parts) != 5:
        return {"error": "Invalid cron expression"}
    try:
        ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
        expanded = [_expand_field(parts[i], lo, hi) for i, (lo, hi) in enumerate(ranges)]
    except (ValueError, IndexError):
        return {"error": "Invalid cron expression"}
    if from_date:
        try:
            current = datetime.fromisoformat(from_date)
        except ValueError:
            current = datetime.now()
    else:
        current = datetime.now()
    current = current.replace(second=0, microsecond=0) + timedelta(minutes=1)
    runs = []
    max_iter = 525960  # ~1 year of minutes
    for _ in range(max_iter):
        dow = current.weekday()
        dow_cron = (dow + 1) % 7  # cron: 0=Sun
        if (current.minute in expanded[0] and current.hour in expanded[1] and
            current.day in expanded[2] and current.month in expanded[3] and
            (dow_cron in expanded[4] or 7 in expanded[4] and dow_cron == 0)):
            runs.append(current.isoformat())
            if len(runs) >= count:
                break
        current += timedelta(minutes=1)
    return {"expression": expression, "next_runs": runs, "count": len(runs)}

@mcp.tool()
def explain_cron(expression: str, api_key: str = "") -> dict[str, Any]:
    """Explain a cron expression in human-readable English."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    if not _rate_check("explain_cron"):
        return {"error": "Rate limit exceeded (50/day)"}
    aliases = {"@yearly": "0 0 1 1 *", "@annually": "0 0 1 1 *", "@monthly": "0 0 1 * *",
               "@weekly": "0 0 * * 0", "@daily": "0 0 * * *", "@hourly": "0 * * * *"}
    expr = aliases.get(expression.lower(), expression)
    parts = expr.split()
    if len(parts) != 5:
        return {"error": "Invalid cron expression"}
    descriptions = []
    # Minute
    if parts[0] == "*": descriptions.append("every minute")
    elif "/" in parts[0]: descriptions.append(f"every {parts[0].split('/')[1]} minutes")
    else: descriptions.append(f"at minute {parts[0]}")
    # Hour
    if parts[1] == "*": descriptions.append("of every hour")
    elif "/" in parts[1]: descriptions.append(f"every {parts[1].split('/')[1]} hours")
    else: descriptions.append(f"at hour {parts[1]}")
    # Day of month
    if parts[2] != "*":
        descriptions.append(f"on day {parts[2]} of the month")
    # Month
    if parts[3] != "*":
        try:
            months = _expand_field(parts[3], 1, 12)
            month_names = [MONTH_NAMES.get(m, str(m)) for m in months]
            descriptions.append(f"in {', '.join(month_names)}")
        except ValueError:
            descriptions.append(f"in month {parts[3]}")
    # Day of week
    if parts[4] != "*":
        try:
            days = _expand_field(parts[4], 0, 7)
            day_names = [DOW_NAMES.get(d % 7, str(d)) for d in days]
            descriptions.append(f"on {', '.join(day_names)}")
        except ValueError:
            descriptions.append(f"on weekday {parts[4]}")
    human = "Runs " + ", ".join(descriptions) + "."
    # Frequency estimate
    try:
        ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
        expanded = [_expand_field(parts[i], lo, hi) for i, (lo, hi) in enumerate(ranges)]
        per_day = len(expanded[0]) * len(expanded[1])
        per_month = per_day * len(expanded[2])
    except ValueError:
        per_day = per_month = 0
    return {"expression": expression, "human_readable": human, "parts": descriptions, "estimated_runs_per_day": per_day, "estimated_runs_per_month": per_month}

if __name__ == "__main__":
    mcp.run()
