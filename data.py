import mysql.connector
import random
from config import HB_HOST, DB_USER, DB_PASS, DB_NAME, ERROR_TXT, START_DIFF, START_REWARD, START_DIFF_THRESHOLD
import time

DB_CONN_ERROR = ERROR_TXT, "\nCannot connect to MySQL database."

# Data starting
class ecDatabaseCreate:
    def fullCreate():
        # Runs full creation sequence
        ecDatabaseCreate.sqlDBCreate()
        ecDatabaseCreate.sqlTablesCreate()
        ecDataManip.createBlock()
        return "ran full create"

    def sqlDBCreate():
        # Creates the MySQL Database (if it doesn't already exist)
        db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS)
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ecdata")

    def sqlTablesCreate():
        # Creates the users and transactions tables (if they don't already exist)
        try: db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS,database=DB_NAME)
        except: print(DB_CONN_ERROR)
        else:
            cursor = db.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (uuid VARCHAR(20) NOT NULL, balance DECIMAL(18,6) UNSIGNED NOT NULL, pool_b MEDIUMINT UNSIGNED NOT NULL, solo_b MEDIUMINT UNSIGNED NOT NULL, pooling BOOL NOT NULL, automining BOOL NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id int UNSIGNED NOT NULL AUTO_INCREMENT, send_uuid VARCHAR(20) NOT NULL, recv_uuid VARCHAR(20) NOT NULL, amount DECIMAL(18,6) UNSIGNED NOT NULL, fee DECIMAL(18,6) UNSIGNED NOT NULL, unix_time INT(11) UNSIGNED NOT NULL, UNIQUE (id))")
            cursor.execute("CREATE TABLE IF NOT EXISTS block (block_number INT PRIMARY KEY AUTO_INCREMENT, reward DECIMAL(18,6) UNSIGNED NOT NULL, difficulty INT UNSIGNED NOT NULL, diff_threshold INT UNSIGNED NOT NULL, unix_time INT(11) UNSIGNED NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS pool_b_data (block_number INT UNSIGNED NOT NULL, miner VARCHAR(20) NOT NULL, shares INT UNSIGNED NOT NULL)")

# Data getting
class ecDataGet:

    def getDB():
        # Gets the database
        db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS,database=DB_NAME)
        return db
    
    def getAllUsers():
        # Get all user data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users")

        users = []
        for user in cursor:
            users.append(user)
        return users

    def getUser(uuid):
        # Get specific user's data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE uuid = {uuid}")
        
        user = None
        for user in cursor: pass
        return user
    
    def getBlock(blockNo):
        # Get specific block data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM block WHERE block_number = {blockNo}")

        block = None
        for block in cursor: pass
        return block
    
    def getTransaction(id):
        # Get specific transaction data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM transactions WHERE id = {id}")

        transaction = None
        for transaction in cursor: pass
        return transaction
    
    def getCurrentBlock():
        # Get current block data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM block WHERE block_number = (SELECT MAX(block_number) FROM block)")

        block = None
        for block in cursor: pass
        return block
    
    def getPoolMiners():
        # Gets pool miner data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pool_b_data")

        miners = []
        for miner in cursor:
            miners.append(miner)
        return miners
    
    def getPoolMiner(uuid):
        # Gets individual pool miner data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM pool_b_data WHERE miner = {uuid}")

        miner = None
        for miner in cursor: pass
        return miner
    
    def getSupply():
        # Gets the total amount of shares
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute("SELECT SUM(balance) FROM users")

        data = None
        for data in cursor: pass
        return data

    def getPoolShareSum():
        # Gets the total amount of shares
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute("SELECT SUM(shares) FROM pool_b_data")

        data = None
        for data in cursor: pass
        return data
    
# Data manipulating
class ecDataManip:
    
    def createUser(uuid):
        # Creates a new user if the user doesn't have an account
        if ecDataGet.getUser(uuid) is None:
            db = ecDataGet.getDB()
            db.cursor().execute("INSERT INTO users (uuid, balance, pool_b, solo_b, pooling) VALUES (%s,%s,%s,%s,%s)", (str(uuid), 0, 0, 0, 0))
            db.commit()
            return ecDataGet.getUser(uuid)
        else: return False

    def createPoolEffortLog(uuid):
        # Creates a log for a user's pool contribution
        db = ecDataGet.getDB()
        db.cursor().execute("INSERT INTO pool_b_data (block_number, miner, shares) VALUES (%s,%s,%s)", (int(ecDataGet.getCurrentBlock()[0]), uuid, 1))
        db.commit()
    
    def createTransactionLog(send_uuid, recv_uuid, amount):
        # Creates a new transaction log
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute("INSERT INTO transactions (send_uuid, recv_uuid, amount, fee, unix_time) VALUES (%s,%s,%s,%s,%s)", (send_uuid, recv_uuid, amount, 0, int(time.time())))
        # Finds the transaction and returns it
        cursor.execute("SELECT * FROM transactions WHERE id = (SELECT MAX(id) FROM transactions)")
        for i in cursor: pass
        db.commit()
        return i
    
    def updateUserBal(uuid, newBal):
        # Updates specific user's balance
        db = ecDataGet.getDB()
        db.cursor().execute("UPDATE users SET balance = %s WHERE uuid = %s", (newBal, uuid))
        db.commit()

    def incrementUserBlockCount(uuid, type):
        # Updates specific user's balance
        db = ecDataGet.getDB()
        if type == "pool": db.cursor().execute(f"UPDATE users SET pool_b = pool_b + 1 WHERE uuid = {uuid}")
        else: db.cursor().execute(f"UPDATE users SET solo_b = solo_b + 1 WHERE uuid = {uuid}")
        db.commit()

    def incrementPoolEffort(uuid):
        # Updates specific user's effort in a pool
        db = ecDataGet.getDB()
        db.cursor().execute(f"UPDATE pool_b_data SET shares = shares + 1 WHERE miner = {uuid}")
        db.commit()

    def updateUserPoolingStatus(uuid):
        # Updates a user's mining status setting
        user = ecDataGet.getUser(uuid)
        db = ecDataGet.getDB()
        if user[4] == 0: db.cursor().execute(f"UPDATE users SET pooling = pooling + 1 WHERE uuid = {uuid}")
        elif user[4] == 1: db.cursor().execute(f"UPDATE users SET pooling = pooling - 1 WHERE uuid = {uuid}")
        db.commit()
        return "Pool" if user[4] == 0 else "Solo"

    def createBlock():
        # Creates a new block
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute("TRUNCATE TABLE pool_b_data")
        reward = calculations.calculateReward()
        diff = calculations.calculateDifficulty()

        cursor.execute("INSERT INTO block (reward, difficulty, diff_threshold, unix_time) VALUES (%s,%s,%s,%s)", (reward, diff, START_DIFF_THRESHOLD, int(time.time())))
        db.commit()

    def dbExecute(string, tuple):
        # Only use for basic operations
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(string, tuple)

