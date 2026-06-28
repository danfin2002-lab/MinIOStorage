from models import FileHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class FileHashRepository:
	def __init__(self, session: AsyncSession)->None:
		self.session = session
		
	async def add_filehash(self, hash: str, destination_file: str)->FileHash:
		new_filehash = FileHash(hash = hash, path_file = destination_file)
		self.session.add(new_filehash)
		await self.session.commit()
		return new_filehash
		
	async def get_filehash_by_path(self, path_file: str)->FileHash:
		existing_filehash = await self.session.scalar(
			select(FileHash).where(FileHash.path_file == path_file)
		)
		return existing_filehash
		
	async def delete_filehash(self, filehash: FileHash):
		await self.session.delete(filehash)
		await self.session.commit()
	
	async def update_filehash(self, filehash: FileHash, hash: str)->FileHash:
		filehash.hash = hash
		await self.session.commit()
		return filehash
		