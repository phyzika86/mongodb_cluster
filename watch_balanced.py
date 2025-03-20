from pymongo import MongoClient
import json

# Подключение к MongoDB
client = MongoClient("mongodb://Alex_Y:123@localhost:27017/")
admin_db = client.admin

# Проверка версии MongoDB
server_info = client.server_info()
print("MongoDB Version:", server_info["version"])

# Проверка подключения к mongos
is_master = admin_db.command("isMaster")
if is_master.get("msg") != "isdbgrid":
    print("Error: Not connected to mongos. Please connect to the mongos router.")
else:
    print("Connected to mongos.")

# Проверка шардированных баз данных
result = admin_db.command("listDatabases")
admin_db.command("enableSharding", "test_db")
for db in result["databases"]:
    print(f"Database: {db['name']}, Sharded: {db.get('sharded', False)}")

shards = client.config.shards.find({})
print("\nShards:")
for shard in shards:
    print(f"Shard: {shard['_id']}, Host: {shard['host']}")

# Проверка шардированных коллекций
config_db = client.config
collections = config_db.collections.find({})
for collection in collections:
    print(f"Collection: {collection['_id']}, Sharded: {not collection.get('dropped', False)}")

# Анализ логов
logs = admin_db.command("getLog", "global")
for line in logs["log"]:
    if "balancer" in line or "chunk move" in line:
        print(line)

# Проверка ролей пользователя
roles = admin_db.command("usersInfo", "Alex_Y")
print("User Roles:", roles)

client = MongoClient("mongodb://localhost:27019/?directConnection=true")
config_status = client.admin.command("replSetGetStatus")
print(config_status)


try:
    admin_db.command("enableSharding", "test_db")
    print("Sharding enabled for database 'test_db'.")
except Exception as e:
    print(f"Error enabling sharding: {e}")

databases = client.config.databases.find({})
print("\nSharded Databases:")
for db in databases:
    print(f"Database: {db['_id']}, Sharded: {db.get('partitioned', False)}")

try:
    # Проверка распределения чанков
    chunks = client.config.chunks.find({"ns": "test_db.test_collection"})
    print("\nChunk Distribution for test_db.test_collection:")
    for chunk in chunks:
        print(f"Chunk: {chunk['_id']}, Shard: {chunk['shard']}")

    # Мониторинг операций перебалансировки
    current_operations = admin_db.command("currentOp", {"desc": "chunk move"})
    print("\nCurrent Chunk Move Operations:", json.dumps(str(current_operations)))

    # Проверка состояния балансировщика
    balancer_status = client.config.settings.find_one({"_id": "balancer"})
    print("\nBalancer Status:", balancer_status)
except Exception as e:
    print(f"Error in alternative monitoring methods: {e}")