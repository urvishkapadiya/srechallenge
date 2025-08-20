import sqlite3
import psycopg

# Hide keys
from hashlib import sha256

# Encrypt values from keys
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode

from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class DumbKV:
    CREATE_QUERY = """
            CREATE TABLE IF NOT EXISTS kv (
                database_id INTEGER,
                key TEXT,
                value TEXT,
                CONSTRAINT unique_keys UNIQUE (database_id, key)
            )
    """
    SELECT_QUERY = "SELECT value FROM kv WHERE database_id = ? AND key = ?"
    INSERT_QUERY = "INSERT INTO kv (database_id, key, value) VALUES (?, ?, ?)"
    DELETE_QUERY = "DELETE FROM kv WHERE database_id = ? AND key = ?"

    def __init__(self, database_location: str):
        logger.info(f"Initializing DumbKV sqlite with database location: {database_location}")
        self._connect(database_location)
        logger.info("DumbKV initialized successfully")

    def create_table(self):
        cursor = self.conn.cursor()
        logger.info("Creating database table if not exists")
        cursor.execute(self.CREATE_QUERY)
        self.conn.commit()

    def get(self, database: int, key: str):
        cursor = self.conn.cursor()
        encrypted_key = self._generate_key(key)
        logger.info(f"Retrieving value for database {database}, key {encrypted_key}")
        cursor.execute(self.SELECT_QUERY, (database, encrypted_key))
        result = cursor.fetchone()
        decrypted_value = self._decrypt_value(result[0], encrypted_key)
        return decrypted_value
        
    def set(self, database: int, key: str, value: str):
        cursor = self.conn.cursor()
        encrypted_key = self._generate_key(key)
        encrypted_value = self._encrypt_value(value, encrypted_key)
        logger.info(f"Storing value for database {database}, key {encrypted_key}")
        cursor.execute(self.INSERT_QUERY, (database, encrypted_key, encrypted_value))
        self.conn.commit()

    def delete(self, database: int, key: str):
        cursor = self.conn.cursor()
        encrypted_key = self._generate_key(key)
        logger.info(f"Deleting value for database {database}, key {encrypted_key}")
        cursor.execute(self.DELETE_QUERY, (database, encrypted_key))
        self.conn.commit()

    def _connect(self, database_location: str):
        self.conn = sqlite3.connect(database_location)
    
    def _generate_key(self, key: str) -> str:
        # Generate a SHA-256 hash of the key
        key_hash = sha256(key.encode()).hexdigest()
        # Trim hash to 32 bytes (Fernet only supports 32 byte keys)
        key_hash = key_hash[:32]
        # Encode the hash using URL-safe base64
        return urlsafe_b64encode(key_hash.encode()).decode("utf-8")
    
    def _encrypt_value(self, value: str, secret_key: str) -> str:
        fernet = Fernet(secret_key)
        encrypted = fernet.encrypt(value.encode())
        return encrypted.decode()

    def _decrypt_value(self, encrypted_value: str, secret_key: str) -> str:
        fernet = Fernet(secret_key)
        decrypted = fernet.decrypt(encrypted_value.encode())
        return decrypted.decode()

class PostgresDumbKV(DumbKV):
    CREATE_QUERY = """
            CREATE TABLE IF NOT EXISTS kv (
                database_id INTEGER,
                key TEXT,
                value TEXT,
                UNIQUE (database_id, key)
            )
    """
    SELECT_QUERY = "SELECT value FROM kv WHERE database_id = %s AND key = %s"
    INSERT_QUERY = "INSERT INTO kv (database_id, key, value) VALUES (%s, %s, %s)"
    DELETE_QUERY = "DELETE FROM kv WHERE database_id = %s AND key = %s"

    def _connect(self, database_location: str):
        self.conn = psycopg.connect(database_location)