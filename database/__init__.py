import mysql.connector
import random
import time
import json

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

class Database():
    def __init__(self):
        self.db = mysql.connector.connect(host=config["db_host"],user=config["db_user"],passwd=config["db_pass"],database=config["db_name"])
    
    def get_user(self, uuid):
        # Get specific user's data
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE uuid = {uuid}")
        
        user = None
        for user in cursor: pass
        return user
    
    def get_auto_miner(self, uuid):
        # Gets automining users
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM automining_data WHERE miner_id = {uuid}")

        autominer = None
        for autominer in cursor: pass
        return autominer