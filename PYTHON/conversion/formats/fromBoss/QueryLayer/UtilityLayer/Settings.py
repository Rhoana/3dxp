import os

BFLY_CONFIG = {}
CONFIG_FILENAME = ''

# HTTP port for server
PORT = int(BFLY_CONFIG.get('port', 2001))
# Path to database and kind of database
DB_UPDATE = BFLY_CONFIG.get('db-update', True)
DB_PATH = BFLY_CONFIG.get('db-path', 'bfly.db')
DB_TYPE = BFLY_CONFIG.get('db-type', 'Nodb')
DB_PORT = BFLY_CONFIG.get('db-port', 27017)

# Path to root edit directory
EDIT_PATH = BFLY_CONFIG.get('edit-path', os.sep)

# Path and level of the log file
LOG_PATH = BFLY_CONFIG.get('log-path', 'bfly.log')
LOG_LEVEL = BFLY_CONFIG.get('log-level', 'INFO')

# Maximum size of the cache in MiB: 1 GiB by default
_max_cache = BFLY_CONFIG.get('max-cache-size', 1024)
MAX_CACHE_SIZE = int(_max_cache) * (1024**2)
# Maximum size of a single block in MiB: 1 MiB by default
_max_block = BFLY_CONFIG.get('max-block-size', 1)
MAX_BLOCK_SIZE = int(_max_block) * (1024**2)

# Paths must start with one of the following allowed paths
ALLOWED_PATHS = BFLY_CONFIG.get('allowed-paths', [os.sep])

# Whether to restart server on changed source-code
DEV_MODE = BFLY_CONFIG.get('developer-mode', False)
