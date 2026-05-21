from minio import S3Error

from src.utils.hashing import compute_sha256
from src.schemas import FilePutSchema, FileGetSchema, FileDeleteSchema
from fastapi import HTTPException
from src.minio_settings import client, bucket_name
from src.repository import FileHashRepository

class FileService:
	def __init__(self, repository: FileHashRepository) -> None:
		self.repository = repository
	
	async def upload_file(self, data: FilePutSchema)->FileGetSchema:
		hash_source_file = compute_sha256(data.source_file)
		
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
		
		res = FileGetSchema(
			path = data.destination_file,
			size = obj.size,
			last_modified = obj.last_modified
		)
		
		return res
		
	async def get_metadata(self)->list[FileGetSchema]:
		try:
			objects_list = client.list_objects(bucket_name, recursive = True)
		except S3Error as err:
			raise HTTPException(status_code=500, detail=str(err))

		result = []
		for obj in objects_list:
			result.append(
				FileGetSchema(
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
		
