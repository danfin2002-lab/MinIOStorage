#Встроенная функция hash() - для работы с коллекциями, без перебора по хэшу обращаться к определённой ячейке памяти
#hashlib - модуль хэширования, содержащий в себе алгоритмы для шифрования.
#filehash

# Я бы использовал SHA-256 алгоритм

import hashlib

def compute_sha256(img_bytes: bytes)->str:
	sha256 = hashlib.sha256() #Создаётся объект хэша SHA256
	sha256.update(img_bytes) #Весь блок целиком
	return sha256.hexdigest()