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
    
    def getUser(self, uuid):
        # Get specific user's data
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE uuid = {uuid}")
        
        user = None
        for user in cursor: pass
        return user