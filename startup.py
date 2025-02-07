import json
import mysql.connector

from database import Database

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

HB_HOST=config["db_host"]
DB_USER=config["db_user"]
DB_PASS=config["db_pass"]
DB_NAME=config["db_name"]

SUCCESS = '\033[92m'
FAIL = '\033[91m'
ENDC = '\033[0m'

class database_startup():
    def fullCreate(self):
        # Creates database
        print("DATABASE GENERATION\n")
        try: self.mysql_db_create()
        except Exception as e: print(f"{FAIL}Error making database!{ENDC}\nException:",e) 
        else: 
            print(f"{SUCCESS}Created {DB_NAME} Database.{ENDC}\n")

            # Creates tables
            print("TABLE GENERATION\n")
            self.mysql_tables_create()

            # Creates the first block
            print("BLOCK GENERATION\n")
            try: Database.create_block(Database())
            except Exception as e: print(f"{FAIL}Error making genesis block!{ENDC}\nException:",e)
            else: 
                print(f"{SUCCESS}Created genesis block.{ENDC}\n")
                print(f"{SUCCESS}Completed full MySQL EC Database creation.{ENDC}\n") # Yippee!

    def mysql_db_create(self):
        # Creates the MySQL Database (if it doesn't already exist)
        db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS)
        print(f"{SUCCESS}Connected to MySQL.{ENDC}")
        cursor = db.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"{SUCCESS}Executed create Database to MySQL.{ENDC}")

    def mysql_tables_create(self):
        # Creates the users and transactions tables (if they don't already exist)
        try: db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS,database=DB_NAME)
        except: print(f"{FAIL}Error getting database!{ENDC}\nException:",e)
        else:
            cursor = db.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (uuid VARCHAR(20) NOT NULL PRIMARY KEY, balance DECIMAL(18,6) UNSIGNED NOT NULL, pool_b MEDIUMINT UNSIGNED NOT NULL, solo_b MEDIUMINT UNSIGNED NOT NULL, pooling BOOL NOT NULL, username VARCHAR(20) NOT NULL, UNIQUE(uuid))")
            print(f"{SUCCESS}Created users Table.{ENDC}")
            cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT, send_uuid VARCHAR(20) NOT NULL, recv_uuid VARCHAR(20) NOT NULL, amount DECIMAL(18,6) UNSIGNED NOT NULL, fee DECIMAL(18,6) UNSIGNED NOT NULL, unix_time INT(11) UNSIGNED NOT NULL)")
            print(f"{SUCCESS}Created transactions Table.{ENDC}")
            cursor.execute("CREATE TABLE IF NOT EXISTS block (block_number INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, reward DECIMAL(18,6) UNSIGNED NOT NULL, difficulty INT UNSIGNED NOT NULL, diff_threshold INT UNSIGNED NOT NULL, unix_time INT(11) UNSIGNED NOT NULL, UNIQUE(block_number))")
            print(f"{SUCCESS}Created block Table.{ENDC}")
            cursor.execute("CREATE TABLE IF NOT EXISTS pool_b_data (block_id INT UNSIGNED NOT NULL, miner VARCHAR(20) NOT NULL, shares INT UNSIGNED NOT NULL, FOREIGN KEY(miner) REFERENCES users(uuid), FOREIGN KEY(block_id) REFERENCES block(block_number))")
            print(f"{SUCCESS}Created pool_b_data Table.{ENDC}")
            cursor.execute("CREATE TABLE IF NOT EXISTS automining_data (miner_id VARCHAR(20) NOT NULL PRIMARY KEY, session_blocks_broken INT UNSIGNED NOT NULL, session_total_shares INT UNSIGNED NOT NULL, session_payout DECIMAL(18,6) UNSIGNED NOT NULL, start_unix INT(11) UNSIGNED NOT NULL, FOREIGN KEY(miner_id) REFERENCES users(uuid))")
            print(f"{SUCCESS}Created automining_data Table.{ENDC}")
            print()

# One-time startup. As soon as this is completed, execute bot.py.
try: db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS,database=DB_NAME)
except: 
    try: database_startup.fullCreate(database_startup())
    except Exception as e: print(f"{FAIL}Error connecting to MySQL!{ENDC}\nException:",e)
    else:print(f"{SUCCESS}DB successfully created!{ENDC}")
else: print(f"{FAIL}Error: DB already exists!{ENDC}")