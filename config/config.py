from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    # Database settings
    db_user: str = Field(..., alias='DB_USER')
    db_password: str = Field(..., alias='DB_PASSWORD')
    db_name: str = Field(..., alias='DB_NAME')
    db_host: str = Field(..., alias='DB_HOST')
    db_port: int = Field(5432, alias='DB_PORT')
    sql_options: str = Field('-c search_path=public,content', alias='SQL_OPTIONS')
    database_type: str = Field('postgres', alias='DATABASE_TYPE')
    batch_size: int = Field(1000, alias='BATCH_SIZE')

    # Elasticsearch settings
    elk_url: str = Field(..., alias='ELK_URL')
    elk_index: str = Field(..., alias='ELK_INDEX')
    elk_port: int = Field(9200, alias='ELK_PORT')

    # Other settings
    schema_file: str = Field(..., alias='SCHEMA_FILE')

    # Redis settings
    redis_host: str = Field(..., alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')


settings = Settings()
