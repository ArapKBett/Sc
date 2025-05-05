def format_message(content, source, max_length=2000):
    """Format a message with content and source, respecting max length."""
    message = f"{content}\n\nSource: {source}"
    if len(message) > max_length:
        message = message[:max_length-3] + "..."
    return message

CATEGORIES = [
    "red_teaming", "blue_teaming", "soc_analysis", "ethical_hacking",
    "threat_intelligence", "forensics", "system_administration"
]
