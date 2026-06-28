from database import async_session_factory
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from repository import FileHashRepository

async def get_async_session():
	async with async_session_factory() as session:
		yield session
		
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

async def get_filehash_repository(session: SessionDep)->FileHashRepository:
	return FileHashRepository(session)
	
FHRepositoryDep = Annotated[FileHashRepository, Depends(get_filehash_repository)]
