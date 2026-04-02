from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Finance Data Processing and Access Control Backend"
    environment: str = "development"
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/finance_backend"
    default_admin_name: str = "System Admin"
    default_admin_email: str = "admin@finance.local"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
