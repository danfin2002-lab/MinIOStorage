from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from typing import Annotated
from sqlalchemy import String

intpk = Annotated[int, mapped_column(primary_key=True)]
str64 = Annotated[str, mapped_column(String(64))]
str255nf = Annotated[str, mapped_column(String(255), nullable=False)]

class Base(DeclarativeBase):
	pass
	
class FileHash(Base):
	__tablename__ = "file_hashes"
	
	id: Mapped[intpk]
	hash: Mapped[str64] = mapped_column(index=True, unique=True)
	path_file: Mapped[str255nf]