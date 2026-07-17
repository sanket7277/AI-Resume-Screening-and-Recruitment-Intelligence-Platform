import re
from werkzeug.utils import secure_filename

def validate_email(email):
    """Basic regex email validation."""
    if not email:
        return False
    # Simple RFC 5322 compliance checking
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """
    Ensure password has at least 8 characters, 
    one uppercase letter, one lowercase letter, and one digit.
    """
    if not password or len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit

def validate_file_extension(filename, allowed_extensions):
    """Check if the uploaded file's extension matches permitted types."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions

def sanitize_filename(filename):
    """Sanitize the uploaded file's name using standard Werkzeug filters."""
    if not filename:
        return 'unnamed_file'
    return secure_filename(filename)

def validate_phone(phone):
    """Check phone formats (minimum 10 numbers, optional +, spaces, hyphens)."""
    if not phone:
        return False
    # Stripping decorative elements
    stripped = re.sub(r'[\s\-\(\)\+]', '', phone)
    return len(stripped) >= 10 and stripped.isdigit()
