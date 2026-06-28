from src.dependencies.session import SessionDep
from fastapi import Depends
from typing import Annotated
from src.repository import FileHashRepository
from src.services import FileService

async def get_filehash_repository(session: SessionDep)->FileHashRepository:
	return FileHashRepository(session)
	
FHRepositoryDep = Annotated[FileHashRepository, Depends(get_filehash_repository)]

async def get_file_service(fh_repository: FHRepositoryDep)->FileService:
	return FileService(fh_repository)

FileServiceDep = Annotated[FileService, Depends(get_file_service)]