import os

JWT_SECRET = os.environ.get("JWT_SECRET", "visionguard-secret-key-2024")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 1
