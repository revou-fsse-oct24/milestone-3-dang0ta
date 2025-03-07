import os

if os.getenv("FLASK_ENV") == "production":
    from app_config_prod import AppConfig
else:
    from app_config_dev import AppConfig

