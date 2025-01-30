import mysql.connector
import random
from config import HB_HOST, DB_USER, DB_PASS, DB_NAME, ERROR_TXT, START_DIFF, START_REWARD, START_DIFF_THRESHOLD, BLOCKS_TO_LOOK_BACK, TARGET_BLOCK_BREAK_TIME
import time

DB_CONN_ERROR = ERROR_TXT, "\nCannot connect to MySQL database."

# Data starting
class ecDatabaseCreate:
    def fullCreate():
        # Runs full creation sequence
        ecDatabaseCreate.sqlDBCreate()
        ecDatabaseCreate.sqlTablesCreate()
        ecDataManip.createBlock()
        print("Completed full MySQL EC Database creation.\n")

    def sqlDBCreate():
        # Creates the MySQL Database (if it doesn't already exist)
        db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS)
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ecdata")
        print("Created ecdata Database.")

    def sqlTablesCreate():
        # Creates the users and transactions tables (if they don't already exist)
        try: db = mysql.connector.connect(host=HB_HOST,user=DB_USER,passwd=DB_PASS,database=DB_NAME)
        except: print(DB_CONN_ERROR)
        else:
            cursor = db.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (uuid VARCHAR(20) NOT NULL PRIMARY KEY, balance DECIMAL(18,6) UNSIGNED NOT NULL, pool_b MEDIUMINT UNSIGNED NOT NULL, solo_b MEDIUMINT UNSIGNED NOT NULL, pooling BOOL NOT NULL, UNIQUE(uuid))")
            print("Created users Table.")
            cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT, send_uuid VARCHAR(20) NOT NULL, recv_uuid VARCHAR(20) NOT NULL, amount DECIMAL(18,6) UNSIGNED NOT NULL, fee DECIMAL(18,6) UNSIGNED NOT NULL, unix_time INT(11) UNSIGNED NOT NULL)")
            print("Created transactions Table.")
            cursor.execute("CREATE TABLE IF NOT EXISTS block (block_number INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, reward DECIMAL(18,6) UNSIGNED NOT NULL, difficulty INT UNSIGNED NOT NULL, diff_threshold INT UNSIGNED NOT NULL, unix_time INT(11) UNSIGNED NOT NULL, UNIQUE(block_number))")
            print("Created block Table.")
            cursor.execute("CREATE TABLE IF NOT EXISTS pool_b_data (block_id INT UNSIGNED NOT NULL, miner VARCHAR(20) NOT NULL, shares INT UNSIGNED NOT NULL, FOREIGN KEY(miner) REFERENCES users(uuid), FOREIGN KEY(block_id) REFERENCES block(block_number))")
            print("Created pool_b_data Table.")
            cursor.execute("CREATE TABLE IF NOT EXISTS automining_data (miner_id VARCHAR(20) NOT NULL PRIMARY KEY, session_blocks_broke INT UNSIGNED NOT NULL, session_total_shares INT UNSIGNED NOT NULL, start_unix INT(11) UNSIGNED NOT NULL, FOREIGN KEY(miner_id) REFERENCES users(uuid))")
            print("Created automining_data Table.")

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
    
    def getUserSentTransactions(uuid):
        # Get specific send transaction data of a user
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM transactions WHERE send_uuid = {uuid}")

        transactions = []
        for transaction in cursor: transactions.append(transaction)
        return transaction
    
    def getUserRecvTransactions(uuid):
        # Get specific recieving transaction data of a user
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM transactions WHERE recv_uuid = {uuid}")

        transactions = []
        for transaction in cursor: transactions.append(transaction)
        return transaction
    
    def getBalancesDescending():
        # Get user data in descending order of balance
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users ORDER BY balance DESC")

        users = []
        for user in cursor: 
            users.append(user)
        return users
    
    def getPoolBlockDescending():
        # Get user data in descending order of broken pool blocks
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users ORDER BY pool_b DESC")

        users = []
        for user in cursor: 
            users.append(user)
        return users
    
    def getSoloBlockDescending():
        # Get user data in descending order of broken solo blocks
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users ORDER BY solo_b DESC")

        users = []
        for user in cursor: 
            users.append(user)
        return users
    
    def getBlock(blockNo):
        # Get specific block data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM block WHERE block_number = {blockNo}")

        block = None
        for block in cursor: pass
        return block

    def getAllBlocks():
        # Gets all block data
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM block")

        blocks = []
        for block in cursor:
            blocks.append(block)
        return blocks
    
    def getTransaction(id):
        # Get specific transaction data from transaction ID
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
    
    def getAutoMiner(uuid):
        # Gets automining users
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM automining_data WHERE miner_uuid = {uuid}")

        autominer = None
        for autominer in cursor: pass
        return autominer
    
    def getAutoMiners():
        # Gets automining users
        db = ecDataGet.getDB()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM automining_data")

        automining = []
        for user in cursor: 
            automining.append(user)
        return automining
    
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
        db.cursor().execute("INSERT INTO pool_b_data (block_id, miner, shares) VALUES (%s,%s,%s)", (int(ecDataGet.getCurrentBlock()[0]), uuid, 1))
        db.commit()
    
    def createAutominingLog(uuid):
        # Creates a log for a user's pool contribution
        db = ecDataGet.getDB()
        db.cursor().execute("INSERT INTO automining_data (miner_uuid, session_blocks_broken, session_total_shares, start_unix) VALUES (%s,%s,%s,%s)", (uuid, 0, 0, int(time.time())))
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

    def updateUserPoolingStatus(uuid):
        # Updates a user's mining method setting
        user = ecDataGet.getUser(uuid)
        db = ecDataGet.getDB()
        if user[4] <= 0: db.cursor().execute(f"UPDATE users SET pooling = pooling + 1 WHERE uuid = {uuid}")
        elif user[4] >= 1: db.cursor().execute(f"UPDATE users SET pooling = pooling - 1 WHERE uuid = {uuid}")
        db.commit()
        return "Pool" if user[4] == 0 else "Solo"
    
    def updateUserAutominingStatus(uuid):
        # Updates a user's automated mining setting
        user = ecDataGet.getAutoMiner(uuid)
        db = ecDataGet.getDB()
        if user is not None:
            db.cursor().execute(f"DELETE FROM automining_data WHERE miner_uuid = {uuid}")
            db.commit()
            return False
        else:
            ecDataManip.createAutominingLog(uuid)
            return True

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

        if curr is not None:
            # Get data n blocks before
            if curr[0] >= BLOCKS_TO_LOOK_BACK:
                to_get = curr[0]-BLOCKS_TO_LOOK_BACK+1
                n_blocks = BLOCKS_TO_LOOK_BACK
            else:
                to_get = 1
                n_blocks = curr[0]

            # Gets the lookback block data
            look_back_blocks = []
            for i in range(BLOCKS_TO_LOOK_BACK):
                look_back_blocks.append(ecDataGet.getBlock(to_get+i))

            # Gets the lookback block difficulties
            look_back_difficulties = []
            for i in look_back_blocks:
                look_back_difficulties.append(i[2])
            
            # Calculates the difficulty average
            diff_average = sum(look_back_difficulties)/BLOCKS_TO_LOOK_BACK

            # Gets the total of Unix seconds between current block break and 3 blocks before
            obsMineTime = int(time.time()) - look_back_blocks[0][4]

            # Print calculations to console for checking
            print('Block Completed! Here are the block statistics:')
            print(f'Averaged time (s):',obsMineTime)
            print(f'Expected time (s):',TARGET_BLOCK_BREAK_TIME*n_blocks)
            print(f'Time deviation from expected: ×{(TARGET_BLOCK_BREAK_TIME*n_blocks)/obsMineTime:.4f}')
            print(f'Time deviation percentage: {(TARGET_BLOCK_BREAK_TIME*n_blocks)/obsMineTime*100:.4f}%')
            print(f'Averaged difficulty: {diff_average}')
            print(f'Adjusted difficulty: {int(diff_average*((TARGET_BLOCK_BREAK_TIME*n_blocks)/obsMineTime))}')
            print()

            # Smooths out difficulty increase to prevent extreme difficulty change shock
            if ((TARGET_BLOCK_BREAK_TIME*BLOCKS_TO_LOOK_BACK)/obsMineTime) > 2: print('diff multiplied by 2\n'); return curr[2]*(2)
            elif ((TARGET_BLOCK_BREAK_TIME*BLOCKS_TO_LOOK_BACK)/obsMineTime) < 1/2: print('diff divided by 2\n'); return curr[2]*(1/2)
            else: print('diff normal math\n'); return int(diff_average*((TARGET_BLOCK_BREAK_TIME*BLOCKS_TO_LOOK_BACK)/obsMineTime))
        else:
            return START_DIFF
        
    def calculateReward():
        curr = ecDataGet.getCurrentBlock()
        reward = START_REWARD

        if curr is not None and curr[0] > 105120:
            power = 1 + curr[0]//105120
            reward = reward/(2**power)

        return reward