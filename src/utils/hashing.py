#Встроенная функция hash() - для работы с коллекциями, без перебора по хэшу обращаться к определённой ячейке памяти
#hashlib - модуль хэширования, содержащий в себе алгоритмы для шифрования.
#filehash

# Я бы использовал SHA-256 алгоритм

import hashlib
import aiofiles

async def compute_sha256(file_path: str)->str:
	sha256 = hashlib.sha256() #Создаётся объект хэша SHA256
	async with aiofiles.open(file_path, mode="rb") as f:
		#for block in iter(lambda: f.read(4096), b""):#Создаётся итератор, который многократно вызывает переданную
	#функцию lambda: f.read(4096), b"" Каждый вызов читает ровно 4096 байт(4 КБ) из файла
	#чтение продолжается до тех пор, пока не будет получено значение, равное второму аргументу - пустой байтовой строке b"" 
		while True:
			block = await f.read(4096)
			if not block:
				break
			sha256.update(block) # Каждый прочитанный блок обновляет текущее хэш-значение
	return sha256.hexdigest()