# Bot config
PREFIXES = ['!', 'ec!', '<@1200004156820303873> '] # Your prefixes
DEFAULT_PREFIX = PREFIXES[0] # Default/fallback prefix
CURRENCY = 'EC <:ec:1220995523469643786>' # Currency
COOLDOWN = 2 # Cooldown in seconds
EMB_COLOUR = 0x000000 # Embed colour
OUTPUT_CHANNEL = None # Enter a channel ID to output completed block info here
TOKEN = '' # Your bot's token here
EC_THUMBNAIL_LINK = 'https://cdn.discordapp.com/attachments/791182073263685672/1323407110528172143/ec_spin.gif?ex=6774666a&is=677314ea&hm=c6e248a36175fcca642e241488ae733245f898c09f6ed22c2360c7045a474e6a' # Picture that shows on top right of embed on transaction info/mining/etc.
ERROR_TXT = 'Error!' # Error text

# Admin config
ADMIN_ID = None # Your Discord User ID to use Admin commands

# DB config
HB_HOST = 'localhost' # Your host
DB_USER = 'root' # Your MySQL username
DB_PASS = 'root' # Your MySQL password
DB_NAME = 'ecdata' # MySQL database name

# Block config
START_DIFF = 1 # Start difficulty prior to automatic difficulty calculations
START_DIFF_THRESHOLD = 10 # Guess must be less than or equal to this number to break block 
START_REWARD = 500 # Reward amount upon breaking block