"""Collections and their fields. The API and the dashboard UI are both generated from this, so adding a field
here is all it takes. Field spec: (name, type, extra) with type in text|longtext|number|date|select|bool."""
from __future__ import annotations

COLLECTIONS: dict[str, dict] = {
    "tasks": {"label": "Tasks", "fields": [
        ("title", "text", {}), ("area", "select", {"options": ["Career", "Money", "Health", "Learning", "YouTube", "Research", "Life"]}),
        ("priority", "select", {"options": ["P1", "P2", "P3"]}), ("due", "date", {}),
        ("status", "select", {"options": ["todo", "doing", "done"]}), ("notes", "longtext", {})]},
    "books": {"label": "Books", "fields": [
        ("title", "text", {}), ("author", "text", {}), ("why", "longtext", {}),
        ("category", "select", {"options": ["Money", "Mindset", "Career/Tech", "People", "Health", "Business"]}),
        ("total_pages", "number", {}), ("pages_read", "number", {}), ("daily_pages", "number", {}),
        ("status", "select", {"options": ["reading", "queued", "done"]})]},
    "workouts": {"label": "Workout plan", "fields": [
        ("day", "select", {"options": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}), ("name", "text", {}),
        ("details", "longtext", {}), ("minutes", "number", {})]},
    "purchases": {"label": "Purchases", "fields": [
        ("date", "date", {}), ("merchant", "text", {}), ("amount", "number", {}), ("category", "text", {}),
        ("card", "text", {}), ("need_or_want", "select", {"options": ["need", "want"]})]},
    "cards": {"label": "Credit cards", "fields": [
        ("name", "text", {}), ("balance", "number", {}), ("limit", "number", {}), ("apr", "number", {}),
        ("min_payment", "number", {}), ("due_day", "number", {})]},
    "investments": {"label": "Investments", "fields": [
        ("symbol", "text", {}), ("account", "text", {}), ("quantity", "number", {}), ("cost_basis", "number", {}),
        ("price", "number", {}), ("kind", "select", {"options": ["stock", "ETF", "crypto", "401k", "cash", "other"]})]},
    "risks": {"label": "Risks", "fields": [
        ("risk", "text", {}), ("area", "select", {"options": ["Money", "Career", "Health", "Legal", "Life"]}),
        ("likelihood", "number", {"min": 1, "max": 5}), ("impact", "number", {"min": 1, "max": 5}),
        ("mitigation", "longtext", {}), ("status", "select", {"options": ["open", "mitigating", "closed"]})]},
    "income": {"label": "Ways to earn", "fields": [
        ("idea", "text", {}), ("monthly_potential", "number", {}), ("effort", "select", {"options": ["low", "medium", "high"]}),
        ("first_step", "longtext", {}), ("status", "select", {"options": ["idea", "testing", "earning", "dropped"]}),
        ("earned_to_date", "number", {})]},
    "youtube": {"label": "YouTube", "fields": [
        ("channel", "text", {}), ("video_title", "text", {}), ("hook", "longtext", {}),
        ("status", "select", {"options": ["idea", "scripted", "recorded", "edited", "published"]}),
        ("publish_date", "date", {}), ("views", "number", {})]},
    "research": {"label": "Research", "fields": [
        ("topic", "text", {}), ("question", "longtext", {}), ("method", "longtext", {}), ("venue", "text", {}),
        ("status", "select", {"options": ["idea", "reading", "experimenting", "writing", "submitted", "published"]})]},
    "goals": {"label": "Goals", "fields": [
        ("goal", "text", {}), ("area", "text", {}), ("target", "number", {}), ("current", "number", {}),
        ("unit", "text", {}), ("deadline", "date", {})]},
}

FIELD_NAMES = {c: [f[0] for f in spec["fields"]] for c, spec in COLLECTIONS.items()}
