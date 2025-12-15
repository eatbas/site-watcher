"""
Script to simulate changes in the database for testing notifications.
"""
import os
import sys
import sqlite3
import hashlib
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from models import Announcement

def compute_hash(title: str, date_text: str, link: str) -> str:
    """Compute a hash for the announcement content"""
    content = f"{title}|{date_text}|{link}"
    return hashlib.md5(content.encode()).hexdigest()

def simulate_new_announcement(db: Database):
    """Simulate a new announcement by inserting one directly"""
    print("\n=== Simulating NEW Announcement ===")
    
    # We'll just delete one if it exists to make it "new" on next scan, 
    # OR we can manually insert a change record appearing as new.
    # Let's insert a fake announcement that looks like it was just found.
    
    title = f"Test Announcement {datetime.now().strftime('%H:%M:%S')}"
    date_text = datetime.now().strftime("%d %B %Y")
    link = f"/test-announcement-{int(datetime.now().timestamp())}"
    
    with db._get_connection() as conn:
        cursor = conn.cursor()
        
        # Insert into announcements
        content_hash = compute_hash(title, date_text, link)
        now = datetime.now()
        
        cursor.execute(
            """INSERT INTO announcements (title, date_text, link, content_hash, first_seen, last_seen)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (title, date_text, link, content_hash, now.isoformat(), now.isoformat())
        )
        announcement_id = cursor.lastrowid
        
        # Insert into changes
        cursor.execute(
            """INSERT INTO changes (announcement_id, change_type, detected_at, title, new_content)
               VALUES (?, 'new', ?, ?, ?)""",
            (announcement_id, now.isoformat(), title, f"{title}|{date_text}")
        )
        conn.commit()
    
    print(f"Inserted new announcement: {title}")
    print("Check the frontend for a 'New' notification.")

def simulate_modified_announcement(db: Database):
    """Simulate a modified announcement"""
    print("\n=== Simulating MODIFIED Announcement ===")
    
    # Get a random announcement
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM announcements ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            print("No announcements found to modify. Run a scan first.")
            return

        ann_id = row["id"]
        old_title = row["title"]
        old_date = row["date_text"]
        link = row["link"]
        
        new_title = f"{old_title} (UPDATED)"
        new_date = datetime.now().strftime("%d %B %Y")
        
        new_hash = compute_hash(new_title, new_date, link)
        now = datetime.now()
        
        # Update announcement
        cursor.execute(
            "UPDATE announcements SET title = ?, date_text = ?, content_hash = ? WHERE id = ?",
            (new_title, new_date, new_hash, ann_id)
        )
        
        # Insert change record
        cursor.execute(
            """INSERT INTO changes (announcement_id, change_type, detected_at, title, old_content, new_content)
               VALUES (?, 'modified', ?, ?, ?, ?)""",
            (ann_id, now.isoformat(), new_title, 
             f"{old_title}|{old_date}", f"{new_title}|{new_date}")
        )
        conn.commit()
        
    print(f"Modified announcement ID {ann_id}")
    print(f"Old: {old_title}")
    print(f"New: {new_title}")
    print("Check the frontend for a 'Modified' notification.")

def simulate_removed_announcement(db: Database):
    """Simulate a removed announcement"""
    print("\n=== Simulating REMOVED Announcement ===")
    
    with db._get_connection() as conn:
        cursor = conn.cursor()
        
        # First create a dummy one to remove, so we don't lose real data
        temp_title = "To Be Removed"
        temp_link = f"/remove-me-{int(datetime.now().timestamp())}"
        temp_hash = compute_hash(temp_title, "today", temp_link)
        
        # Insert it (silently, no change record yet)
        cursor.execute(
            """INSERT INTO announcements (title, date_text, link, content_hash, first_seen, last_seen)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (temp_title, "today", temp_link, temp_hash, datetime.now().isoformat(), datetime.now().isoformat())
        )
        ann_id = cursor.lastrowid
        conn.commit()
        
        print(f"Created temporary announcement: {temp_title}")
        
        # Now "remove" it by adding a removed change record
        # Note: In the real app, the announcement stays in DB but isn't in the scan results.
        # But for 'removed' notifications, we look at the changes table.
        
        now = datetime.now()
        cursor.execute(
            """INSERT INTO changes (announcement_id, change_type, detected_at, title, old_content)
               VALUES (?, 'removed', ?, ?, ?)""",
            (ann_id, now.isoformat(), temp_title, f"{temp_title}|today")
        )
        conn.commit()
        
    print(f"Removed announcement: {temp_title}")
    print("Check the frontend for a 'Removed' notification.")

def main():
    db_path = os.getenv("DATABASE_PATH", "ptt_watcher.db")
    db = Database(db_path)
    
    while True:
        print("\nOPTIONS:")
        print("1. Simulate NEW announcement")
        print("2. Simulate MODIFIED announcement")
        print("3. Simulate REMOVED announcement")
        print("4. Exit")
        
        choice = input("Enter choice (1-4): ")
        
        if choice == "1":
            simulate_new_announcement(db)
        elif choice == "2":
            simulate_modified_announcement(db)
        elif choice == "3":
            simulate_removed_announcement(db)
        elif choice == "4":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