class ecCore:

    def transaction(send_uuid, recv_uuid, amount):
        sender = None
        amount = float(amount)
        if send_uuid != "Coinbase": sender = ecDataGet.getUser(send_uuid)

        if send_uuid == "Coinbase" or float(sender[1]) >= amount:
            if type(recv_uuid) is str:
                reciept = ecCore.transaction_aux(recv_uuid, send_uuid, sender, amount)
            elif type(recv_uuid) is list and type(amount) is list: # WIP
                reciept = []
                i = 0
                while i < len(recv_uuid):
                    reciept.append(ecCore.transaction_aux(recv_uuid[i], send_uuid, sender, amount[i]))
                    i += 1
            else: return "Error"
            return reciept
        else:
            return "Your balance is too low."

    def transaction_aux(recv_uuid, send_uuid, sender, amount):
        recver = ecDataGet.getUser(recv_uuid)
        try: verify = recver[1]
        except: return False
        else:
            if send_uuid != "Coinbase": ecDataManip.updateUserBal(send_uuid, float(sender[1])-amount)
            ecDataManip.updateUserBal(recv_uuid, float(recver[1])+amount)
            reciept = ecDataManip.createTransactionLog(send_uuid, recv_uuid, amount)
            return reciept

    def mine(uuid):
        block = ecDataGet.getCurrentBlock()
        pooling = ecDataGet.getUser(uuid)[4]
        guess = random.randint(0,block[2])
        reciept = None

        if pooling == 1:
            if ecDataGet.getPoolMiner(uuid) is not None: ecDataManip.incrementPoolEffort(str(uuid))
            else: ecDataManip.createPoolEffortLog(uuid)
        
        if guess < block[3]: # broken block procedure
            if pooling == 1: # pool
                reciept = []
                miners = ecDataGet.getPoolMiners()
                summed = ecDataGet.getPoolShareSum()
                print(summed)
                for miner in miners:
                    ecDataManip.incrementUserBlockCount(miner[1], 'pool')
                    result = ecCore.transaction("Coinbase", miner[1], block[1]*(miner[2]/summed[0]))
                    print(result)
                    reciept.append(result)
            elif pooling == 0: # solo
                ecDataManip.incrementUserBlockCount(str(uuid), 'solo')
                reciept = ecCore.transaction("Coinbase", str(uuid), block[1])
            ecDataManip.createBlock()
            
        return guess, reciept
        
class calculations:
    def calculateDifficulty():
        curr = ecDataGet.getCurrentBlock()

        if curr is not None and curr[0] >= 6:
            # Get data points
            farPrev = ecDataGet.getBlock(curr[0]-5)

            # Gets the total of Unix seconds between current block and 5 blocks before
            obsMineTime = curr[4] - farPrev[4]

            # Expected time (s) taken to mine 6 blocks
            expMineTime = 1800

            # Print calculations to console for checking
            print('Block Completed! Here are the block statistics:')
            print('Averaged time (s):',obsMineTime)
            print('Expected time (s):',expMineTime)
            print(f'Deviation from expected: ×{expMineTime/obsMineTime:.4f}')
            print(f'Deviation percentage: {expMineTime/obsMineTime*100:.4f}%')
            print()

            # Smooths out difficulty increase to prevent extreme difficulty change shock
            if (expMineTime/obsMineTime) > 2: print('diff multiplied by 2\n'); return curr[2]*(2)
            elif (expMineTime/obsMineTime) < 1/2: print('diff divided by 2\n'); return curr[2]*(1/2)
            else: print('diff normal math\n'); return curr[2]*(expMineTime/obsMineTime)
        else:
            return START_DIFF
        
    def calculateReward():
        curr = ecDataGet.getCurrentBlock()
        reward = START_REWARD

        if curr is not None and curr[0] > 105120:
            power = 1 + curr[0]//105120
            reward = reward/(2**power)

        return reward