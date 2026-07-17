import uuid
import json
from datetime import datetime

def format_date(dt, fmt='%b %d, %Y'):
    """Format datetime objects cleanly."""
    if not dt:
        return 'N/A'
    return dt.strftime(fmt)

def time_ago(dt):
    """Generate '2 hours ago' style relative time string."""
    if not dt:
        return 'never'
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    if seconds < 0:
        return 'just now'
        
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    months = days // 30
    years = days // 365
    
    if seconds < 60:
        return 'just now'
    elif minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes > 1 else ''} ago"
    elif hours < 24:
        return f"{int(hours)} hour{'s' if hours > 1 else ''} ago"
    elif days < 30:
        return f"{int(days)} day{'s' if days > 1 else ''} ago"
    elif months < 12:
        return f"{int(months)} month{'s' if months > 1 else ''} ago"
    else:
        return f"{int(years)} year{'s' if years > 1 else ''} ago"

def truncate_text(text, length=200):
    """Truncate long string summaries cleanly."""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length].rstrip() + '...'

def generate_unique_filename(original_filename):
    """Prefix a unique UUID token to the original file's extension."""
    if not original_filename or '.' not in original_filename:
        ext = 'txt'
    else:
        ext = original_filename.rsplit('.', 1)[1].lower()
    
    unique_id = uuid.uuid4().hex
    return f"{unique_id}.{ext}"

def safe_json_loads(text, default=None):
    """Parse JSON strings safely without throwing exceptions."""
    if not text:
        return default if default is not None else {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default if default is not None else {}

def percentage(part, whole):
    """Calculate percentage score safely."""
    if not whole:
        return 0.0
    return round((part / whole) * 100, 1)

def format_file_size(bytes_size):
    """Format file size into readable KB/MB labels."""
    if bytes_size is None or bytes_size < 0:
        return '0 B'
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
        
    return f"{bytes_size:.1f} TB"
