
import re
# Регулярные выражения для валидации
VALIDATORS = {
    'username': re.compile(r'^[a-zA-Z0-9_-]{3,30}$'),
    'email': re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'),
    'password': re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,30}$')
}

ERRORS = {
    'fields_required': ('All fields are required', 400),
    'username_length': ('Username must be between 3 and 30 characters', 400),
    'username_format': ('Username can only contain letters, numbers, hyphens and underscores', 400),
    'email_format': ('Invalid email format', 400),
    'password_length': ('Password must be between 8 and 30 characters', 400),
    'password_strength': ('Password must contain at least one uppercase letter, one lowercase letter and one digit', 400),
    'username_exists': ('Username already exists', 409),
    'email_exists': ('Email already registered', 409),
    'db_error': ('Database error', 500)
}