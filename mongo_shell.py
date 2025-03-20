import docker

# Подключение к Docker
client = docker.from_env()

# Получение контейнера
container = client.containers.get("mongodb_lessons_6-router-1")

# Команда для выполнения rs.status() в MongoDB
command = "mongo --eval 'db.getSiblingDB(\'test_db\'); db.getCollectionNames()'"

# Выполнение команды в контейнере
result = container.exec_run(command)

# Вывод результата
print(result.output.decode())