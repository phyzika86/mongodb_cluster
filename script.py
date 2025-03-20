from pymongo import MongoClient

# Подключение к одному из конфигурационных серверов
"""
TODO здесь либо указывать параметр mongodb://localhost:27019/?directConnection=true чтобы
подключиться к одному из конфигурационных серверов, либо проинициализирвоать сначала через mongo shell непосредственно
через контейнер 
"""
config_client = MongoClient('mongodb://localhost:27019/?directConnection=true')
shards_client = MongoClient('mongodb://localhost:27018/?directConnection=true')

# Команда для инициализации репликасета
config = {
    "_id": "configReplSet",
    "configsvr": True,
    "members": [
        {"_id": 0, "host": "config1:27019"},
        {"_id": 1, "host": "config2:27019"},
        {"_id": 2, "host": "config3:27019"}
    ]
}

shard1_config = {
    "_id": "shard1",
    "members": [
        {"_id": 0, "host": "shard1a:27018"},
        {"_id": 1, "host": "shard1b:27018"},
        {"_id": 2, "host": "shard1c:27018"}
    ]
}

shard2_config = {
    "_id": "shard2",
    "members": [
        {"_id": 0, "host": "shard2a:27018"},
        {"_id": 1, "host": "shard2b:27018"},
        {"_id": 2, "host": "shard2c:27018"}
    ]
}

shard3_config = {
    "_id": "shard3",
    "members": [
        {"_id": 0, "host": "shard3a:27018"},
        {"_id": 1, "host": "shard3b:27018"},
        {"_id": 2, "host": "shard3c:27018"}
    ]
}

# Инициализация репликасета для конфигурационных серверов
try:
    config_client.admin.command("replSetInitiate", config)
    print("Репликасет конфигурационных серверов успешно инициализирован.")
    # Проверка статуса репликасета
    status = config_client.admin.command("replSetGetStatus")
    print("Статус репликасета:", status)
except Exception as e:
    print(f"Ошибка при инициализации репликасета: {e}")


# Инициализация репликасетов для шардов
shard_configs = [shard1_config, shard2_config, shard3_config]
shard_ports = [27018, 27048, 27078]  # Порта для подключения к первичным узлам шардов описаны в docker-compose

for index, (shard_config, port) in enumerate(zip(shard_configs, shard_ports)):
    try:
        # Подключение к первичному узлу шарда
        shard_client = MongoClient(f'mongodb://localhost:{port}/?directConnection=true')
        shard_client.admin.command("replSetInitiate", shard_config)
        print(f"Репликасет шарда {index + 1} успешно инициализирован.")
        status = shard_client.admin.command("replSetGetStatus")
        print(f"Статус репликасета шарда {index + 1}:", status)
    except Exception as e:
        print(f"Ошибка при инициализации репликасета шарда {index + 1}: {e}")


# Подключение к маршрутизатору
router_client = MongoClient('mongodb://localhost:27017/?directConnection=true')

# Добавление шарда в кластер
try:
    router_client.admin.command("addShard", "shard1/shard1a:27018,shard1b:27018,shard1c:27018")
    router_client.admin.command("addShard", "shard2/shard2a:27018,shard2b:27018,shard2c:27018")
    router_client.admin.command("addShard", "shard3/shard3a:27018,shard3b:27018,shard3c:27018")
    print("Шарды успешно добавлены в кластер.")
except Exception as e:
    print(f"Ошибка при добавлении шарда: {e}")


# Проверка статуса балансировки. Включается автоматически, но можно проверить и включить вручную
try:
    balancer_status = router_client.config.settings.find_one({"_id": "balancer"})
    if balancer_status and not balancer_status.get("stopped", False):
        print("Балансировка уже включена.")
    else:
        # Включение балансировки
        router_client.config.settings.update_one(
            {"_id": "balancer"},
            {"$set": {"stopped": False}},
            upsert=True
        )
        print("Балансировка включена.")
except Exception as e:
    print(f"Ошибка при проверке/включении балансировки: {e}")


# Выбор базы данных и коллекции
db = router_client.test_db
collection = db.test_collection

# Включение шардирования для коллекции
try:
    router_client.admin.command("enableSharding", "test_db")
    print("Шардирование для базы данных 'test_db' включено.")
except Exception as e:
    print(f"Ошибка при включении шардирования: {e}")

# Выбор ключа шардирования
# shard_key = {"user_id": 1}  # Пример ключа шардирования
shard_key = {"user_id": "hashed"}
try:
    router_client.admin.command("shardCollection", "test_db.test_collection", key=shard_key)
    print(f"Коллекция 'test_collection' зашардирована по ключу: {shard_key}.")
except Exception as e:
    print(f"Ошибка при шардировании коллекции: {e}")

# Нагрузка данными
try:
    for i in range(10000):
        collection.insert_one({"user_id": i, "data": f"sample_data_{i}"})
    print("Данные успешно загружены.")
except Exception as e:
    print(f"Ошибка при загрузке данных: {e}")
