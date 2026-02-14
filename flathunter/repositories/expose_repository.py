"""Repository for expose persistence"""
import threading
import sqlite3 as lite
import json
from typing import Optional, List, Dict
from datetime import datetime
from flathunter.core.logging import logger

class SqliteExposeRepository:
    """SQLite implementation of repository pattern"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.threadlocal = threading.local()
        self._initialize_db()

    def _initialize_db(self):
        """Create tables if not exist"""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS processed (ID INTEGER)')
        cur.execute('CREATE TABLE IF NOT EXISTS exposes (id INTEGER, created TIMESTAMP, '
                   'crawler STRING, details BLOB, PRIMARY KEY (id, crawler))')
        cur.execute('CREATE TABLE IF NOT EXISTS executions (timestamp timestamp)')
        conn.commit()

    def _get_connection(self):
        """Get thread-local database connection"""
        connection = getattr(self.threadlocal, 'connection', None)
        if connection is None:
            self.threadlocal.connection = lite.connect(self.db_path)
            connection = self.threadlocal.connection
        return connection

    def is_processed(self, expose_id: int | str) -> bool:
        """Check if expose has been processed"""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM processed WHERE ID=?", (str(expose_id),))
        return cur.fetchone() is not None

    def mark_processed(self, expose_id: int | str) -> None:
        """Mark expose as processed"""
        if self.is_processed(expose_id):
            return
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO processed VALUES (?)", (str(expose_id),))
        conn.commit()

    def save_expose(self, expose: Dict) -> None:
        """Save expose to database"""
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT OR REPLACE INTO exposes (id, created, crawler, details) "
                "VALUES (?, ?, ?, ?)",
                (expose['id'], datetime.now(), expose.get('crawler', ''), json.dumps(expose))
            )
            conn.commit()
        except lite.Error as e:
            logger.error(f"Database error saving expose: {e}")

    def get_recent_exposes(self, count: int = 20) -> List[Dict]:
        """Get recently saved exposes"""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT details FROM exposes ORDER BY created DESC LIMIT ?",
            (count,)
        )
        rows = cur.fetchall()
        return [json.loads(row[0]) for row in rows]

    def record_execution(self) -> None:
        """Record an execution timestamp"""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO executions VALUES (?)", (datetime.now(),))
        conn.commit()

    def get_last_execution_time(self) -> Optional[datetime]:
        """Get the timestamp of the last execution"""
        conn = self._get_connection()
        cur = conn.cursor()
        cur.execute("SELECT MAX(timestamp) FROM executions")
        row = cur.fetchone()
        if row and row[0]:
            return datetime.fromisoformat(row[0])
        return None
