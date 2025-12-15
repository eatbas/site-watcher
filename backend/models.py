"""
Data models for PTT Site Watcher
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Announcement:
    """Represents a PTT announcement"""
    id: Optional[int]
    title: str
    date_text: str
    link: str
    content_hash: str
    first_seen: datetime
    last_seen: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "date_text": self.date_text,
            "link": self.link,
            "content_hash": self.content_hash,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


@dataclass
class Change:
    """Represents a detected change in announcements"""
    id: Optional[int]
    announcement_id: Optional[int]
    change_type: str  # 'new', 'modified', 'removed'
    detected_at: datetime
    title: str
    old_content: Optional[str]
    new_content: Optional[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "announcement_id": self.announcement_id,
            "change_type": self.change_type,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "title": self.title,
            "old_content": self.old_content,
            "new_content": self.new_content,
        }


@dataclass
class ScanStatus:
    """Represents the status of the scraper"""
    last_scan: Optional[datetime]
    is_scanning: bool
    announcement_count: int
    error: Optional[str]

    def to_dict(self) -> dict:
        return {
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "is_scanning": self.is_scanning,
            "announcement_count": self.announcement_count,
            "error": self.error,
        }
