from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):

    PROJECT_NAME: str = "Video Compressor API"

    VERSION: str = "1.0.0"

    API_V1_STR: str = "/api/v1"

    

    # Declarar os campos para que o Pydantic os leia do ambiente

    POSTGRES_USER: str

    POSTGRES_PASSWORD: str

    POSTGRES_DB: str

    POSTGRES_HOST: str = "db" # Valor padrão

    POSTGRES_PORT: int = 5432

    

    REDIS_HOST: str = "redis"  # Declarar aqui

    REDIS_PORT: int = 6379    # Declarar aqui

    

    @computed_field

    @property

    def DATABASE_URL(self) -> str:

        # Use self.POSTGRES_HOST para respeitar a Opção B ou a var de ambiente

        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"



    @computed_field

    @property

    def REDIS_URL(self) -> str:

        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"



    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")
    # Variáveis brutas do .env
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    
    REDIS_PORT: int = 6379

    # Monta a URL do Banco automaticamente
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Monta a URL do Redis automaticamente
    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://redis:{self.REDIS_PORT}/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()