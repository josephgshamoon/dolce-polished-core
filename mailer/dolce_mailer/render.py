"""Merge-field rendering. Placeholders: {{first_name}}, {{unsubscribe_url}}."""
from . import config


def render(html: str, contact) -> str:
    first = (contact["first_name"] or "").strip() or "there"
    unsub = f"{config.APP_BASE_URL}/unsubscribe/{contact['unsub_token']}"
    logo = f"{config.APP_BASE_URL}/static/dolce-logo.jpg"
    return (html.replace("{{first_name}}", first)
                .replace("{{unsubscribe_url}}", unsub)
                .replace("{{logo_url}}", logo))
