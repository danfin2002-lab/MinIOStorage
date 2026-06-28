import pytest
import os
from src.utils.hashing import compute_sha256

@pytest.fixture
def temp_file():
	path = "temp_test_file.txt"
	with open(path, "w") as f:
		f.write("Hello, world!!!")
	
	yield path
	
	os.remove(path)


@pytest.mark.asyncio
async def test_compute_sha256(temp_file):
	res = await compute_sha256(temp_file)
	print(res)
	assert isinstance(res, str) and len(res) == 64
		
	
