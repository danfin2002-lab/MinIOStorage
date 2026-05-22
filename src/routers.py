from fastapi import APIRouter, HTTPException
from src.schemas import FilePutSchema, FileDeleteSchema, FileGetSchema
from src.dependencies.filehash import FileServiceDep

router = APIRouter(prefix = "/minio", tags=["Действия в хранилище"])


@router.post("",
    summary = "Загрузить файл",
	response_model = FileGetSchema
)
#TODO Чего возврщать-то?
async def put_file(data: FilePutSchema, file_service: FileServiceDep)-> FileGetSchema:
    new_file = await file_service.upload_file(data)
    return new_file



@router.get("", #Размер, путь, когда создан
    summary = "Получить метаданные обо всех файлах",
    response_model = list[FileGetSchema]
)
async def get_metadata_files(file_service: FileServiceDep)->list[FileGetSchema]:
    result = file_service.get_metadata()
    return result


@router.delete("",
    summary = "Удалить файл по пути"
)
async def delete_file(data: FileDeleteSchema, file_service: FileServiceDep):
    await file_service.delete_file(data)
