import os
from unittest.mock import AsyncMock, patch

import pytest_asyncio
import pytest
from dotenv import load_dotenv
from minio import Minio, S3Error

from src.models import FileHash
from src.repository import FileHashRepository
from src.services import FileService
from src.schemas import FilePutSchema, MetadataGetSchema, FileDeleteSchema


# --------------------------------------------------------------
# For Service


@pytest.fixture(scope="session")
def minio_client():
    load_dotenv()
    MIO_ENDPOINT = os.getenv("MIO_ENDPOINT")
    MIO_ACCESS_KEY = os.getenv("MIO_ACCESS_KEY")
    MIO_SECRET_KEY = os.getenv("MIO_SECRET_KEY")

    client = Minio(
        endpoint=MIO_ENDPOINT,
        access_key=MIO_ACCESS_KEY,
        secret_key=MIO_SECRET_KEY,
        secure=False,
    )

    return client


@pytest.fixture(scope="function")
def testing_bucket(minio_client):
    load_dotenv()
    bucket_name = os.getenv("MIO_TEST_BUCKET_NAME")

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    yield bucket_name

    objects = minio_client.list_objects(bucket_name, recursive=True)

    for obj in objects:
        minio_client.remove_object(bucket_name, obj.object_name)

    minio_client.remove_bucket(bucket_name)


@pytest.fixture(scope="function")
def temp_file(tmp_path):
    file_path = tmp_path / "test_file.txt"#встроенную фикстуру tmp_path (pytest), которая создаёт временную директорию
    file_path.write_text("Hy!!!")
    return str(file_path)


@pytest.fixture(scope="function")
def filehash_obj(file_hash_values):
    path_file, hash_str_file = file_hash_values
    new_fh = FileHash(path_file=path_file, hash=hash_str_file)
    return new_fh


@pytest_asyncio.fixture(scope="function")
async def file_service(testing_bucket, minio_client, temp_file, filehash_obj):
    mock_repo = AsyncMock(spec=FileHashRepository)
    mock_repo.check_filehash_by_hash = AsyncMock(return_value=None)
    mock_repo.check_filehash_by_path = AsyncMock(return_value=None)
    mock_repo.add_filehash = AsyncMock(return_value=filehash_obj)
    mock_repo.delete_filehash = AsyncMock()

    # заменяет глобальный объект client в модуле src.services на реальный клиент MinIO
    with patch("src.services.client", minio_client), \
            patch("src.services.bucket_name", testing_bucket):
        #заменяет глобальную переменную bucket_name на имя тестового бакета.
        service = FileService(repository=mock_repo)

        with patch("src.services.compute_sha256", return_value=filehash_obj.hash): #Подменяет функцию compute_sha256 с помощью вложенного patch, возвращая фиксированный хэш из filehash_obj.hash
            yield service, mock_repo, temp_file, testing_bucket, minio_client


@pytest.fixture(scope="function")
def add_objects_to_bucket(tmp_path, temp_file, testing_bucket, minio_client):
    file_path_2 = tmp_path / "test_file_2.txt"#встроенную фикстуру tmp_path (pytest), которая создаёт временную директорию
    file_path_2.write_text("Daniel")
    temp_file_2 = str(file_path_2)

    minio_client.fput_object(
        testing_bucket, "uploaded/test.txt", temp_file
    )

    minio_client.fput_object(
        testing_bucket, "uploaded/test_2.txt", temp_file_2
    )

    yield

    #testing_bucket всё сам подчищает

@pytest.fixture(scope="function")
def destination_file():
    destination_file = "uploaded/test.txt"
    return destination_file

#-------------------------Tests----------------------


@pytest.mark.asyncio
async def test_upload_file(file_service, destination_file):
    service, mock_repo, temp_file, testing_bucket, minio_client = file_service

    data = FilePutSchema(
        source_file=temp_file,
        destination_file=destination_file
    )

    result = await service.upload_file(data)

    stat = minio_client.stat_object(testing_bucket, destination_file)#получает метаданные загруженного объекта
    assert stat.size > 0

    assert isinstance(result, MetadataGetSchema)
    assert result.path == destination_file
    assert result.size == stat.size  #Сопоставляем, что данные, которые мы отправили и получили в upload_file, соответствуют данным, которые мы получили здесь напрямую stat_object
    assert result.last_modified == stat.last_modified



def test_get_metadata(file_service, add_objects_to_bucket, destination_file):
    service, _ , _ , testing_bucket, minio_client = file_service

    result = service.get_metadata()

    objects_list = minio_client.list_objects(testing_bucket, recursive=True)

    metadata = []
    for obj in objects_list:
        metadata.append(
            MetadataGetSchema(
                path=obj.object_name,
                size=obj.size,
                last_modified=obj.last_modified
            )
        )

    assert isinstance(result[0], MetadataGetSchema)
    assert len(result) == len(metadata)
    assert result[0].size == metadata[0].size
    assert result[0].last_modified == metadata[0].last_modified
    assert result[0].path == destination_file
    assert result[1].path =="uploaded/test_2.txt"


@pytest.mark.asyncio
async def test_delete_file(temp_file, testing_bucket, minio_client, destination_file):#file_service):

    #Сначала создаю файл, затем удаляю - в фикстуру
    #_, _, temp_file, testing_bucket, minio_client = file_service

    #result = await service.upload_file(data)


    minio_client.fput_object(
        testing_bucket, destination_file, temp_file
    )

    data = FileDeleteSchema(
        destination_file=destination_file
    )


    filehash_obj = FileHash(
        path_file = destination_file,
        hash = "B94D27B9934D3E08A52E52D7DA7DABFAC484EFE37A5380EE9088F7ACE2EFCDE9"
    )

    mock_repo = AsyncMock(spec=FileHashRepository)
    mock_repo.check_filehash_by_path = AsyncMock(return_value=filehash_obj)
    mock_repo.delete_filehash = AsyncMock()

    # заменяет глобальный объект client в модуле src.services на реальный клиент MinIO
    with patch("src.services.client", minio_client), \
            patch("src.services.bucket_name", testing_bucket):
        # заменяет глобальную переменную bucket_name на имя тестового бакета.
        service = FileService(repository=mock_repo)
        await service.delete_file(data=data)



    with pytest.raises(S3Error) as exc_info:
        minio_client.stat_object(testing_bucket, destination_file)
        assert exc_info.value.code == "NoSuchKey"


    #assert new_result is None
    mock_repo.delete_filehash.assert_awaited_once_with(filehash_obj)






