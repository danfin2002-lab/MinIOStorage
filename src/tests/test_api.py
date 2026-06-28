from http.client import responses

from fastapi.testclient import TestClient
from main import app
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.dependencies.filehash import get_file_service
from src.my_exceptions import FileAlreadyExistsException
from src.schemas import MetadataGetSchema, FileDeleteSchema
from src.services import FileService


@pytest.fixture(scope="function")
def mock_file_service():
    mock = Mock(spec=FileService)
    mock.upload_file = AsyncMock(
        return_value = MetadataGetSchema(
            path="uploaded/test_file.txt",
            size=12345,
            last_modified="2026-06-27T20:25:00"
        )
    )
    mock.get_metadata = Mock(
        return_value = [
            MetadataGetSchema(
                path="uploaded/test_file.txt",
                size=12345,
                last_modified="2026-06-27T20:25:00"
            ),
            MetadataGetSchema(
                path="uploaded/test_file_2.txt",
                size=67891,
                last_modified="2012-06-27T21:25:00"
            )
        ]
    )
    mock.delete_file = AsyncMock(
        return_value = None
    )
    return mock

@pytest.fixture(scope="function")
def client(mock_file_service):
    #Переопределяем зависимость
    app.dependency_overrides[get_file_service] = lambda: mock_file_service
    yield TestClient(app=app)
    #Ояищаем переопредление класса
    app.dependency_overrides.clear()



def test_put_file(client: TestClient):
    payload = {
        "source_file": "/tmp/somefile.txt",
        "destination_file": "uploaded/test_file.txt"
    }

    response = client.post("/minio", json=payload)

    assert response.status_code==200
    data_response = response.json()
    assert data_response["path"]=="uploaded/test_file.txt"
    assert data_response["size"]==12345
    assert data_response["last_modified"]=="2026-06-27T20:25:00"

    # path="uploaded/test_file.txt",
    # size=12345,
    # last_modified="2026-06-27T20:25:00"

def test_put_file_conflict(client, mock_file_service):
    mock_file_service.upload_file.side_effect = FileAlreadyExistsException(
        "File already exists"
    )
    payload = {
        "source_file": "/tmp/somefile.txt",
        "destination_file": "uploaded/test_file.txt"
    }
    response = client.post("/minio", json=payload)

    assert response.status_code == 400
    assert "File already exists" in response.text

def test_get_metadata_files(client: TestClient):
    response = client.get("/minio")

    assert response.status_code == 200
    data_response = response.json()
    assert data_response[0]["path"] == "uploaded/test_file.txt"
    assert data_response[0]["size"] == 12345
    assert data_response[0]["last_modified"] == "2026-06-27T20:25:00"

    assert data_response[1]["path"] == "uploaded/test_file_2.txt"
    assert data_response[1]["size"] == 67891
    assert data_response[1]["last_modified"] == "2012-06-27T21:25:00"

def test_delete_file(client: TestClient):
    payload = {
        "destination_file": "uploaded/test_file.txt"
    }
    response = client.request("DELETE","/minio", json=payload)
    assert response.status_code==200
