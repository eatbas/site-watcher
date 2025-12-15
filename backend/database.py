"""
SQLite database operations for PTT Site Watcher
"""
import sqlite3
import hashlib
from datetime import datetime
from typing import List, Optional
from contextlib import contextmanager

from models import Announcement, Change


class Database:
    def __init__(self, db_path: str = "ptt_watcher.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize the database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Announcements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date_text TEXT NOT NULL,
                    link TEXT NOT NULL UNIQUE,
                    content_hash TEXT NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Changes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    announcement_id INTEGER,
                    change_type TEXT NOT NULL,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    title TEXT NOT NULL,
                    old_content TEXT,
                    new_content TEXT,
                    FOREIGN KEY (announcement_id) REFERENCES announcements(id)
                )
            """)
            
            # Scan status table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_status (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    last_scan TIMESTAMP,
                    is_scanning INTEGER DEFAULT 0,
                    error TEXT
                )
            """)
            
            # Initialize scan status if not exists
            cursor.execute("""
                INSERT OR IGNORE INTO scan_status (id, last_scan, is_scanning) 
                VALUES (1, NULL, 0)
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    refresh_interval INTEGER DEFAULT 600,
                    email_enabled INTEGER DEFAULT 0,
                    email_sender TEXT DEFAULT '',
                    email_recipients TEXT DEFAULT '[]',
                    smtp_server TEXT DEFAULT 'smtp.office365.com',
                    smtp_port INTEGER DEFAULT 587,
                    smtp_username TEXT DEFAULT '',
                    smtp_password TEXT DEFAULT ''
                )
            """)
            
            # Initialize settings if not exists
            cursor.execute("""
                INSERT OR IGNORE INTO settings (id, refresh_interval, email_enabled, email_sender, email_recipients)
                VALUES (1, 600, 0, '', '[]')
            """)
            
            conn.commit()

    @staticmethod
    def compute_hash(title: str, date_text: str, link: str) -> str:
        """Compute a hash for the announcement content"""
        content = f"{title}|{date_text}|{link}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_all_announcements(self) -> List[Announcement]:
        """Get all announcements"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM announcements ORDER BY last_seen DESC")
            rows = cursor.fetchall()
            return [
                Announcement(
                    id=row["id"],
                    title=row["title"],
                    date_text=row["date_text"],
                    link=row["link"],
                    content_hash=row["content_hash"],
                    first_seen=datetime.fromisoformat(row["first_seen"]) if row["first_seen"] else None,
                    last_seen=datetime.fromisoformat(row["last_seen"]) if row["last_seen"] else None,
                )
                for row in rows
            ]

    def get_announcement_by_link(self, link: str) -> Optional[Announcement]:
        """Get an announcement by its link"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM announcements WHERE link = ?", (link,))
            row = cursor.fetchone()
            if row:
                return Announcement(
                    id=row["id"],
                    title=row["title"],
                    date_text=row["date_text"],
                    link=row["link"],
                    content_hash=row["content_hash"],
                    first_seen=datetime.fromisoformat(row["first_seen"]) if row["first_seen"] else None,
                    last_seen=datetime.fromisoformat(row["last_seen"]) if row["last_seen"] else None,
                )
            return None

    def upsert_announcement(self, title: str, date_text: str, link: str) -> tuple[Announcement, Optional[Change]]:
        """Insert or update an announcement, returns the announcement and any change detected"""
        content_hash = self.compute_hash(title, date_text, link)
        now = datetime.now()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if announcement exists
            existing = self.get_announcement_by_link(link)
            
            if existing:
                # Update last_seen
                cursor.execute(
                    "UPDATE announcements SET last_seen = ? WHERE id = ?",
                    (now.isoformat(), existing.id)
                )
                
                # Check if content changed
                change = None
                if existing.content_hash != content_hash:
                    cursor.execute(
                        "UPDATE announcements SET title = ?, date_text = ?, content_hash = ? WHERE id = ?",
                        (title, date_text, content_hash, existing.id)
                    )
                    
                    # Record change
                    cursor.execute(
                        """INSERT INTO changes (announcement_id, change_type, detected_at, title, old_content, new_content)
                           VALUES (?, 'modified', ?, ?, ?, ?)""",
                        (existing.id, now.isoformat(), title, 
                         f"{existing.title}|{existing.date_text}", f"{title}|{date_text}")
                    )
                    change = Change(
                        id=cursor.lastrowid,
                        announcement_id=existing.id,
                        change_type="modified",
                        detected_at=now,
                        title=title,
                        old_content=f"{existing.title}|{existing.date_text}",
                        new_content=f"{title}|{date_text}",
                    )
                
                conn.commit()
                existing.last_seen = now
                return existing, change
            else:
                # Insert new announcement
                cursor.execute(
                    """INSERT INTO announcements (title, date_text, link, content_hash, first_seen, last_seen)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (title, date_text, link, content_hash, now.isoformat(), now.isoformat())
                )
                announcement_id = cursor.lastrowid
                
                # Record new announcement change
                cursor.execute(
                    """INSERT INTO changes (announcement_id, change_type, detected_at, title, new_content)
                       VALUES (?, 'new', ?, ?, ?)""",
                    (announcement_id, now.isoformat(), title, f"{title}|{date_text}")
                )
                
                conn.commit()
                
                announcement = Announcement(
                    id=announcement_id,
                    title=title,
                    date_text=date_text,
                    link=link,
                    content_hash=content_hash,
                    first_seen=now,
                    last_seen=now,
                )
                change = Change(
                    id=cursor.lastrowid,
                    announcement_id=announcement_id,
                    change_type="new",
                    detected_at=now,
                    title=title,
                    old_content=None,
                    new_content=f"{title}|{date_text}",
                )
                return announcement, change

    def mark_removed_announcements(self, current_links: List[str]) -> List[Change]:
        """Mark announcements as removed if they're no longer on the page"""
        changes = []
        now = datetime.now()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all announcements that are not in current_links
            placeholders = ",".join(["?" for _ in current_links]) if current_links else "''"
            query = f"""
                SELECT * FROM announcements 
                WHERE link NOT IN ({placeholders})
                AND id NOT IN (
                    SELECT announcement_id FROM changes 
                    WHERE change_type = 'removed' AND announcement_id IS NOT NULL
                )
            """
            cursor.execute(query, current_links if current_links else [])
            removed = cursor.fetchall()
            
            for row in removed:
                cursor.execute(
                    """INSERT INTO changes (announcement_id, change_type, detected_at, title, old_content)
                       VALUES (?, 'removed', ?, ?, ?)""",
                    (row["id"], now.isoformat(), row["title"], f"{row['title']}|{row['date_text']}")
                )
                changes.append(Change(
                    id=cursor.lastrowid,
                    announcement_id=row["id"],
                    change_type="removed",
                    detected_at=now,
                    title=row["title"],
                    old_content=f"{row['title']}|{row['date_text']}",
                    new_content=None,
                ))
            
            conn.commit()
        
        return changes

    def get_all_changes(self, limit: int = 50) -> List[Change]:
        """Get all changes, most recent first"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM changes ORDER BY detected_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                Change(
                    id=row["id"],
                    announcement_id=row["announcement_id"],
                    change_type=row["change_type"],
                    detected_at=datetime.fromisoformat(row["detected_at"]) if row["detected_at"] else None,
                    title=row["title"],
                    old_content=row["old_content"],
                    new_content=row["new_content"],
                )
                for row in rows
            ]

    def get_scan_status(self) -> dict:
        """Get the current scan status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scan_status WHERE id = 1")
            row = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) as count FROM announcements")
            count_row = cursor.fetchone()
            
            return {
                "last_scan": row["last_scan"],
                "is_scanning": bool(row["is_scanning"]),
                "announcement_count": count_row["count"],
                "error": row["error"],
            }

    def set_scanning(self, is_scanning: bool, error: str = None):
        """Set the scanning status"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if is_scanning:
                cursor.execute(
                    "UPDATE scan_status SET is_scanning = 1, error = NULL WHERE id = 1"
                )
            else:
                cursor.execute(
                    "UPDATE scan_status SET is_scanning = 0, last_scan = ?, error = ? WHERE id = 1",
                    (datetime.now().isoformat(), error)
                )
            conn.commit()

    def get_settings(self) -> dict:
        """Get the current settings"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings WHERE id = 1")
            row = cursor.fetchone()
            
            if row:
                import json
                recipients = json.loads(row["email_recipients"]) if row["email_recipients"] else []
                return {
                    "refresh_interval": row["refresh_interval"],
                    "email_enabled": bool(row["email_enabled"]),
                    "email_sender": row["email_sender"],
                    "email_recipients": recipients,
                    "smtp_server": row["smtp_server"],
                    "smtp_port": row["smtp_port"],
                    "smtp_username": row["smtp_username"],
                    "smtp_password": row["smtp_password"],
                }
            return {
                "refresh_interval": 600,
                "email_enabled": False,
                "email_sender": "",
                "email_recipients": [],
                "smtp_server": "smtp.office365.com",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
            }

    def update_settings(self, settings: dict):
        """Update the settings"""
        import json
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE settings SET 
                    refresh_interval = ?,
                    email_enabled = ?,
                    email_sender = ?,
                    email_recipients = ?,
                    smtp_server = ?,
                    smtp_port = ?,
                    smtp_username = ?,
                    smtp_password = ?
                WHERE id = 1
            """, (
                settings.get("refresh_interval", 600),
                1 if settings.get("email_enabled", False) else 0,
                settings.get("email_sender", ""),
                json.dumps(settings.get("email_recipients", [])),
                settings.get("smtp_server", "smtp.office365.com"),
                settings.get("smtp_port", 587),
                settings.get("smtp_username", ""),
                settings.get("smtp_password", ""),
            ))
            conn.commit()
