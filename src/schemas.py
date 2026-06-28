from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated

str255 = Annotated[str, Field(..., max_length = 255)]

class FilePutSchema(BaseModel):
	source_file: str255
	destination_file: str255

class FileDeleteSchema(BaseModel):
	destination_file: str255
	
class MetadataGetSchema(BaseModel):
	path: str255
	size: int = Field(..., ge = 0)
	last_modified: datetime
	
class FileGetSchema(BaseModel):
	destination_file: str255
	
class PredictSendSchema(BaseModel):
	destination_file: str255