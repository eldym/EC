import mysql.connector
import random
import time
import json

def get_config():
    with open('config.json') as f:
        return json.load(f)

config = get_config()

START_DIFF = config["start_diff"]
START_DIFF_THRESHOLD = config["start_diff_threshold"]
START_REWARD = config["start_reward"]
LOOK_BACK = config["look_back"]
TARGET_TIME = config["target_time"]

class Database():
    def __init__(self):
        self.db = mysql.connector.connect(host=config["db_host"],user=config["db_user"],passwd=config["db_pass"],database=config["db_name"])
    
    # CREATORS

    def create_user(self, uuid):
        # Creates a new user if the user doesn't have an account
        if self.get_user(uuid) is None:
            self.db.cursor().execute("INSERT INTO users (uuid, balance, pool_b, solo_b, pooling) VALUES (%s,%s,%s,%s,%s)", (str(uuid), 0, 0, 0, 0))
            self.db.commit()
            return self.get_user(uuid)
        else: return False

    def create_pool_effort_log(self, uuid):
        # Creates a log for a user's pool contribution
        self.db.cursor().execute("INSERT INTO pool_b_data (block_id, miner, shares) VALUES (%s,%s,%s)", (int(self.get_current_block()[0]), uuid, 1))
        self.db.commit()
    
    def create_automining_log(self, uuid):
        # Creates a log for a user's automining session
        self.db.cursor().execute("INSERT INTO automining_data (miner_id, session_blocks_broken, session_total_shares, session_payout, start_unix) VALUES (%s,%s,%s,%s,%s)", (uuid, 0, 0, 0, int(time.time())))
        self.db.commit()

    def create_block(self):
        # Creates a new block
        cursor = self.db.cursor()
        cursor.execute("TRUNCATE TABLE pool_b_data")
        reward = self.calculate_reward()
        diff = self.calculate_difficulty()

        if diff == 0: # Should not ever equal 0
            diff = START_DIFF

        cursor.execute("INSERT INTO block (reward, difficulty, diff_threshold, unix_time) VALUES (%s,%s,%s,%s)", (reward, diff, START_DIFF_THRESHOLD, int(time.time())))
        self.db.commit()
    
    def create_transaction_log(self, send_uuid, recv_uuid, amount):
        # Creates a new transaction log
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO transactions (send_uuid, recv_uuid, amount, fee, unix_time) VALUES (%s,%s,%s,%s,%s)", (send_uuid, recv_uuid, amount, 0, int(time.time())))
        # Finds the transaction and returns it
        cursor.execute("SELECT * FROM transactions WHERE id = (SELECT MAX(id) FROM transactions)")
        for i in cursor: pass
        self.db.commit()
        return i
    
    # UPDATERS
    
    def update_user_bal(self, uuid, new_bal):
        # Updates specific user's balance
        self.db.cursor().execute("UPDATE users SET balance = %s WHERE uuid = %s", (new_bal, uuid))
        self.db.commit()

    def update_user_pooling_status(self, uuid):
        # Updates a user's mining method setting
        pooling = self.get_user(uuid)[4] # Gets user data to see if user is pooling
        if pooling <= 0: self.db.cursor().execute(f"UPDATE users SET pooling = pooling + 1 WHERE uuid = {uuid}")
        elif pooling >= 1: self.db.cursor().execute(f"UPDATE users SET pooling = pooling - 1 WHERE uuid = {uuid}")
        self.db.commit()
        return "Pool" if pooling == 0 else "Solo"
    
    def update_user_automining_status(self, uuid):
        # Updates a user's automated mining setting
        user = self.get_auto_miner(uuid)
        if user is not None:
            self.db.cursor().execute(f"DELETE FROM automining_data WHERE miner_id = {uuid}")
            self.db.commit()
            return False
        else:
            self.create_automining_log(uuid)
            return True

    # INCREMENTERS

    def increment_user_block_count(self, uuid, type):
        # Updates specific user's balance
        if type == "pool": self.db.cursor().execute(f"UPDATE users SET pool_b = pool_b + 1 WHERE uuid = {uuid}")
        else: self.db.cursor().execute(f"UPDATE users SET solo_b = solo_b + 1 WHERE uuid = {uuid}")
        self.db.commit()

    def increment_pool_effort(self, uuid):
        # Updates specific user's effort in a pool
        self.db.cursor().execute(f"UPDATE pool_b_data SET shares = shares + 1 WHERE miner = {uuid}")
        self.db.commit()

    def increment_user_automine_session_block(self, uuid):
        # Updates specific user's Automine Session Block Count
        self.db.cursor().execute(f"UPDATE automining_data SET session_blocks_broken = session_blocks_broken + 1 WHERE miner_id = {uuid}")
        self.db.commit()
    
    def increment_user_automine_session_hashes(self, uuid):
        # Updates specific user's Automine Session Hash Count
        self.db.cursor().execute(f"UPDATE automining_data SET session_total_shares = session_total_shares + 1 WHERE miner_id = {uuid}")
        self.db.commit()

    def increment_user_automine_session_payout(self, uuid, amt):
        # Updates specific user's total Automine Session Payout Amount
        self.db.cursor().execute(f"UPDATE automining_data SET session_payout = session_payout + {amt} WHERE miner_id = {uuid}")
        self.db.commit()

    # GETTERS

    def get_user(self, uuid):
        # Get specific user's data
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE uuid = {uuid}")
        
        user = None
        for user in cursor: pass
        return user
        
    def get_block(self, block_number):
        # Get specific block data
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM block WHERE block_number = {block_number}")

        block = None
        for block in cursor: pass
        return block
    
    def get_all_blocks(self):
        # Gets all block data
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM block")

        blocks = []
        for block in cursor:
            blocks.append(block)
        return blocks
    
    def get_current_block(self):
        # Get current block data
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM block WHERE block_number = (SELECT MAX(block_number) FROM block)")

        block = None
        for block in cursor: pass
        return block
    
    def getTransaction(self, id):
        # Get specific transaction data from transaction ID
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM transactions WHERE id = {id}")

        transaction = None
        for transaction in cursor: pass
        return transaction
    
    def get_pool_miner(self, uuid):
        # Gets a specific pool miner
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM pool_b_data WHERE miner = {uuid}")

        miner = None
        for miner in cursor: pass
        return miner
    
    def get_pool_miners(self):
        # Gets all pool miners
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM pool_b_data")

        miners = []
        for miner in cursor:
            miners.append(miner)
        return miners
    
    def get_pool_share_sum(self):
        # Gets and calculates the total share sum in the pool
        cursor = self.db.cursor()
        cursor.execute("SELECT SUM(shares) FROM pool_b_data")

        data = None
        for data in cursor: pass
        return data
    
    def get_auto_miner(self, uuid):
        # Gets an automining user
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM automining_data WHERE miner_id = {uuid}")

        autominer = None
        for autominer in cursor: pass
        return autominer
    
    def get_auto_miners(self):
        # Gets all automining users
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM automining_data")

        miners = []
        for miner in cursor:
            miners.append(miner)
        return miners
    
    def get_balances_descending(self):
        # Get user data in descending order of balance
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM users ORDER BY balance DESC")

        users = []
        for user in cursor: 
            users.append(user)
        return users
    
    def get_pool_block_descending(self):
        # Get user data in descending order of broken pool blocks
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM users ORDER BY pool_b DESC")

        users = []
        for user in cursor: 
            users.append(user)
        return users
    
    def get_solo_block_descending(self):
        # Get user data in descending order of broken solo blocks
        cursor = self.db.cursor()
        cursor.execute(f"SELECT * FROM users ORDER BY solo_b DESC")

        users = []
        for user in cursor: 
            users.append(user)
        return users
    
    def get_supply(self):
        # Gets the total amount of coins in emission
        cursor = self.db.cursor()
        cursor.execute("SELECT SUM(balance) FROM users")

        data = None
        for data in cursor: pass
        return data
    
    # CORE FUNCTIONS
    
    def transaction(self, send_uuid, recv_uuid, amount):
        sender = None
        amount = float(amount)
        if send_uuid != "Coinbase": sender = self.get_user(send_uuid)

        if send_uuid == "Coinbase" or float(sender[1]) >= amount:
            if type(recv_uuid) is str:
                reciept = self.transaction_aux(recv_uuid, send_uuid, sender, amount)
            elif type(recv_uuid) is list and type(amount) is list: # WIP
                reciept = []
                i = 0
                while i < len(recv_uuid):
                    reciept.append(self.__transaction_aux(recv_uuid[i], send_uuid, sender, amount[i]))
                    i += 1
            else: return "Error"
            return reciept
        else:
            return "Your balance is too low."
        
    def __transaction_aux(self, recv_uuid, send_uuid, sender, amount):
        # Private auxillary function
        recver = self.get_user(recv_uuid)
        try: verify = recver[1]
        except: return False
        else:
            if send_uuid != "Coinbase": self.update_user_bal(send_uuid, float(sender[1])-amount)
            self.update_user_bal(recv_uuid, float(recver[1])+amount)
            reciept = self.create_transaction_log(send_uuid, recv_uuid, amount)
            return reciept
        
    def mine(self, uuid):
        block = self.get_current_block()
        pooling = self.get_user(uuid)[4]
        auto_status = self.get_auto_miner(uuid)
        guess = random.randint(0,block[2])
        reciept = None

        if pooling == 1:
            if self.get_pool_miner(uuid) is not None: self.increment_pool_effort(str(uuid))
            else: self.create_pool_effort_log(uuid)
        
        if guess < block[3]: # broken block procedure
            if pooling == 1: # pool
                reciept = []
                miners = self.get_pool_miners()
                summed = self.get_pool_share_sum()

                for miner in miners:
                    self.increment_user_block_count(miner[1], 'pool')
                    result = self.transaction("Coinbase", miner[1], block[1]*(miner[2]/summed[0]))

                    if self.get_auto_miner(miner[1]) is not None:
                        self.increment_user_automine_session_payout(miner[1], block[1]*(miner[2]/summed[0]))

                    reciept.append(result)

            elif pooling == 0: # solo
                self.increment_user_block_count(str(uuid), 'solo')
                reciept = self.transaction("Coinbase", str(uuid), block[1])

                if self.get_auto_miner(uuid) is not None:
                    self.increment_user_automine_session_payout(uuid, block[1])

            if auto_status is not None:
                self.increment_user_automine_session_block(uuid)

            self.create_block()

        if auto_status is not None:
            self.increment_user_automine_session_hashes(uuid)

        return guess, reciept
    
    # CALCULATIONS

    def calculate_difficulty(self):
        curr = self.get_current_block()

        if curr is not None:
            # Get data n blocks before
            if curr[0] >= LOOK_BACK:
                to_get = curr[0]-LOOK_BACK+1
                n_blocks = LOOK_BACK
            else:
                to_get = 1
                n_blocks = curr[0]

            # Gets the lookback block data
            look_back_blocks = []
            for i in range(LOOK_BACK):
                look_back_blocks.append(self.get_block(to_get+i))

            # Gets the lookback block difficulties
            look_back_difficulties = []
            for i in look_back_blocks:
                try: look_back_difficulties.append(i[2])
                except: pass
            
            # Calculates the difficulty average
            diff_average = sum(look_back_difficulties)/LOOK_BACK

            # Gets the total of Unix seconds between current block break and 3 blocks before
            obsMineTime = int(time.time()) - look_back_blocks[0][4]

            # Print calculations to console for checking
            print('Block Completed! Here are the block statistics:')
            print(f'Averaged time (s):',obsMineTime)
            print(f'Expected time (s):',TARGET_TIME*n_blocks)
            print(f'Time deviation from expected: ×{(TARGET_TIME*n_blocks)/obsMineTime:.4f}')
            print(f'Time deviation percentage: {(TARGET_TIME*n_blocks)/obsMineTime*100:.4f}%')
            print(f'Averaged difficulty: {diff_average}')
            print(f'Adjusted difficulty: {int(diff_average*((TARGET_TIME*n_blocks)/obsMineTime))}')
            print()

            # Smooths out difficulty increase to prevent extreme difficulty change shock
            if ((TARGET_TIME*LOOK_BACK)/obsMineTime) > 2: print('Difficulty multiplied by 2\n'); return curr[2]*(2)
            elif ((TARGET_TIME*LOOK_BACK)/obsMineTime) < 1/2: print('Difficulty divided by 2\n'); return curr[2]*(1/2)
            else: print('Difficulty on normal math\n'); return int(diff_average*((TARGET_TIME*LOOK_BACK)/obsMineTime))
        else:
            return START_DIFF
        
    def calculate_reward(self):
        curr = self.get_current_block()
        reward = START_REWARD

        if curr is not None and curr[0] > 105120:
            power = 1 + curr[0]//105120
            reward = reward/(2**power)

        return reward