from minio import S3Error

from src.utils.hashing import compute_sha256
from src.schemas import FilePutSchema, MetadataGetSchema, FileDeleteSchema, FileGetSchema
from fastapi import HTTPException
from src.minio_settings import client, bucket_name
from src.repository import FileHashRepository
import mimetypes

class FileService:
	def __init__(self, repository: FileHashRepository) -> None:
		self.repository = repository
	
	async def upload_file(self, data: FilePutSchema)->MetadataGetSchema:
		hash_source_file = await compute_sha256(data.source_file)
		
		existing_hash = await self.repository.check_filehash_by_hash(hash_source_file)
		if existing_hash is not None:
			raise HTTPException(status_code=400, detail="A file with such contents already exists.")

		#Если хэш-сумма файла уникальна, а такое название уже есть, то старый файл надо удалить из БД
		existing_path = await self.repository.check_filehash_by_path(data.destination_file)
		if existing_path is not None:
			await self.repository.delete_filehash(existing_path)
		
		#metadata = {"x-amz-meta-sha256": hash_source_file} #TODO Надо ли?
		try:
			client.fput_object(
				bucket_name, data.destination_file, data.source_file
			)
		except S3Error as err:
			raise HTTPException(status_code=500, detail=str(err))
		
		await self.repository.add_filehash(hash_source_file, data.destination_file)
		
		obj = client.stat_object(bucket_name, data.destination_file)
		
		res = MetadataGetSchema(
			path = data.destination_file,
			size = obj.size,
			last_modified = obj.last_modified
		)
		
		return res
		
	def get_metadata(self)->list[MetadataGetSchema]:
		try:
			objects_list = client.list_objects(bucket_name, recursive = True)
		except S3Error as err:
			raise HTTPException(status_code=500, detail=str(err))

		result = []
		for obj in objects_list:
			result.append(
				MetadataGetSchema(
					path=obj.object_name,
					size=obj.size,
					last_modified=obj.last_modified
				)
			)

		return result
	
	async def delete_file(self, data: FileDeleteSchema):
		try:
			client.stat_object(bucket_name, data.destination_file)
		except S3Error:
			raise HTTPException(status_code=404, detail="File not found")
			
		try:
			client.remove_object(bucket_name, data.destination_file)
		except S3Error:
			raise HTTPException(status_code=500, detail="Error while deleting")
		
		existing_filehash = await self.repository.check_filehash_by_path(data.destination_file)
		await self.repository.delete_filehash(existing_filehash)
		
	def get_file(self, destination_file: str): #Должен быть на выходе либо файл для скачивания или ссылка что ли
		try:
			client.stat_object(bucket_name, destination_file)
		except S3Error:
			raise HTTPException(status_code=404, detail="File not found")
		
		response = client.get_object(bucket_name, destination_file)#Возвращает поток байтов
		
		content_type = mimetypes.guess_type(destination_file)[0] or "application/octet-stream"#Определяем content_type по расширению файла

		return response, content_type
		
