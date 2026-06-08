import pymysql
import os
import time


def fix_mojibake(value):
    if isinstance(value, str) and ('Ã' in value or 'Â' in value):
        try:
            return value.encode('latin1').decode('utf-8')
        except UnicodeError:
            return value
    if isinstance(value, dict):
        return {key: fix_mojibake(item) for key, item in value.items()}
    if isinstance(value, list):
        return [fix_mojibake(item) for item in value]
    return value


class Utf8DictCursor(pymysql.cursors.DictCursor):
    def fetchone(self):
        return fix_mojibake(super().fetchone())

    def fetchall(self):
        return fix_mojibake(super().fetchall())


def get_connection():
    """Retorna conexão com o MySQL."""
    last_error = None
    for attempt in range(5):
        try:
            return pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', 3306)),
                user=os.getenv('DB_USER', 'smartfat_user'),
                password=os.getenv('DB_PASS', 'smartfat_pass'),
                database=os.getenv('DB_NAME', 'smartfat'),
                charset='utf8mb4',
                use_unicode=True,
                init_command="SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci",
                cursorclass=Utf8DictCursor
            )
        except pymysql.err.OperationalError as error:
            last_error = error
            if attempt == 4:
                break
            time.sleep(1)
    raise last_error
