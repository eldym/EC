# Bot config
PREFIXES = ['!', 'ec!'] # Your prefixes
COOLDOWN = 2 # Cooldown in seconds
DEFAULT_PREFIX = PREFIXES[0] # Default/fallback prefix
TOKEN = '' # Your bot's token here

# Currency config
CURRENCY = 'EC' # Your currency symbol
CURRENCY_EMOJI = '<:ec:1220995523469643786>' # Optional currency emoji
DISPLAY_CURRENCY = f'{CURRENCY}{' '+CURRENCY_EMOJI if len(CURRENCY_EMOJI) > 0 else ''}' # Used to display currency + emoji in embeds in main

# Embed config
EMB_COLOUR = 0x000000 # Embed colour
EC_THUMBNAIL_LINK = 'https://cdn.discordapp.com/attachments/791182073263685672/1323407110528172143/ec_spin.gif?ex=6774666a&is=677314ea&hm=c6e248a36175fcca642e241488ae733245f898c09f6ed22c2360c7045a474e6a' # Picture that shows on top right of embed on transaction info/mining/etc.
ERROR_TXT = 'Error!' # Error text
OUTPUT_CHANNEL = None # Enter a channel ID to output completed block info here

# Admin config
ADMIN_ID = None # Discord User ID to use Admin commands

# DB config
HB_HOST = 'localhost' # Your host
DB_USER = 'root' # Your MySQL username
DB_PASS = 'root' # Your MySQL password
DB_NAME = 'ecdata' # MySQL database name

# Block config
START_DIFF = 1 # Start difficulty prior to automatic difficulty calculations
START_DIFF_THRESHOLD = 10 # Number that guess must be less than or equal to this number to break block 
START_REWARD = 500 # Reward amount upon breaking block
BLOCKS_TO_LOOK_BACK = 3 # Number of blocks to look back up (used for calculating difficulty)
TARGET_BLOCK_BREAK_TIME = 900 # How many seconds should it take for a block to break