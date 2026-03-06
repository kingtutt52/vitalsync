from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    app_name: str = "VitalSync API"
    debug: bool = False

    # Database
    database_url: str = "postgresql://vitalsync:vitalsync@localhost:5432/vitalsync"

    # JWT
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_OPENSSL_RAND_HEX_32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # File storage
    storage_root: str = os.path.join(os.path.dirname(__file__), "../../storage")

    # Stripe
    stripe_secret_key: str = "sk_test_YOUR_STRIPE_SECRET_KEY"
    stripe_webhook_secret: str = "whsec_YOUR_WEBHOOK_SECRET"
    stripe_price_premium_lite: str = "price_PREMIUM_LITE_ID"
    stripe_price_vital_plus: str = "price_VITAL_PLUS_ID"
    stripe_price_vital_pro: str = "price_VITAL_PRO_ID"

    # App base URL (for Stripe redirect)
    app_base_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
