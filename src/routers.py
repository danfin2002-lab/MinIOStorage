from fastapi import APIRouter, HTTPException
from src.schemas import FilePutSchema, FileDeleteSchema, MetadataGetSchema, FileGetSchema, PredictSendSchema
from src.dependencies.filehash import FileServiceDep
from fastapi.responses import StreamingResponse
from src.broker import publisher
from src.my_exceptions import FileNotFoundException, DeleteFileException, ListObjectsException, FileAlreadyExistsException, FPutObjectException


router = APIRouter(prefix = "/minio", tags=["Действия в хранилище"])


@router.post("",
    summary = "Загрузить файл",
    response_model = MetadataGetSchema
)
async def put_file(data: FilePutSchema, file_service: FileServiceDep)-> MetadataGetSchema:
    try:
        new_file = await file_service.upload_file(data)
    except FileAlreadyExistsException as err:
        raise HTTPException(status_code=400, detail=str(err))
    except FPutObjectException as err:
        raise HTTPException(status_code=500, detail=str(err))
    return new_file



@router.get("", #Размер, путь, когда создан
    summary = "Получить метаданные обо всех файлах",
    response_model = list[MetadataGetSchema]
)
def get_metadata_files(file_service: FileServiceDep)->list[MetadataGetSchema]:
    try:
        result = file_service.get_metadata()
    except ListObjectsException as err:
        raise HTTPException(status_code=500, detail=str(err))
    return result


@router.delete("",
    summary = "Удалить файл по пути"
)
async def delete_file(data: FileDeleteSchema, file_service: FileServiceDep):
    try:
        await file_service.delete_file(data)
    except FileNotFoundException as err:
        raise HTTPException(status_code=404, detail=str(err))
    except DeleteFileException as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.get("/{destination_file:path}",
    summary = "Скачать файл",
)
def get_file(
        destination_file: str,
        file_service: FileServiceDep)->StreamingResponse:
    try:
        response, content_type = file_service.get_file(destination_file)
    except FileNotFoundException as err:
        raise HTTPException(status_code=404, detail=str(err))

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
async def send_to_prediction(data: PredictSendSchema, file_service: FileServiceDep):
    try:
        file_service.check_exists_file(data.destination_file)
    except FileNotFoundException as err:
        raise HTTPException(status_code=404, detail=str(err))

    await publisher.publish(data.destination_file)
    return {"status": "message published", "file": data.destination_file}