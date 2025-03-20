from pymongo import MongoClient

# Подключение к MongoDB (используйте учетные данные администратора)
client = MongoClient("mongodb://localhost:27017/")
admin_db = client.admin

# Имя и пароль нового пользователя
new_username = "Alex_Y"
new_password = "123"

# Создание нового пользователя
try:
    admin_db.command("createUser", new_username, pwd=new_password, roles=[])
    print(f"User '{new_username}' successfully created.")
except Exception as e:
    print(f"Error creating user: {e}")

# Назначение роли clusterMonitor
try:
    admin_db.command("grantRolesToUser", new_username, roles=["clusterMonitor"])
    admin_db.command("grantRolesToUser", "Alex_Y", roles=["clusterManager"])
    print(f"Role 'clusterMonitor' successfully granted to user '{new_username}'.")
except Exception as e:
    print(f"Error granting role: {e}")

# Проверка ролей пользователя
roles_info = admin_db.command("usersInfo", new_username)
print(f"Roles for user '{new_username}':", roles_info)