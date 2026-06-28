from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings_for_Testing(BaseSettings):
    DB_TESTING_HOST: str
    DB_TESTING_PORT: int
    DB_TESTING_USER: str
    DB_TESTING_PASS: str
    DB_TESTING_NAME: str

    @property
    def Testing_DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_TESTING_USER}:{self.DB_TESTING_PASS}@{self.DB_TESTING_HOST}:{self.DB_TESTING_PORT}/{self.DB_TESTING_NAME}"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore",)

settings = Settings_for_Testing()
