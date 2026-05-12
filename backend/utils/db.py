import pymysql
import os

def get_connection():
    """Retorna conexão com o MySQL."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'smartfat_user'),
        password=os.getenv('DB_PASS', 'smartfat_pass'),
        database=os.getenv('DB_NAME', 'smartfat'),
        cursorclass=pymysql.cursors.DictCursor
    )