# pip install filetype

import filetype


def check_filetype(minio_client, bucket_name, destination_file):
    try:
        """with minio_client.get_object(bucket_name, destination_file, length=261) as response:
            head = response.read(261)"""

        response = minio_client.get_object(bucket_name, destination_file,
                                           length=261)  # Библиотека filetype для определения типа обычно считывает заголовок размером до 261 байта (это её внутреннее ограничение, покрывающее все поддерживаемые форматы).
        head = response.read(261)
        response.close()
        response.release_conn()

        kind = filetype.guess(head) #принимает первые байты файла (в виде bytes) и пытается определить его MIME-тип и расширение.
        return kind is not None and kind.mime.startswith('image/') #Условие: kind is not None (тип определён) и MIME-тип начинается с 'image/' (т.е. image/jpeg, image/png и т.д.
    except Exception:
        print("Ошибка в определении типа файла")
        return False