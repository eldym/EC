from data import *

# One-time startup. As soon as this is completed, execute main.py.
try: ecDataGet.getDB()
except: 
    try: ecDatabaseCreate.fullCreate()
    except: print("Error connecting to MySQL.")
    else:print("DB successfully created!")
else: print("DB already exists!")