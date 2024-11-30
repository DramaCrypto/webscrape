############################ DB SETTINGS #####################################

# local DB
USER = 'root'
PASS = 'mysql123'
HOST = 'localhost'
PORT = '3306'
DATABASE = 'development'
# production db

USER = 'scraper'
PASS = 'Scraper2020$'
HOST = '142.44.136.176'
PORT = '3306'
DATABASE = 'ygolegacy'


DATABASE_URI = f'mysql+pymysql://{USER}:{PASS}@{HOST}:{PORT}/{DATABASE}'

############################ WEBSITE SETTINGS #####################################

WEBSITE_PASSWORD = '123'

################## SERVICES SETTINGS #####################
PICKLE_PATH = "D:\\Dev\\Projects\\WorkProjects\\Ygolegacy_projects\\count_and_value_updater\\data"
EBAY_API_CONFIG = 'D:\\Dev\\Projects\\WorkProjects\\ygolegacy\\ygolegacy\\ebay.yaml'
EBAY_IMAGES = "D:\\Dev\\Projects\\WorkProjects\\ygolegacy\\ygolegacy\\static\\ebay_image"
# PICKLE_PATH = "/root/scripts/count_and_value_updater/data"
# EBAY_API_CONFIG = '/apps/app_repo/ygolegacy/ygolegacy/ebay.yaml'
# EBAY_IMAGES = "/apps/app_repo/ygolegacy/ygolegacy/static/ebay_image"

################## EBAY SETTINGS #####################
EBAY_USER = 'ygolegacy'
EBAY_PWD = '1MadProfit1$'

