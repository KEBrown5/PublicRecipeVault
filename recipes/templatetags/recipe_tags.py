from django import template

register = template.Library()

@register.filter
def time_format(minutes):
    # Converts an int of minutes into a more readable format for display

    # Check that the value even exists
    if not minutes:
        return "0 mins"
    
    try:
        minutes = int(minutes)
    except (ValueError, TypeError):
        return ""
    
    hours, mins = divmod(minutes, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours} hr")
    if mins > 0:
        parts.append(f"{mins} mins")

    return " ".join(parts)