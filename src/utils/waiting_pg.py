import time
import subprocess
#pip install python-dotenv
import os
from dotenv import load_dotenv

# Загрузка файла .env с указанием пути (если нужно)
load_dotenv(dotenv_path=".env")

# Получение значения переменной
user_from_env = os.getenv('DB_TESTING_USER')
container_name_from_env=os.getenv('DB_TESTING_CONTAINER_NAME')

def wait_for_postgres(container_name=container_name_from_env, user=user_from_env, timeout=10):
    """Ожидает, пока PostgreSQL в контейнере станет готов к приёму соединений."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = subprocess.run(
            ["docker", "exec", container_name, "pg_isready", "-U", user],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        time.sleep(0.5)
    raise TimeoutError(f"PostgreSQL в контейнере {container_name} не запустился за {timeout} сек.")