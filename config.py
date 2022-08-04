from pydantic import BaseSettings
from beanie import init_beanie
from models.db import SignatureInDB
from motor.motor_asyncio import AsyncIOMotorClient

class Settings(BaseSettings):
    DATABASEURL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        orm_mode = True


async def init_database():
    client = AsyncIOMotorClient(Settings().DATABASEURL)
    await init_beanie(database=client.signverifyapp, document_models=[SignatureInDB])
