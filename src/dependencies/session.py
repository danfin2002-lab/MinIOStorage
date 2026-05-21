from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated
from src.database import async_session_factoty

async def get_async_session():
	async with async_session_factoty() as session:
		yield session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]