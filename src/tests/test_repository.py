import pytest
from sqlalchemy import select

from src.repository import FileHashRepository
from src.models import FileHash

@pytest.mark.asyncio
async def test_check_filehash_by_path(db_session, sample_filehash):
    path_file, hash_file = sample_filehash

    fh_repository = FileHashRepository(session=db_session)
    file_hash_obj = await fh_repository.check_filehash_by_path(path_file)
    assert isinstance(file_hash_obj, FileHash) and file_hash_obj.path_file==path_file and file_hash_obj.hash==hash_file

@pytest.mark.asyncio
async def test_check_filehash_by_hash(db_session, sample_filehash):
    path_file, hash_file = sample_filehash

    fh_repository = FileHashRepository(session=db_session)
    file_hash_obj = await fh_repository.check_filehash_by_hash(hash_file)
    assert isinstance(file_hash_obj, FileHash) and file_hash_obj.path_file == path_file and file_hash_obj.hash==hash_file

@pytest.mark.asyncio
async def test_add_filehash(db_session, file_hash_values):
    path_file, hash_file = file_hash_values

    fh_repository = FileHashRepository(session=db_session)
    file_hash_obj = await fh_repository.add_filehash(hash_source_file=hash_file, destination_file=path_file)

    assert (file_hash_obj, FileHash) and file_hash_obj.path_file==path_file and file_hash_obj.hash==hash_file

    await db_session.delete(file_hash_obj)
    await db_session.commit()

@pytest.mark.asyncio
async def test_delete_filehash(db_session, file_hash_values):
    path_file, hash_file = file_hash_values

    testing_Filehash = FileHash(path_file=path_file, hash=hash_file)
    fh_repository = FileHashRepository(session=db_session)

    db_session.add(testing_Filehash)
    await db_session.commit()

    await fh_repository.delete_filehash(testing_Filehash)

    expected_Filehash = await db_session.scalar(select(FileHash).where(FileHash.hash==hash_file, FileHash.path_file==path_file))

    assert expected_Filehash is None

