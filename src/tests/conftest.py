import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.tests.config import settings
import subprocess
import asyncio
import pytest
from src.utils.waiting_pg import wait_for_postgres
from src.models import FileHash
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

container_name_from_env = os.getenv('DB_TESTING_CONTAINER_NAME')


@pytest.fixture(scope="session")
def setup_db():
    subprocess.run(["docker", "compose", "up", "-d", container_name_from_env], check=True)

    wait_for_postgres()

    subprocess.run(["alembic", "upgrade", "head"], check=True)

    yield

    subprocess.run(["docker", "compose", "down", "-v", container_name_from_env], check=True)


@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db):
    async_engine = create_async_engine(settings.Testing_DATABASE_URL_asyncpg, echo=True)
    async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session
    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def sample_filehash(db_session, file_hash_values):
    path_file, hash_str_file = file_hash_values

    testing_Filehash = FileHash(path_file=path_file, hash=hash_str_file)

    db_session.add(testing_Filehash)
    await db_session.commit()

    yield path_file, hash_str_file

    await db_session.delete(testing_Filehash)
    await db_session.commit()


@pytest.fixture(scope="function")
def file_hash_values():
    path_file = "test_file.docx"
    hash_str_file = "B94D27B9934D3E08A52E52D7DA7DABFAC484EFE37A5380EE9088F7ACE2EFCDE9"

    return path_file, hash_str_file


