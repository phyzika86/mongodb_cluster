from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
config_status = client.config.command("replSetGetStatus")
print("Config Server Replica Set Status:", config_status)