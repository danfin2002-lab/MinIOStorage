from datetime import date
import cv2

def put_date(image):
	today_str = date.today().strftime("%Y-%m-%d")
	
	font = cv2.FONT_HERSHEY_SIMPLEX
	font_scale = 0.7
	thickness = 2
	color = (255, 255, 255)
	
	# Вычисляем размер текста, чтобы, например, разместить в правом верхнем углу
	(text_width, text_height), baseline = cv2.getTextSize(today_str, font, font_scale, thickness)
	
	# Координаты: отступ от правого и верхнего края
	x = image.shape[1] - text_width - 10   # правый край минус ширина текста и отступ
	y = text_height + 10
	
	
	# Рисуем полупрозрачный фон для лучшей читаемости (опционально)
	overlay = image.copy()
	cv2.rectangle(overlay, (x - 5, y - text_height - 5), (x + text_width + 5, y + 5), (0, 0, 0), -1)
	image = cv2.addWeighted(overlay, 0.5, image, 0.5, 0)
	
	# Накладываем текст
	cv2.putText(image, today_str, (x, y), font, font_scale, color, thickness)
	
	return image