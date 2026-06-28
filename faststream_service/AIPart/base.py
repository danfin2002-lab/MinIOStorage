#pip install ultralytics
import io

from ultralytics import YOLO
import cv2
import numpy as np
import os
from database import async_session_factory
from repository import FileHashRepository
from minio import S3Error
from utils.hashing import compute_sha256
from utils.put_date import put_date


# Загрузка модели YOLOv8
model = YOLO('yolov8n.pt')

# Список цветов для различных классов
colors = [
	(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
	(255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
	(0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
	(47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
]

# Функция для обработки изображения
def process_image(minio_client, bucket_name, image_path):
	# Загрузка изображения
	response = minio_client.get_object(bucket_name, image_path) #TODO Можно заменить на контекстный меннеджер
	image_bytes = response.read()
	response.close()
	response.release_conn()

	#Преобразуем байты в numpy array (OpenCV)
	np_array = np.frombuffer(image_bytes, np.uint8)
	img_cv = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
	if img_cv is None:
		raise ValueError("Не удалось декодировать изображение")


	results = model(img_cv)[0]

	# Получение оригинального изображения и результатов
	image = results.orig_img #numpy-массив
	classes_names = results.names
	classes = results.boxes.cls.cpu().numpy()
	boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

	# Подготовка словаря для группировки результатов по классам
	grouped_objects = {}

	# Рисование рамок и группировка результатов
	for class_id, box in zip(classes, boxes):
		class_name = classes_names[int(class_id)]
		color = colors[int(class_id) % len(colors)]  # Выбор цвета для класса
		if class_name not in grouped_objects:
			grouped_objects[class_name] = []
		grouped_objects[class_name].append(box)

		# Рисование рамок на изображении
		x1, y1, x2, y2 = box
		cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
		cv2.putText(image, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

	image = put_date(image)
	return image


async def save_new_image(minio_client, bucket_name, image_path, image):
	# Берём расширение из исходного пути
	#fh_repo = FHRepositoryDep
	ext = os.path.splitext(image_path)[1]
	if ext.lower() == '.jpg':
		encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95] #С этим надо быть поаккуратнее - я не знаю, как оно работает
		success, buffer = cv2.imencode('.jpg', image, encode_param)
		content_type = "image/jpeg"
	elif ext.lower() == '.png':
		success, buffer = cv2.imencode('.png', image)
		content_type = "image/png"
	elif ext.lower() == '.bmp':
		success, buffer = cv2.imencode('.bmp', image)
		content_type = "image/bmp"
	elif ext.lower() == '.jpeg':
		success, buffer = cv2.imencode('.jpeg', image)
		content_type = "image/jpeg"
	else:
		# Если формат не поддерживается
		raise ValueError(f"Неподдерживаемый формат изображения: {ext}. "
                     "Разрешены: .jpg, .jpeg, .png, .bmp.")
	if not success:
		raise RuntimeError("Ошибка кодирования изображения")

	img_bytes = buffer.tobytes()

	hash_file = compute_sha256(img_bytes)


	try:
		#Перезаписываем объект в MinIO (тот же path, то же имя)
		minio_client.put_object(
			bucket_name,
			image_path,# никаких изменений
			io.BytesIO(img_bytes),
			length=len(img_bytes),
			content_type=content_type
		)
	except S3Error:
		raise Exception("Error to put object")

	async with async_session_factory() as session:
		fh_repo = FileHashRepository(session)
		filehash_obj = await fh_repo.get_filehash_by_path(image_path)
		filehash_updt = await fh_repo.update_filehash(filehash_obj, hash_file)


