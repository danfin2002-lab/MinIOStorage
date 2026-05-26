from fastapi import APIRouter, Query
from src.schemas import FilePutSchema, FileDeleteSchema, MetadataGetSchema, FileGetSchema, PredictSendSchema
from src.dependencies.filehash import FileServiceDep
from fastapi.responses import StreamingResponse

router = APIRouter(prefix = "/minio", tags=["Действия в хранилище"])


@router.post("",
    summary = "Загрузить файл",
    response_model = MetadataGetSchema
)
#TODO Чего возврщать-то?
async def put_file(data: FilePutSchema, file_service: FileServiceDep)-> MetadataGetSchema:
    new_file = await file_service.upload_file(data)
    return new_file



@router.get("", #Размер, путь, когда создан
    summary = "Получить метаданные обо всех файлах",
    response_model = list[MetadataGetSchema]
)
def get_metadata_files(file_service: FileServiceDep)->list[MetadataGetSchema]:
    result = file_service.get_metadata()
    return result


@router.delete("",
    summary = "Удалить файл по пути"
)
async def delete_file(data: FileDeleteSchema, file_service: FileServiceDep):
    await file_service.delete_file(data)


@router.get("/{destination_file:path}",
    summary = "Скачать файл",
)
def get_file(
		destination_file: str,
		file_service: FileServiceDep)->StreamingResponse:
    response, content_type = file_service.get_file(destination_file)
    return StreamingResponse( #Позволяет передавать файл частями без загрузки всего в память
        response,
        media_type=content_type,
        headers={
            "Content-Disposition": f'inline; filename="{destination_file.split("/")[-1]}"'
            #если нужно открывать в браузере, замените attachment на inline
        }
    )
#http://localhost:8000/minio/path_to_file


@router.post("/image",
    summary="Отправить изображение на предсказание"
)
def send_to_prediction(data: PredictSendSchema):
    pass

