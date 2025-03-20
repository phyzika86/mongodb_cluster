from pymongo import MongoClient

# Подключение к маршрутизатору
router_client = MongoClient('mongodb://localhost:27017/?directConnection=true')

# Проверка статуса балансировки
try:
    balancer_status = router_client.config.settings.find_one({"_id": "balancer"})
    if balancer_status and balancer_status.get("stopped", False):
        print("Балансировка остановлена. Включаем...")
        router_client.config.settings.update_one(
            {"_id": "balancer"},
            {"$set": {"stopped": False}},
            upsert=True
        )
        print("Балансировка включена в настройках.")
    else:
        print("Балансировка уже активна.")
except Exception as e:
    print(f"Ошибка при проверке/включении балансировки: {e}")

# Ручной запуск балансировки
try:
    router_client.admin.command("balancerStart")
    print("Балансировка запущена вручную.")
except Exception as e:
    print(f"Ошибка при запуске балансировки: {e}")

# Проверка состояния кластера
try:
    shard_status = router_client.admin.command("listShards")
    print("Статус шардов:", shard_status)
except Exception as e:
    print(f"Ошибка при проверке статуса шардов: {e}")

# Проверка данных
try:
    db = router_client.test_db
    collection = db.test_collection
    count = collection.count_documents({})
    print(f"Количество документов в коллекции: {count}")
except Exception as e:
    print(f"Ошибка при проверке данных: {e}")


# Проверка распределения данных по шардам
try:
    stats = router_client.test_db.command("collStats", "test_collection")
    print("Статистика коллекции:", stats)
except Exception as e:
    print(f"Ошибка при получении распределения данных: {e}")