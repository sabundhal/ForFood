
import re
import os
# Регулярные выражения для валидации
VALIDATORS = {
    'username': re.compile(r'^[a-zA-Z0-9_-]{3,30}$'),
    'email': re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'),
    'password': re.compile(r'^[a-zA-Z0-9_-]{8,30}$')
}

# Загрузите Client Secret из переменных окружения
JWT_SECRET_KEY_VALUE = '6eac08dd7b367838734720a99431fa01a4e7f550f265feb4'
#secret_key = os.urandom(24).hex()
#print(secret_key)
CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")

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