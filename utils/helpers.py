import json
from datetime import datetime

def format_datetime(value, format="%Y-%m-%d"):
    """Jinja filter to format a datetime object."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

def get_risk_badge_class(risk_level):
    """Return styling class for a risk level."""
    level = str(risk_level).lower().strip()
    if level == 'high':
        return 'danger'
    elif level == 'medium':
        return 'warning'
    return 'success'

def get_risk_percentage(prob):
    """Format risk probability decimal as a percentage."""
    try:
        return f"{float(prob) * 100:.1f}%"
    except (ValueError, TypeError):
        return "N/A"

def parse_json_safely(data_str):
    """Safely parse a JSON string or return an empty dict/list on failure."""
    if not data_str:
        return {}
    try:
        return json.loads(data_str)
    except (json.JSONDecodeError, TypeError):
        return {}

def calculate_change(current, previous):
    """Calculate directional change and return arrow details."""
    if current is None or previous is None:
        return "neutral", "→ No change"
    
    diff = current - previous
    if diff > 0.05: # Risk increased significantly
        return "negative", f"↑ Increased by {diff*100:.1f}%"
    elif diff < -0.05: # Risk decreased significantly
        return "positive", f"↓ Decreased by {abs(diff)*100:.1f}%"
    else:
        return "neutral", "→ Stable"
